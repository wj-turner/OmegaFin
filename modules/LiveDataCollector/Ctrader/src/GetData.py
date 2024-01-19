from twisted.internet import reactor
import json
from ctrader_fix import *
import datetime
import redis
import simplefix
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


with open("/usr/src/app/src/config-quote.json") as configFile:
    config = json.load(configFile)
client = Client(config["Host"], config["Port"], ssl = config["SSL"])

# to do make this dynamic
static_symbol_ids = {
    "1": "EURUSD",
    "2": "GBPUSD",
    "3": "EURJPY",
    "41": "XAUUSD",
    "101": "USDX",
    "128": "BTCUSD",
    "333": "Apple_Inc_(AAPL.O)"
}

logging.info("This is an info message")

def send(request):
    diferred = client.send(request)
    #diferred.addCallback(lambda _: print("\nSent: ", request.getMessage(client.getMessageSequenceNumber())))
def onMessageReceived(client, responseMessage): # Callback for receiving all messages
#     print("\nReceived: ", responseMessage.getMessage())
    
#     if parsed_message:
#     # Iterate over the parsed message
#         for tag, value in parsed_message.pairs():
#             print(f"Tag: {tag}, Value: {value.decode()}")
    # We get the message type field value
    messageType = responseMessage.getFieldValue(35)
    logging.info(f"Received message type: {messageType}")
    # we send a security list request after we received logon message response
    if messageType == "A":
        securityListRequest = SecurityListRequest(config)
        securityListRequest.SecurityReqID = "A"
        securityListRequest.SecurityListRequestType = 0
        send(securityListRequest)
    # After receiving the security list we send a market order request by using the security list first symbol
    elif messageType == "W":
        fix_message = responseMessage.getMessage()

        parser = simplefix.FixParser()

        # Append the FIX message to the parser's buffer (replace '|' with '\x01')
        parser.append_buffer(fix_message.replace('|', '\x01').encode())

        # Extract the message
        # print(fix_message)
        message = parser.get_message()
        
        if message:
            # print(f"Total fields: {message.count()}")
            # for tag, value in message:
            #     print(f"Tag: {tag}, Value: {value.decode()}")
            # else:
            #     print("No complete FIX message found in the buffer.")
            symbol = None
            bid_price = None
            ask_price = None
            time = None
            # print(message)
            for tag, value in message:
                value_decoded = value.decode()
                tag_int = int(tag)
                # print(f"{tag} {value}")
                if tag == 55:  # Symbol
                    symbol = value_decoded
                elif tag == 270:  # Bid and Ask Prices
                    if bid_price is None:
                        bid_price = value_decoded
                    else:
                        ask_price = value_decoded
                elif tag == 52:  # Time
                    time = value_decoded
            # print(f"{tag} {value}")
            if symbol and bid_price and ask_price and time:
                client_price = {
                    "source": "pepperstone",
                    "symbol": static_symbol_ids[symbol],
                    "closeoutBid": bid_price,
                    "closeoutAsk": ask_price,
                    "time": time
                }
                # print(client_price)
                # Connect to Redis and stream the data
                redis_client = redis.Redis(host='redis-live-data', port=6379)
                stream_key = "liveStream"   # Replace 'streamKeyPrefix_' with your actual prefix
                redis_client.xadd(stream_key, {'data': json.dumps(client_price)})

    elif messageType == "y":
        symboldIds = responseMessage.getFieldValue(55)
        # Assuming symboldIds is a list of symbol IDs

        for symbol_id in static_symbol_ids.keys():
            if config["TargetSubID"] != "TRADE":
                # Send market data request for each symbol
                marketDataRequest = MarketDataRequest(config)
                marketDataRequest.MDReqID = "a"  # Unique for each request
                marketDataRequest.SubscriptionRequestType = 1
                marketDataRequest.MarketDepth = 1
                marketDataRequest.NoMDEntryTypes = 1
                marketDataRequest.MDEntryType = 0
                marketDataRequest.NoRelatedSym = 1
                marketDataRequest.Symbol = symbol_id
                send(marketDataRequest)
    # after receiving the new order request response we stop the reactor
    # And we will be disconnected from API
    elif messageType == "8" or messageType == "j":
        print("We are done, stopping the reactor")
        reactor.stop()

def disconnected(client, reason): # Callback for client disconnection
    print("\nDisconnected, reason: ", reason)

def connected(client): # Callback for client connection
    print("Connected")
    logonRequest = LogonRequest(config)
    send(logonRequest)
    
# Setting client callbacks
client.setConnectedCallback(connected)
client.setDisconnectedCallback(disconnected)
client.setMessageReceivedCallback(onMessageReceived)

# Starting the client service
client.startService()
# Run Twisted reactor, we imported it earlier
reactor.run()