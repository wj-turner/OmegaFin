from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from twisted.internet.ssl import CertificateOptions
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.defer import DeferredList

from twisted.enterprise import adbapi
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python.log import startLogging

import psycopg2
import json
import datetime
import calendar
import redis
import sys
import os
dbpool = adbapi.ConnectionPool(
    "psycopg2",
    user=os.getenv("POSTGRES_MAIN_DB_name"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="postgres",
    database=os.getenv("POSTGRES_CONFIG_DB_name")
)
# credentials = {
#     "ClientId": os.getenv("Ctrader_RESTAPI_ClientId"),
#     "Secret": os.getenv("Ctrader_RESTAPI_Secret"),
#     "HostType": os.getenv("Ctrader_RESTAPI_HostType"),
#     "AccessToken": os.getenv("Ctrader_RESTAPI_AccessToken"),
#     "AccountId": int(os.getenv("Ctrader_RESTAPI_AccountId")),
# }

credentialsFile = open("src/credentials.json")
credentials = json.load(credentialsFile)
original_send = Client.send

def send_with_logging(self, request):
    print(f"Request sent: {request}")
    deferred = original_send(self, request)
    if deferred is None:
        print("Warning: 'send' method returned None")
    return deferred
    
Client.send = send_with_logging
host = EndPoints.PROTOBUF_LIVE_HOST if credentials["HostType"].lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
symbolName = "USDX"
dailyBars = []
startLogging(sys.stdout)


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
    print("\nTrendbars received")
    # print(result)
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
    print("\here")
    deferred.addCallbacks(accountAuthResponseCallback, onError)

def onError(client, failure=None): # Call back for errors
    if failure is not None:
        print("\nMessage Error: ", failure)
    else:
        print("\nAn error occurred, but no failure information is available.")


def disconnected(client, reason): # Callback for client disconnection
    print("\nDisconnected: ", reason)
    pass

def onMessageReceived(client, message): # Callback for receiving all messages
    if message.payloadType in [ProtoHeartbeatEvent().payloadType, ProtoOAAccountAuthRes().payloadType, ProtoOAApplicationAuthRes().payloadType, ProtoOASymbolsListRes().payloadType, ProtoOAGetTrendbarsRes().payloadType]:
        return
    # print("\nMessage received: \n", Protobuf.extract(message))

def connected(client): # Callback for client connection
    print("\nConnected")
    request = ProtoOAApplicationAuthReq()
    
    request.clientId = credentials["ClientId"]
    request.clientSecret = credentials["Secret"]
    deferred = client.send(request)
    # print("\nhere: ",deferred)
    # deferred.addErrback(onError)
    deferred.addCallbacks(applicationAuthResponseCallback, onError)
@inlineCallbacks
def fetch_and_process(result):
    print(result)
    # Fetch data from the database
    rows = yield dbpool.runQuery("SELECT id, symbol, start_date, end_date, timeframe FROM time_data_gap WHERE status = 'pending'")

    for row in rows:
        row_id, symbolName, fromTimestamp, toTimestamp, period = row

        # Process each row
        if(symbolName == 'symbol_initiation'):
            symbols = Protobuf.extract(result)
            # print(symbols)
            yield insert_symbols(dbpool,symbols)
        else:
            symbolFilterResult = yield process_row(symbolName, fromTimestamp, toTimestamp, period)

        # Update the status of the row in the database after processing
        yield dbpool.runOperation("UPDATE time_data_gap SET status = 'processed' WHERE id = %s", [row_id])
        

    # Close the database connection after processing all rows
    dbpool.close()

    # Stop the reactor if it's running
    if reactor.running:
        reactor.stop()


def insert_symbols(dbpool, proto_symbols_res):

    deferreds = []
    insert_query = """
    INSERT INTO symbols ("symbolId", "symbolName", "source", "initUntil", "enabled", "baseAssetId", "quoteAssetId", "symbolCategoryId", "description")
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
    symbols = proto_symbols_res.symbol
    def on_success(_):
        log.msg("Insert operation successful.")

    def on_error(e):
        log.err(f"Insert operation failed: {e}")
    for symbol in symbols:
        
        try:
            # print('hiiiiiiiiiii')
            d = dbpool.runOperation(insert_query, (
                symbol.symbolId,
                symbol.symbolName,
                'pepperstone',
                '0',
                '0',
                symbol.baseAssetId,
                symbol.quoteAssetId,
                symbol.symbolCategoryId,
                symbol.description
            ))
            deferreds.append(d)
            # d.addCallbacks(on_success, on_error)
            log.msg(f"Inserted symbol {symbol.symbolName} successfully")
        except Exception as e:
            # Log or handle the error
            log.err(f"Failed to insert symbol {symbol.symbolName}: {str(e)}")
    return DeferredList(deferreds)


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