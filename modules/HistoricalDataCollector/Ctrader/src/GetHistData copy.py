from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from twisted.internet.ssl import CertificateOptions
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
from flask import Flask, jsonify
from flask import request as flask_request

import json
import datetime
import calendar
# import argparse
import redis


# Create the parser
# parser = argparse.ArgumentParser(description='Fetch historical forex data.')

# # Add arguments
# parser.add_argument('--fromTimestamp', type=int, help='Start timestamp for fetching data')
# parser.add_argument('--toTimestamp', type=int, help='End timestamp for fetching data')
# parser.add_argument('--period', help='Time period for the data')
# parser.add_argument('--symbolName', help='Name of the symbol for which to fetch data')

# # Parse the arguments
# args = parser.parse_args()
app = Flask(__name__)
app.debug = True

credentialsFile = open("src/credentials.json")
credentials = json.load(credentialsFile)
host = EndPoints.PROTOBUF_LIVE_HOST if credentials["HostType"].lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
symbolName = "USDX"
dailyBars = []
def transformTrendbar(trendbar):
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
        'volume': trendbar.volume
    }
def trendbarsResponseCallback(result):
    print("\nTrendbars received")
    redis_queue = redis.Redis(host='redis-queue', port=6379, db=0)
    trendbars = Protobuf.extract(result)
    barsData = list(map(transformTrendbar, trendbars.trendbar))
    global dailyBars
    dailyBars.clear()
    dailyBars.extend(barsData)
    stream_key = "HistoricalStream"
    # print("//////////////////////")
    for bar in dailyBars:
        print(bar)
        # redis_client.xadd(stream_key, {'data': json.dumps(bar)})
        # redis_queue.rpush(stream_key, {'data': json.dumps(bar)})
        bar_json = json.dumps(bar)
        redis_queue.rpush(stream_key, bar_json)
          # Print each bar's data
    # print("//////////////////////")

    # print("\ndailyBars length:", len(dailyBars))
    # print("\Stopping reactor...")
    reactor.stop()

def symbolsResponseCallback(result):
    # print("\nSymbols received")
    fromTimestamp = int(args.fromTimestamp) if args.fromTimestamp else int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1300)).utctimetuple())) * 1000
    toTimestamp = int(args.toTimestamp) if args.toTimestamp else int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1250)).utctimetuple())) * 1000
    period = int(args.period) if args.period else ProtoOATrendbarPeriod.MN1
    symbolName = args.symbolName if args.symbolName else "USDX"

    
    
    symbols = Protobuf.extract(result)
    symbolsFilterResult = list(filter(lambda symbol: symbol.symbolName == symbolName, symbols.symbol))
    if len(symbolsFilterResult) == 0:
        raise Exception(f"There is symbol that matches to your defined symbol name: {symbolName}")
    elif len(symbolsFilterResult) > 1:
        raise Exception(f"More than one symbol matched with your defined symbol name: {symbolName}, match result: {symbolsFilterResult}")
    symbol = symbolsFilterResult[0]
    request = ProtoOAGetTrendbarsReq()
    request.symbolId = symbol.symbolId
    print(symbol.symbolId)
    # print(toTimestamp)
    # print(period)
    # print(symbolName)
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
    # print("\nAccount authenticated")
    request = ProtoOASymbolsListReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.includeArchivedSymbols = False
    deferred = client.send(request)
    # deferred.addCallbacks(symbolsResponseCallback, onError)

def applicationAuthResponseCallback(result):
    print("\nApplication authenticated")
    request = ProtoOAAccountAuthReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.accessToken = credentials["AccessToken"]
    deferred = client.send(request)
    deferred.addCallbacks(accountAuthResponseCallback, onError)

def onError(client, failure): # Call back for errors
    # print("\nMessage Error: ", failure)
    pass

def disconnected(client, reason): # Callback for client disconnection
    # print("\nDisconnected: ", reason)
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

@app.route('/fetch-historical-data', methods=['POST'])
def fetch_historical_data():
    data = flask_request.json
    fromTimestamp = data.get('fromTimestamp')
    toTimestamp = data.get('toTimestamp')
    period = data.get('period')
    symbolName = data.get('symbolName')

    # Set up and trigger the data fetching process here
    # Replace args usage with variables from data

    # For example:
    request = ProtoOAGetTrendbarsReq()
    request.symbolId = 1 # Implement get_symbol_id function
    request.ctidTraderAccountId = credentials["AccountId"]
    request.fromTimestamp = int(fromTimestamp)
    request.toTimestamp = int(toTimestamp)
    request.period = int(period)

    # Send the request and set up callbacks
    deferred = client.send(request)
    deferred.addCallbacks(trendbarsResponseCallback, onError)

    return jsonify({"status": "Data fetching started"}), 202
# Setting optional client callbacks
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)
# Starting the client service
client.startService()
# Run Twisted reactor, we imported it earlier
reactor.run()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5100)