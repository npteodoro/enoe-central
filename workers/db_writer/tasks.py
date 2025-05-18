import os
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from celery import shared_task

INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api()

@shared_task
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