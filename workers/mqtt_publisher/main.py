import os
import time
import json
import paho.mqtt.client as mqtt
import random

MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "test/topic")
PUBLISH_INTERVAL = float(os.environ.get("PUBLISH_INTERVAL", 5))  # Interval in seconds

def generate_message():
    """Generate a random message in the required format."""
    return {
        "sensor_id": "river-001",
        "timestamp": int(time.time()),
        "height": round(random.uniform(1.0, 5.0), 2),
        "latitude": 19.4326,
        "longitude": -99.1332,
        "health": {
            "battery": random.randint(50, 100),
            "signal": random.randint(-90, -50),
            "status": "ok"
        }
    }

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    while True:
        message = generate_message()
        payload = json.dumps(message)
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(PUBLISH_INTERVAL)

if __name__ == "__main__":
    main()
