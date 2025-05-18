import os
import time
import json
import paho.mqtt.client as mqtt
import redis
from influxdb_client import InfluxDBClient
import base64

# Environment variables
MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "test/topic")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")

def publish_test_message():
    message = {
        "sensor_id": "test-sensor",
        "timestamp": int(time.time()),
        "height": 2.34,
        "latitude": 19.4326,
        "longitude": -99.1332,
        "health": {
            "battery": 99,
            "signal": -60,
            "status": "ok"
        }
    }
    payload = json.dumps(message)
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, payload)
    print(f"Published test message to MQTT: {payload}")
    return message

def check_redis(message):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    key = f"mqtt:{MQTT_TOPIC}"
    time.sleep(2)  # Wait for ingestion
    msgs = r.lrange(key, 0, -1)
    found = any(json.loads(m.decode())["sensor_id"] == message["sensor_id"] for m in msgs)
    print("✅ Found test message in Redis!" if found else "❌ Test message NOT found in Redis.")
    return found

def check_influxdb(message):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "river_height" and r.sensor_id == "{message["sensor_id"]}")
'''
    tables = client.query_api().query(query, org=INFLUXDB_ORG)
    found = any(tables)
    print("✅ Found test message in InfluxDB!" if found else "❌ Test message NOT found in InfluxDB.")
    return found

def publish_test_image():
    # Create a dummy image (1x1 pixel PNG)
    image_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xf8\x0f'
        b'\x00\x01\x01\x01\x00\x18\xdd\x8d\x18\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    image_b64 = base64.b64encode(image_bytes).decode()
    message = {
        "sensor_id": "test-sensor-img",
        "timestamp": int(time.time()),
        "filename": "test_image.png",
        "image_data": image_b64
    }
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r.lpush("image_queue", json.dumps(message))
    print("Published test image to Redis image_queue.")

def check_image_influxdb():
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "river_image" and r.sensor_id == "test-sensor-img")
'''
    tables = client.query_api().query(query, org=INFLUXDB_ORG)
    found = any(tables)
    print("✅ Found test image metadata in InfluxDB!" if found else "❌ Test image metadata NOT found in InfluxDB.")
    return found

def main():
    message = publish_test_message()
    check_redis(message)
    time.sleep(5)  # Wait for db_writer to process
    check_influxdb(message)
    # Test image ingestion
    publish_test_image()
    time.sleep(5)
    check_image_influxdb()

if __name__ == "__main__":
    main()