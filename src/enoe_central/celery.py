import os
from celery import Celery

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DATABASE = int(os.environ.get("REDIS_DATABASE", 0))

app = Celery('enoe_central',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}',
    include=['enoe_central.celery_tasks']
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
