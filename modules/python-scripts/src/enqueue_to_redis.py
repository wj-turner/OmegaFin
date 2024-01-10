import redis
import json
import threading

from standardize_and_validate import standardize_and_validate

# Function to read and process data from the Redis stream

def read_and_process_stream(redis_live, redis_queue, stream_name):
    last_id = '0'  # Start reading from the beginning of the stream

    while True:
        # Read from the stream
        stream_data = redis_live.xread({stream_name: last_id}, count=100, block=10000)
        
        if stream_data:
            for _, messages in stream_data:
                for message_id, message in messages:
                    # Convert message data from bytes to string or a proper format
                    raw_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in message.items()}

                    # Now process the data
                    validated_data = standardize_and_validate(raw_data)

                    # Push validated data to the Redis queue
                    redis_queue.rpush('processed_data_queue', json.dumps(validated_data))

                    last_id = message_id  # Update last_id for next read

# Main execution
if __name__ == "__main__":
    # Connect to Redis instances
    redis_live = redis.Redis(host='redis-live-data', port=6379, db=0)
    redis_queue = redis.Redis(host='redis-queue', port=6379, db=0)

    # Start a separate thread to read and process the stream
    processing_thread = threading.Thread(target=read_and_process_stream, args=(redis_live, redis_queue, 'price_stream_EUR_USD'))
    processing_thread.start()
