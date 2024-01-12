import redis
import json

from standardize_and_validate import standardize_and_validate
#chmod +x subscribe_redis_stream.py
# Connect to Redis instances
redis_live = redis.Redis(host='redis-live-data', port=6379, db=0)
redis_queue = redis.Redis(host='redis-queue', port=6380, db=0)


# Subscribe to Redis live data stream
pubsub = redis_live.pubsub()
pubsub.subscribe('price_stream_EUR_USD')

print("Subscribed to Redis channel for live data.")
# Process incoming messages
for message in pubsub.listen():
    if message['type'] == 'message':
        raw_data = json.loads(message['data'])
        validated_data = standardize_and_validate(raw_data)

        # Push validated data to the Redis queue
        redis_queue.rpush('processed_data_queue', json.dumps(validated_data))
