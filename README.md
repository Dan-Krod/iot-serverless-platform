# IOT-Serverless-Platform

This repository contains a **serverless IoT platform** project designed for simulation, ingestion, and processing of IoT sensor data using Azure Functions and a local sensor emulator.

---

## Repository Structure

```

IOT-Serverless-Platform/
├── iot-lab-functions/       # Azure Functions project
│   ├── GetSensorHistory/    # Function to retrieve sensor history
│   ├── IngestSensorData/    # Function to ingest sensor data into Event Hub
│   ├── ProcessSensorEvent/  # Function to process Event Hub events and store in Cosmos DB
│   ├── requirements.txt
│   ├── host.json
│   └── ...                  # Configuration and VS Code metadata files
└── sensor-emulator/         # Local sensor emulator
    ├── template/            # CSS/JS assets for the web UI + Jinja2 UI templates
    ├── docs/                # Screenshots, diagrams, documentation assets
    │   └── ui-preview.png    # Screenshot of the emulator web interface
    ├── emulator.py           # Main FastAPI application
    └── simulator.py          # Sensor simulation engine

````

## Components

### 1. Sensor Emulator
- **Purpose:** Simulates multiple types of IoT sensors with configurable frequency and endpoints.
- **Features:**
  - Supports temperature, weight, voltage sensors and "bad" sensors generating invalid data for DLQ testing.
  - Configurable transmission frequency (20–100 ms).
  - Web UI for starting/stopping sensors and viewing last values.
- **Usage:**
```bash
uvicorn emulator:app --reload --host 0.0.0.0 --port 8000
````

Open [http://localhost:8000](http://localhost:8000) in a browser.

---

### 2. Azure Functions (`iot-lab-functions`)

* **Purpose:** Serverless backend for ingesting, processing, and retrieving IoT sensor data.
* **Functions:**

  1. **IngestSensorData** – HTTP endpoint for receiving sensor events and forwarding them to Event Hub.
  2. **ProcessSensorEvent** – Event Hub triggered function that validates, stores events in Cosmos DB, and sends invalid events to DLQ.
  3. **GetSensorHistory** – Retrieves sensor history from Cosmos DB.
* **Deployment:** Deploy using VS Code or Azure CLI.

---

## IoT Event Schema

All sensor events follow a standard structure:

```json
{
  "id": "uuid",
  "sensorId": "temp1",
  "sensorType": "temperature",
  "value": 23.5,
  "unit": "C",
  "timestamp": 1733929200,
  "location": {
    "lat": х.х,
    "lon": х.х
  },
  "raw": { ... } // original sensor payload
}
```

* Allows uniform handling of different sensor types.
* Easy to extend with new fields without breaking existing functions.
* Supports routing and analytics.

---

## Local Testing

1. Run the **sensor emulator** locally.
2. Start Azure Functions locally:

```bash
func start
```

3. Use web UI to start sensors and monitor logs.
4. Verify DLQ handling by enabling "bad" sensors.

---

## Deployment

1. Authenticate with Azure:

```bash
az login
```

2. Deploy `iot-lab-functions` using VS Code: **Deploy to Azure Function App**
3. Verify functionality with real Event Hub and Cosmos DB endpoints.
