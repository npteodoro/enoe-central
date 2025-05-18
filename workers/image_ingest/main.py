import os
import hashlib
import redis
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
import time

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")
IMAGE_FOLDER = "enoe/river_images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=None)

def compute_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

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

        import base64
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

def main():
    while True:
        _, message = redis_client.blpop("image_queue")
        if message:
            process_image_message(message.decode())

if __name__ == "__main__":
    main()