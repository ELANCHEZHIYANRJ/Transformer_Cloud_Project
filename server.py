# CRITICAL COMPILER PASS: The gevent monkey patch module MUST execute at line 1 
# before importing any other system extensions, or the async data loop will deadlock!
from gevent import monkey
monkey.patch_all()

import os
import json
from flask import Flask, send_from_directory
from flask_sock import Sock
import paho.mqtt.client as mqtt

app = Flask(__name__)
sock = Sock(app)

web_clients = []

# --- EMQX FREE PUBLIC BROKER NETWORK CONFIGURATION ---
MQTT_SERVER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "transformer/telemetry/elans_unique_project_node" 

@app.route('/')
def home():
    # Serves the index.html template file directly from the root execution directory
    return send_from_directory(os.getcwd(), 'index.html')

# Maps the WebSocket client loop cleanly to your root endpoint string choice
@sock.route('/')
def live_stream(ws):
    print("New browser client hooked to live web dashboard!")
    web_clients.append(ws)
    try:
        while True:
            ws.receive()
    except Exception:
        pass
    finally:
        if ws in web_clients:
            web_clients.remove(ws)

# --- MQTT CLOUD BRIDGE EVENT HANDLERS ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Success! Web server securely hooked into EMQX global pipeline.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Cloud data bridge connection rejected with code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)
        print("Intercepted Mesh Frame:", data)
        
        sensor_payload = {
            "val1": data.get("val1", "--"),
            "val2": data.get("val2", "--"),
            "val3": data.get("val3", "--"),
            "val4": data.get("val4", "--")
        }
        
        # Broadcast the metrics to all globally open browser dashboard tabs instantly
        dead_clients = []
        for web_client in web_clients:
            try:
                web_client.send(json.dumps(sensor_payload))
            except Exception:
                dead_clients.append(web_client)
        for dead in dead_clients:
            if dead in web_clients:
                web_clients.remove(dead)
    except Exception as e:
        print("Data parsing error:", e)

# Spin up public cluster broker interface
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Could not reach EMQX node: {e}")

if __name__ == '__main__':
    # Dynamically inject the runtime environment port numbers passed down by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
