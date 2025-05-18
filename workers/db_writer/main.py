import os
import redis
from celery import Celery
from influxdb_client import InfluxDBClient, Point, WritePrecision
import json
import time

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

def write_to_influx(topic, payload):
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

def main():
    print("db_writer started, scanning for mqtt:* keys in Redis...")
    print("INFLUXDB_URL:", INFLUXDB_URL)
    print("INFLUXDB_TOKEN:", INFLUXDB_TOKEN)
    print("INFLUXDB_ORG:", INFLUXDB_ORG)
    print("INFLUXDB_BUCKET:", INFLUXDB_BUCKET)
    while True:
        for key in redis_client.scan_iter("mqtt:*"):
            print(f"Found Redis key: {key}")
            topic = key.decode().split("mqtt:")[1]
            payload = redis_client.rpop(key)
            if payload:
                print(f"Processing payload from {key}: {payload}")
                write_to_influx(topic, payload.decode())  # <-- Remove .delay
        time.sleep(1)

if __name__ == "__main__":
    main()
