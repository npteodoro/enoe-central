import os
import redis
import time
from celery import Celery

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

celery_app = Celery('image_ingest')
celery_app.config_from_object('image_ingest.celeryconfig')

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def main():
    from image_ingest.tasks import process_image_message
    print("image_ingest started, listening for image_queue in Redis...")
    while True:
        _, message = redis_client.blpop("image_queue")
        if message:
            process_image_message.delay(message.decode())
        time.sleep(1)

if __name__ == "__main__":
    main()
    
import image_ingest.tasks
