# import redis
# import psycopg2
# import json
# import os
# import time

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from models.model import Base, TickData
# from sqlalchemy.exc import IntegrityError

# from datetime import datetime
# import re

# def fetch_data_from_redis(redis_client, queue_name):
#     return redis_client.brpop(queue_name, 0)  # 0 for infinite timeout

# def old_process_and_save_data(db_conn, data):
#     # Extract closeoutBid, closeoutAsk, and timestamp from the data
#     closeout_bid = data['closeoutBid']
#     closeout_ask = data['closeoutAsk']
#     timestamp = parse_isoformat_with_timezone(data['time'])

#     # Save data to the TimescaleDB hypertable
#     with db_conn.cursor() as cursor:
#         insert_query = "INSERT INTO forex_data (time, closeout_bid, closeout_ask) VALUES (%s, %s, %s)"
#         cursor.execute(insert_query, (timestamp, closeout_bid, closeout_ask))
#         db_conn.commit()

# def process_and_save_data(session, data):
#     # Extract required data from the JSON
#     pair_name = data['symbol']
#     source = data['source']
#     closeout_bid = data['closeoutBid']
#     closeout_ask = data['closeoutAsk']
#     timestamp = parse_isoformat_with_timezone(data['time'])

#     # Create a new TickData object and add it to the session
#     new_tick_data = TickData(
#         pair_name=pair_name,
#         time=timestamp,
#         source=source,
#         bid=closeout_bid,
#         ask=closeout_ask
#     )
#     try:
#         session.add(new_tick_data)
#         session.commit()
#     except IntegrityError:
#         session.rollback()

# def parse_isoformat_with_timezone(date_string):
#     # Remove the 'Z' timezone designator, as Python's fromisoformat() does not handle it
#     date_string = date_string.rstrip('Z')

#     # Truncate the fractional part to microseconds (6 digits)
#     # date_string = re.sub(r'(\.\d{6})\d+', r'\1', date_string)

#     # return datetime.fromisoformat(date_string)
#     formatted_string = datetime.strptime(date_string, '%Y%m%d-%H:%M:%S.%f').isoformat()

#     return datetime.fromisoformat(formatted_string)

# def continuous_processing(redis_client, db_conn, queue_name):
#     while True:
#         _, raw_data = fetch_data_from_redis(redis_client, queue_name)
#         if raw_data:
#             # Decode and load the JSON data
#             raw_data = raw_data.decode('utf-8')
#             data = json.loads(raw_data)

#             # Extract the nested JSON data
#             data = json.loads(data['data'])

#             # Process and save the data
#             process_and_save_data(db_conn, data)

# if __name__ == "__main__":
#     redis_client = redis.Redis(host='redis-queue', port=6379, db=0)
#     # db_conn = psycopg2.connect(
#     #     dbname=os.getenv('POSTGRES_DB'),
#     #     user=os.getenv('POSTGRES_USER'),
#     #     password=os.getenv('POSTGRES_PASSWORD'),
#     #     host=os.getenv('POSTGRES_HOST')
#     # )
#     db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
#     engine = create_engine(db_url)
#     Base.metadata.bind = engine
#     DBSession = sessionmaker(bind=engine)
#     session = DBSession()

#     # Connect to Redis and start processing
#     redis_client = redis.Redis(host='redis-queue', port=6379, db=0)
#     continuous_processing(redis_client, session, 'processed_data_queue')
#     # continuous_processing(redis_client, db_conn, 'processed_data_queue')






import redis
import psycopg2
import json
import os
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.model import Base, OneMinData, FiveMinData, FifteenMinData, ThirtyMinData, OneHourData
from sqlalchemy.exc import IntegrityError

# Establish database connection
db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Connect to Redis
redis_client = redis.Redis(host='redis-queue', port=6379, db=0)


# Other imports remain the same

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Modify existing functions to include logging
def save_ohlc_data(ohlc_data, symbol, source, timeframe, timeframe_class):
    """
    Save OHLC data to the database.
    """
    try:
        ohlc_entry = timeframe_class(
            time=get_timeframe_start(datetime.utcnow(), timeframe),  # Adjust as necessary
            pair_name=symbol,
            source=source,
            open=ohlc_data['open'],
            high=ohlc_data['high'],
            low=ohlc_data['low'],
            close=ohlc_data['close']
        )
        session.add(ohlc_entry)
        session.commit()
        logging.info(f"OHLC data saved successfully for {symbol} - {timeframe}min timeframe")
    except IntegrityError as e:
        logging.error(f"Error saving OHLC data for {symbol} - {timeframe}min timeframe: {e}")
        session.rollback()
from datetime import datetime, timedelta

def get_timeframe_start(current_time, timeframe_minutes):
    """
    Rounds down the current time to the nearest start of the timeframe.

    Parameters:
    - current_time: datetime.datetime object representing the current time
    - timeframe_minutes: integer representing the timeframe duration in minutes

    Returns:
    A datetime.datetime object representing the start of the current timeframe.
    """
    # Convert the timeframe to a timedelta
    timeframe_delta = timedelta(minutes=timeframe_minutes)

    # Calculate the number of timeframes since the epoch
    time_since_epoch = current_time - datetime(1970, 1, 1)
    timeframe_count_since_epoch = time_since_epoch // timeframe_delta

    # Calculate the start of the current timeframe
    timeframe_start = datetime(1970, 1, 1) + (timeframe_count_since_epoch * timeframe_delta)

    return timeframe_start

def process_tick_data(tick_data):
    """
    Process a single tick of data.
    """
    try:
        symbol = tick_data['symbol']
        source = tick_data['source']
        logging.info(f"Processed tick data for {symbol}")
        timestamp = parse_datetime_from_string(tick_data['time'])
        
        # Example: Process and save for 1-minute timeframe
        ohlc_data = aggregate_to_ohlc([tick_data], 1)  # This is simplified; aggregate correctly in practice
        save_ohlc_data(ohlc_data, symbol, source, 1, OneMinData)
        
    except Exception as e:
        logging.error(f"Failed to process tick data: {e}")

def aggregate_to_ohlc(tick_data, timeframe):
    """
    Aggregates tick data into OHLC format for a given timeframe.

    Parameters:
    - tick_data: list of tick data dictionaries
    - timeframe: the timeframe in minutes for the OHLC data

    Returns:
    A dictionary with OHLC data.
    """
    # Initialize the OHLC data structure
    ohlc_data = {
        'open': None,
        'high': None,
        'low': None,
        'close': None
    }

    for tick in tick_data:
        bid = float(tick['closeoutBid'])
        ask = float(tick['closeoutAsk'])
        mid_price = (bid + ask) / 2

        if ohlc_data['open'] is None:
            ohlc_data['open'] = mid_price

        if ohlc_data['high'] is None or mid_price > ohlc_data['high']:
            ohlc_data['high'] = mid_price

        if ohlc_data['low'] is None or mid_price < ohlc_data['low']:
            ohlc_data['low'] = mid_price

        ohlc_data['close'] = mid_price

    return ohlc_data

def parse_datetime_from_string(date_string):
    """
    Parses a datetime string to a datetime object.
    """
    # The format needs to match the format of your incoming date_string
    # Adjust the format string according to your actual date_string format
    try:
        return datetime.strptime(date_string, "%Y%m%d-%H:%M:%S.%f")
    except ValueError as e:
        logging.error(f"Failed to parse datetime from string {date_string}: {e}")
        return None
def continuous_processing(redis_client, queue_name):
    while True:
        try:
            logging.info("test test")
            _, raw_data = redis_client.brpop(queue_name, 0)  # 0 for infinite timeout
            try:
                data_string = raw_data.decode('utf-8')
                data = json.loads(data_string)
                logging.info(f"Decoded tick data: {data}")
                
                # Parse the JSON string found under the 'data' key
                tick_data = json.loads(data['data'])
                logging.info(f"Tick data fetched from Redis: {tick_data}")
                
                process_tick_data(tick_data)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                return
            except KeyError as e:
                logging.error(f"Key error - missing key: {e}")
                return
            except Exception as e:
                logging.error(f"Unexpected error processing data from Redis: {e}")
                return
        except Exception as e:
            logging.error(f"Error in continuous processing: {e}")


#read data from redis
#parse data into ohlc
#check if its not exist, add it into database            


if __name__ == "__main__":
    logging.info("Starting tick data processing script")
    continuous_processing(redis_client, 'processed_data_queue')

