from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from twisted.internet.ssl import CertificateOptions
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor

from twisted.enterprise import adbapi
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


import psycopg2
import json
import datetime
import calendar
import redis

dbpool = adbapi.ConnectionPool(
    "psycopg2",
    database="forexdb",
    user="forexuser",
    password="forexpassword",
    host="postgres"
)

credentialsFile = open("src/credentials.json")
credentials = json.load(credentialsFile)
host = EndPoints.PROTOBUF_LIVE_HOST if credentials["HostType"].lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
symbolName = "USDX"
dailyBars = []
def transformTrendbar(trendbar, symbolId, period):
    #openTime = datetime.datetime.fromtimestamp(trendbar.utcTimestampInMinutes * 60, datetime.timezone.utc)
    openTime = datetime.datetime.fromtimestamp(trendbar.utcTimestampInMinutes * 60, datetime.timezone.utc).isoformat()
    openPrice = (trendbar.low + trendbar.deltaOpen) / 100000.0
    highPrice = (trendbar.low + trendbar.deltaHigh) / 100000.0
    lowPrice = trendbar.low / 100000.0
    closePrice = (trendbar.low + trendbar.deltaClose) / 100000.0
    # return [openTime, openPrice, highPrice, lowPrice, closePrice, trendbar.volume]
    return {
        'openTime': openTime,
        'openPrice': openPrice,
        'highPrice': highPrice,
        'lowPrice': lowPrice,
        'closePrice': closePrice,
        'volume': trendbar.volume,
        'symbolId': symbolId,
        'period': period
    }
def trendbarsResponseCallback(result, symbolId, period):
    # print("\nTrendbars received")
    redis_queue = redis.Redis(host='redis-queue', port=6379, db=0)
    trendbars = Protobuf.extract(result)
    barsData = list(map(lambda trendbar: transformTrendbar(trendbar, symbolId, period), trendbars.trendbar))
    global dailyBars
    dailyBars.clear()
    dailyBars.extend(barsData)
    stream_key = "HistoricalStream"
    # print("//////////////////////")
    for bar in dailyBars:
        # print(bar)
        # redis_client.xadd(stream_key, {'data': json.dumps(bar)})
        # redis_queue.rpush(stream_key, {'data': json.dumps(bar)})
        bar_json = json.dumps(bar)
        redis_queue.rpush(stream_key, bar_json)
          # Print each bar's data
    # print("//////////////////////")

    # print("\ndailyBars length:", len(dailyBars))
    # print("\Stopping reactor...")
    # reactor.stop()

def symbolsResponseCallback(result):
    # print("\nSymbols received")
    fromTimestamp =  int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1300)).utctimetuple())) * 1000
    toTimestamp =  int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1250)).utctimetuple())) * 1000
    period =  ProtoOATrendbarPeriod.MN1
    symbolName = "USDX"

    # print(fromTimestamp)
    # print(toTimestamp)
    # print(period)
    # print(symbolName)
    
    symbols = Protobuf.extract(result)
    # print(symbols);
    symbolsFilterResult = list(filter(lambda symbol: symbol.symbolName == symbolName, symbols.symbol))
    if len(symbolsFilterResult) == 0:
        raise Exception(f"There is symbol that matches to your defined symbol name: {symbolName}")
    elif len(symbolsFilterResult) > 1:
        raise Exception(f"More than one symbol matched with your defined symbol name: {symbolName}, match result: {symbolsFilterResult}")
    symbol = symbolsFilterResult[0]
    request = ProtoOAGetTrendbarsReq()
    request.symbolId = symbol.symbolId
    request.ctidTraderAccountId = credentials["AccountId"]
    


    
    # We set the from/to time stamps to 50 weeks, you can load more data by sending multiple requests
    # Please check the ProtoOAGetTrendbarsReq documentation for more detail
    request.fromTimestamp = fromTimestamp
    request.period = period
    #request.fromTimestamp = 158113000000
    #request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
    request.toTimestamp = toTimestamp
    deferred = client.send(request)
    deferred.addCallbacks(trendbarsResponseCallback, onError)

def accountAuthResponseCallback(result):
    print("\nAccount authenticated")
    request = ProtoOASymbolsListReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.includeArchivedSymbols = False
    deferred = client.send(request)
    deferred.addCallbacks(fetch_and_process, onError)

def applicationAuthResponseCallback(result):
    print("\nApplication authenticated")
    request = ProtoOAAccountAuthReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.accessToken = credentials["AccessToken"]
    deferred = client.send(request)
    deferred.addCallbacks(accountAuthResponseCallback, onError)

def onError(client, failure): # Call back for errors
    print("\nMessage Error: ", failure)
    pass

def disconnected(client, reason): # Callback for client disconnection
    print("\nDisconnected: ", reason)
    pass

def onMessageReceived(client, message): # Callback for receiving all messages
    if message.payloadType in [ProtoHeartbeatEvent().payloadType, ProtoOAAccountAuthRes().payloadType, ProtoOAApplicationAuthRes().payloadType, ProtoOASymbolsListRes().payloadType, ProtoOAGetTrendbarsRes().payloadType]:
        return
    # print("\nMessage received: \n", Protobuf.extract(message))

def connected(client): # Callback for client connection
    # print("\nConnected")
    request = ProtoOAApplicationAuthReq()
    request.clientId = credentials["ClientId"]
    request.clientSecret = credentials["Secret"]
    deferred = client.send(request)
    deferred.addCallbacks(applicationAuthResponseCallback, onError)
@inlineCallbacks
def fetch_and_process(result):

    # Fetch data from the database
    rows = yield dbpool.runQuery("SELECT id, symbol, start_date, end_date, timeframe FROM time_data_gap WHERE status = 'pending'")

    for row in rows:
        row_id, symbolName, fromTimestamp, toTimestamp, period = row

        # Process each row
        symbolFilterResult = yield process_row(symbolName, fromTimestamp, toTimestamp, period)

        # Update the status of the row in the database after processing
        yield dbpool.runOperation("UPDATE time_data_gap SET status = 'processed' WHERE id = %s", [row_id])

    # Close the database connection after processing all rows
    dbpool.close()

    # Stop the reactor if it's running
    if reactor.running:
        reactor.stop()


@inlineCallbacks
def process_row(symbolName, fromTimestamp, toTimestamp, period):
    # Your existing logic to process this data
    request = ProtoOAGetTrendbarsReq()
    request.symbolId = int(symbolName)
    request.ctidTraderAccountId = credentials["AccountId"]
    request.fromTimestamp = int(fromTimestamp)
    request.period = int(period)
    request.toTimestamp = int(toTimestamp)

    deferred = client.send(request)
    yield deferred.addCallbacks(lambda result: trendbarsResponseCallback(result, symbolName, period), onError)


    # yield deferred.addCallbacks(trendbarsResponseCallback, onError)

# Start the processing
# fetch_and_process()

# Setting optional client callbacks
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)
# Starting the client service
client.startService()
# Run Twisted reactor, we imported it earlier
reactor.run()