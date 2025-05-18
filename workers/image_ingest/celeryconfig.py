import os

broker_url = f'redis://{os.environ.get("REDIS_HOST", "redis")}:{os.environ.get("REDIS_PORT", 6379)}/0'
result_backend = broker_url
imports = ('image_ingest.tasks',)