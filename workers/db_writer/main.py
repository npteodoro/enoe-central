import os
import redis
from celery import Celery
from influxdb_client import InfluxDBClient, Point, WritePrecision
import json

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")

celery_app = Celery(
    'db_writer',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api()

@celery_app.task
def write_to_influx(topic, payload):
    """Write a single message to InfluxDB."""
    try:
        data = json.loads(payload)
        point = (
            Point("river_height")
            .tag("sensor_id", data.get("sensor_id", "unknown"))
            .tag("topic", topic)
            .field("height", float(data.get("height", 0)))
            .field("latitude", float(data.get("latitude", 0)))
            .field("longitude", float(data.get("longitude", 0)))
            .field("battery", int(data.get("health", {}).get("battery", 0)))
            .field("signal", int(data.get("health", {}).get("signal", 0)))
            .field("status", str(data.get("health", {}).get("status", "")))
            .time(int(data.get("timestamp", 0)), WritePrecision.S)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    except Exception as e:
        print(f"Failed to parse or write payload: {payload} ({e})")

@celery_app.task
def process_redis_messages():
    """Scan Redis for messages and enqueue them for writing to InfluxDB."""
    for key in redis_client.scan_iter("mqtt:*"):
        print("message found")
        topic = key.decode().split("mqtt:")[1]
        print(f"Processing: {topic}")
        while True:
            payload = redis_client.rpop(key)
            if not payload:
                break
            write_to_influx.delay(topic, payload.decode())
        # Optionally delete the key if it's empty
        if redis_client.llen(key) == 0:
            redis_client.delete(key)

def main():
    """Continuously enqueue Redis processing tasks."""
    print("Starting Redis message processing...")
    while True:
        process_redis_messages.delay()

if __name__ == "__main__":
    main()
