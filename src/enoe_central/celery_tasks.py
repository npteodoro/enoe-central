from .celery import app
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import os

INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")

influx_client = InfluxDBClient(url=INFLUXDB_URL, org=INFLUXDB_ORG, token=INFLUXDB_TOKEN, debug=True)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)

@app.task
def db_writer(topic, payload):
    """Write a single message to InfluxDB."""
    print(f"Writting to Influxdb: {topic} -> {payload}")
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
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print(f"Recorded {INFLUXDB_BUCKET} -> {point}")

    except Exception as e:
        print(f"Failed to parse or write payload: {payload} ({e})")
        raise
