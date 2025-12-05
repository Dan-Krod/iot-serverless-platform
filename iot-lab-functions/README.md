# **IoT Lab – Azure Serverless Functions**

This folder contains the Azure Functions backend for the IoT Lab platform.
The service ingests sensor events, processes them through an event pipeline, stores normalized data in Cosmos DB, and exposes APIs for historical analytics.

## **Project Structure**

```
iot-lab-functions/
│
├── GetSensorHistory/
│   ├── __init__.py           # HTTP API → query Cosmos DB for history
│   └── function.json
│
├── IngestSensorData/
│   ├── __init__.py           # HTTP API → send events to Event Hub
│   ├── function.json
│   └── host.json             # Function-specific settings (Event Hub binding)
│
├── ProcessSensorEvent/
│   ├── __init__.py           # Event Hub trigger → validate → store → DLQ
│   └── function.json
│
├── .funcignore               # Files excluded from deployment
├── .gitignore                # Git exclusions
├── extensions.json           # Binding extensions configuration
├── settings.json             # VS Code workspace settings (local only)
├── tasks.json                # VS Code build/debug tasks
└── requirements.txt          # Python dependencies
```

## **Function Overview**

### **1. IngestSensorData**

**Type:** HTTP Trigger → Event Hub
**Purpose:**
Accepts incoming sensor telemetry via HTTP, validates minimal schema, and publishes events to Azure Event Hub.

### **2. ProcessSensorEvent**

**Type:** Event Hub Trigger → Cosmos DB
**Pipeline:**

* Receives raw events from Event Hub
* Performs validation and normalization
* Inserts valid records into Cosmos DB
* Routes malformed events to a dead-letter mechanism

### **3. GetSensorHistory**

**Type:** HTTP Trigger → Cosmos DB
**Purpose:**
Serves as an analytics endpoint for retrieving historical measurements.
Supports:

* Filtering by `sensorType`
* Timestamp ranges (`start`, `end`)
* Pagination (`limit`)

## **Local Development**

Install dependencies:

```
pip install -r requirements.txt
```

Start the Functions Host:

```
func start
```

> Note: Local Cosmos DB / Event Hub emulation relies on your environment settings and Azurite if configured.

## **Deployment**

Deployment is typically performed via VS Code:

**Azure Functions: Deploy to Function App**

Or via CLI:

```
az login
func azure functionapp publish <FUNCTION_APP_NAME>
```

## **Technology Stack**

* **Azure Functions (Python)**
* **Azure Event Hub**
* **Azure Cosmos DB (Core SQL API)**
* **Function Bindings Extensions**

