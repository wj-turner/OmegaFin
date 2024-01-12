import redis
import psycopg2
import json
import os
import time
from datetime import datetime
import re

def fetch_data_from_redis(redis_client, queue_name):
    return redis_client.brpop(queue_name, 0)  # 0 for infinite timeout

def process_and_save_data(db_conn, data):
    # Extract closeoutBid, closeoutAsk, and timestamp from the data
    closeout_bid = data['closeoutBid']
    closeout_ask = data['closeoutAsk']
    timestamp = parse_isoformat_with_timezone(data['time'])

    # Save data to the TimescaleDB hypertable
    with db_conn.cursor() as cursor:
        insert_query = "INSERT INTO forex_data (time, closeout_bid, closeout_ask) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (timestamp, closeout_bid, closeout_ask))
        db_conn.commit()

def parse_isoformat_with_timezone(date_string):
    # Remove the 'Z' timezone designator, as Python's fromisoformat() does not handle it
    date_string = date_string.rstrip('Z')

    # Truncate the fractional part to microseconds (6 digits)
    date_string = re.sub(r'(\.\d{6})\d+', r'\1', date_string)

    return datetime.fromisoformat(date_string)

def continuous_processing(redis_client, db_conn, queue_name):
    while True:
        _, raw_data = fetch_data_from_redis(redis_client, queue_name)
        if raw_data:
            # Decode and load the JSON data
            raw_data = raw_data.decode('utf-8')
            data = json.loads(raw_data)

            # Extract the nested JSON data
            data = json.loads(data['data'])

            # Process and save the data
            process_and_save_data(db_conn, data)

if __name__ == "__main__":
    redis_client = redis.Redis(host='redis-queue', port=6379, db=0)
    db_conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST')
    )

    continuous_processing(redis_client, db_conn, 'processed_data_queue')
