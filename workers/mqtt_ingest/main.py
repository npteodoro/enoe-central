import os
import redis
import paho.mqtt.client as mqtt

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "test/topic")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def persist_message(topic, payload):
    redis_client.lpush(f"mqtt:{topic}", payload)
    print(f"Pushed to Redis: mqtt:{topic} -> {payload}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message on {msg.topic}: {payload}")
    persist_message(msg.topic, payload)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()