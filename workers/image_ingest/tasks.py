import os
import json
import base64
import hashlib
from influxdb_client import InfluxDBClient, Point, WritePrecision
from celery import shared_task
import time

INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")
IMAGE_FOLDER = "enoe/river_images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api()

def compute_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

@shared_task
def process_image_message(message):
    try:
        data = json.loads(message)
        sensor_id = data.get("sensor_id", "unknown")
        timestamp = int(data.get("timestamp", time.time()))
        filename = data.get("filename", f"{sensor_id}_{timestamp}.jpg")
        image_b64 = data.get("image_data")
        if not image_b64:
            print("No image data found in message.")
            return

        image_bytes = base64.b64decode(image_b64)
        filepath = os.path.join(IMAGE_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        hash_value = compute_hash(filepath)

        point = (
            Point("river_image")
            .tag("sensor_id", sensor_id)
            .field("filename", filename)
            .field("hash", hash_value)
            .time(timestamp, WritePrecision.S)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Processed image {filename} for sensor {sensor_id}")
    except Exception as e:
        print(f"Failed to process image message: {e}")