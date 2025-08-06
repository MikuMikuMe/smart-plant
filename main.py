Creating a comprehensive IoT-based plant monitoring system can be quite involved. Below is a simplified version of such a system using Python. This example assumes the use of a DHT11 sensor to measure humidity and temperature, a soil moisture sensor for measuring soil moisture level, and a Light Dependent Resistor (LDR) to detect light intensity. I'll include error handling and comments for better understanding.

### Prerequisites
Before running this code, make sure you have:
1. Raspberry Pi (or any other microcontroller)
2. DHT11 sensor
3. Soil moisture sensor
4. Light sensor (LDR)
5. Appropriate libraries installed (e.g., `gpiozero` for GPIO handling, `Adafruit_DHT` for DHT11 sensor)
6. Network connection for real-time data transmission (you can use MQTT, HTTP, or any other protocol)

The following Python libraries might need to be installed:
- `Adafruit_DHT`
- `paho-mqtt` if you're using MQTT for real-time updates

Here's a foundational Python program:

```python
import Adafruit_DHT
from gpiozero import MCP3008, LightSensor
import time
import paho.mqtt.client as mqtt

# Sensor and GPIO configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO pin for DHT11
SOIL_SENSOR_CHANNEL = 0  # Analog channel for soil sensor
MOISTURE_THRESHOLD = 300  # Example threshold for soil moisture
LDR_PIN = 18  # GPIO pin for LDR
BROKER_ADDRESS = "your_mqtt_broker_address"
TOPIC = "smart-plant/monitoring"

def read_environmental_data():
    """
    Read data from sensors
    """
    # Read temperature and humidity from DHT11
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    # Read soil moisture level
    soil_moisture_sensor = MCP3008(channel=SOIL_SENSOR_CHANNEL)
    soil_moisture = soil_moisture_sensor.value * 1023  # Scale ADC value

    # Read light intensity
    light_sensor = LightSensor(LDR_PIN)
    light_intensity = light_sensor.value

    return humidity, temperature, soil_moisture, light_intensity

def on_connect(client, userdata, flags, rc):
    """
    MQTT callback for connection
    """
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    """
    MQTT callback for receiving messages
    """
    print(msg.topic + " " + str(msg.payload))

def send_alerts(humidity, temperature, soil_moisture, light_intensity):
    """
    Send alerts based on sensor data
    """
    if humidity is None or temperature is None:
        print("Failed to retrieve data from DHT sensor")
        return

    alerts = []
    if soil_moisture > MOISTURE_THRESHOLD:
        alerts.append("Soil is too dry. Consider watering the plant.")
    if temperature < 15 or temperature > 30:
        alerts.append(f"Temperature is {'too low' if temperature < 15 else 'too high'}. Current temp: {temperature:.2f} C")
    if light_intensity < 0.2:
        alerts.append("Plant needs more light.")

    return alerts

def main():
    # Initialize MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, 1883, 60)
    
    client.loop_start()

    try:
        while True:
            humidity, temperature, soil_moisture, light_intensity = read_environmental_data()
            alerts = send_alerts(humidity, temperature, soil_moisture, light_intensity)
            
            # Print or send the alerts
            if alerts:
                for alert in alerts:
                    print(alert)
                    client.publish(TOPIC, alert)
            
            time.sleep(60)  # Wait for 1 minute before next reading

    except KeyboardInterrupt:
        print("Terminating the program.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
```

### Key Elements in this Program

- **Sensor Reading**: The program fetches data from a DHT11 temperature/humidity sensor, a soil moisture sensor, and a light sensor.
- **Alerts and Notifications**: Simple threshold-based alerts for each type of measurement are generated; these alerts inform the user if the plant requires attention.
- **Error Handling**: Basic error handling includes retrying sensor readings and catching exceptions.
- **MQTT Setup**: Utilizes MQTT for real-time data alerts. You need to set the `BROKER_ADDRESS` to your MQTT broker's address.

This example presents a basic structure; you should further refine the program according to your intelligent plant monitoring system's requirements, perhaps integrating a GUI, adding a database for historical data, or more advanced alert management.