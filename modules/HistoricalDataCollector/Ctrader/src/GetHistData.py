from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from twisted.internet.ssl import CertificateOptions
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
import json
import datetime
import calendar
credentialsFile = open("src/credentials.json")
credentials = json.load(credentialsFile)
host = EndPoints.PROTOBUF_LIVE_HOST if credentials["HostType"].lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

_symbolName = "USDX"
_fromTimestamp = ''
_toTimestamp = ''
_period = ''
dailyBars = []



def transformTrendbar(trendbar):
    openTime = datetime.datetime.fromtimestamp(trendbar.utcTimestampInMinutes * 60, datetime.timezone.utc)
    openPrice = (trendbar.low + trendbar.deltaOpen) / 100000.0
    highPrice = (trendbar.low + trendbar.deltaHigh) / 100000.0
    lowPrice = trendbar.low / 100000.0
    closePrice = (trendbar.low + trendbar.deltaClose) / 100000.0
    return [openTime, openPrice, highPrice, lowPrice, closePrice, trendbar.volume]
def trendbarsResponseCallback(result):
    print("\nTrendbars received")
    trendbars = Protobuf.extract(result)
    barsData = list(map(transformTrendbar, trendbars.trendbar))
    global dailyBars
    dailyBars.clear()
    dailyBars.extend(barsData)

    for bar in dailyBars:
        print(bar)  # Print each bar's data

    print("\ndailyBars length:", len(dailyBars))
    print("\Stopping reactor...")
    reactor.stop()
    
def symbolsResponseCallback(result):
    print("\nSymbols received")
    symbols = Protobuf.extract(result)
    global symbolName, _fromTimestamp, _toTimestamp, _period
    symbolsFilterResult = list(filter(lambda symbol: symbol.symbolName == _symbolName, symbols.symbol))
    if len(symbolsFilterResult) == 0:
        raise Exception(f"There is symbol that matches to your defined symbol name: {_symbolName}")
    elif len(symbolsFilterResult) > 1:
        raise Exception(f"More than one symbol matched with your defined symbol name: {_symbolName}, match result: {symbolsFilterResult}")
    symbol = symbolsFilterResult[0]
    request = ProtoOAGetTrendbarsReq()
    request.symbolId = symbol.symbolId
    request.ctidTraderAccountId = credentials["AccountId"]
    # request.period = ProtoOATrendbarPeriod.MN1
    request.period = _period
    # We set the from/to time stamps to 50 weeks, you can load more data by sending multiple requests
    # Please check the ProtoOAGetTrendbarsReq documentation for more detail
    # request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1300)).utctimetuple())) * 1000
    request.fromTimestamp = int(calendar.timegm(_fromTimestamp.utctimetuple())) * 1000
    #request.fromTimestamp = 158113000000
    #request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
    request.toTimestamp = int(calendar.timegm(_toTimestamp.utctimetuple())) * 1000
    # request.toTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=1250)).utctimetuple())) * 1000
    deferred = client.send(request)
    deferred.addCallbacks(trendbarsResponseCallback, onError)
    
def accountAuthResponseCallback(result):
    print("\nAccount authenticated")
    request = ProtoOASymbolsListReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.includeArchivedSymbols = False
    deferred = client.send(request)
    deferred.addCallbacks(symbolsResponseCallback, onError)
    
def applicationAuthResponseCallback(result):
    print("\nApplication authenticated")
    request = ProtoOAAccountAuthReq()
    request.ctidTraderAccountId = credentials["AccountId"]
    request.accessToken = credentials["AccessToken"]
    deferred = client.send(request)
    deferred.addCallbacks(accountAuthResponseCallback, onError)

def onError(client, failure): # Call back for errors
    print("\nMessage Error: ", failure)

def disconnected(client, reason): # Callback for client disconnection
    print("\nDisconnected: ", reason)

def onMessageReceived(client, message): # Callback for receiving all messages
    if message.payloadType in [ProtoHeartbeatEvent().payloadType, ProtoOAAccountAuthRes().payloadType, ProtoOAApplicationAuthRes().payloadType, ProtoOASymbolsListRes().payloadType, ProtoOAGetTrendbarsRes().payloadType]:
        return
    print("\nMessage received: \n", Protobuf.extract(message))
    
def connected(client): # Callback for client connection
    print("\nConnected")
    request = ProtoOAApplicationAuthReq()
    request.clientId = credentials["ClientId"]
    request.clientSecret = credentials["Secret"]
    deferred = client.send(request)
    deferred.addCallbacks(applicationAuthResponseCallback, onError)

def fetch_data(symbol, start_date, end_date, timeframe):
    global symbolName, _fromTimestamp, _toTimestamp, _period
    symbolName = symbol
    # Modify the request with provided parameters
    _fromTimestamp = start_date
    _toTimestamp = end_date
    _period = timeframe

    client.startService()
    reactor.run()
# Setting optional client callbacks
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)
# Starting the client service
# client.startService()
# # Run Twisted reactor, we imported it earlier
# reactor.run()