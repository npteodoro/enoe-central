import os
import redis
import time
from celery import Celery

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

celery_app = Celery('db_writer')
celery_app.config_from_object('db_writer.celeryconfig')

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def main():
    from db_writer.tasks import write_to_influx
    print("db_writer started, scanning for mqtt:* keys in Redis...")
    while True:
        for key in redis_client.scan_iter("mqtt:*"):
            topic = key.decode().split("mqtt:")[1]
            payload = redis_client.rpop(key)
            if payload:
                write_to_influx.delay(topic, payload.decode())  # Use Celery async task
        time.sleep(1)

if __name__ == "__main__":
    main()
    
import db_writer.tasks
