# **IoT Sensor Emulator**

A lightweight FastAPI-based emulator for generating synthetic IoT sensor data and sending it to an Azure Function endpoint.
The emulator allows simulating both valid and faulty sensors with configurable frequencies and payload formats.

---

## **Features**

* Simulates multiple sensors in parallel (temperature, weight, voltage, etc.).
* Supports **valid** and **faulty** data modes for robustness testing.
* Sends data to:

  * Azure Function HTTP ingestion endpoint
  * or any custom URL via environment variable
* Web UI for starting/stopping sensors and monitoring last produced values.
* Independent background threads per sensor.

---

## **Project Structure**

```
/template/            # CSS/JS assets for the web UI + Jinja2 UI templates
/docs/                # Screenshots, diagrams, documentation assets
    ui-preview.png    # Screenshot of the emulator web interface
emulator.py           # Main FastAPI application
simulator.py          # Sensor simulation engine
```

---

## **Environment Configuration**

Create an environment variable to define the ingestion endpoint:

```
INGEST_ENDPOINT=https://<your-function-app>.azurewebsites.net/api/<your-function-name>
```

If not provided, the emulator uses a predefined default endpoint.

---

## **Running the Emulator**

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Start the FastAPI server

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the UI

Open:

```
http://localhost:8000
```

From the UI you can:

* Start any sensor
* Stop any sensor
* View current status and last emitted value

---

## **Sensor Logic Overview**

Each sensor runs in its own thread and periodically emits data based on the configuration:

```python
{
    "sensorId": "temp1",
    "sensorType": "temperature",
    "freq_ms": 50,
    "bad": False
}
```

### **Normal mode**

Produces valid payloads:

```json
{
  "sensorId": "temp1",
  "sensorType": "temperature",
  "value": 73.42,
  "timestamp": 1764241722.78
}
```

### **Faulty mode**

Randomly generates malformed or incomplete messages for stress-testing the ingestion pipeline.

---

## **HTTP Endpoints**

### UI

`GET /` — load the dashboard

### Control

```
POST /start/{sensor_id}
POST /stop/{sensor_id}
GET  /status/{sensor_id}
```