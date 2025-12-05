from typing import List
import logging, json, os, uuid
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.eventhub import EventHubProducerClient, EventData
import azure.functions as func

COSMOS_URI = os.environ.get("COSMOS_DB_CONNECTION")
COSMOS_KEY = os.environ.get("COSMOS_KEY")
COSMOS_DB = os.environ.get("COSMOS_DB_NAME")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER")

try:
    client = CosmosClient(COSMOS_URI, COSMOS_KEY)
except Exception as e:
    logging.error(f"Cannot connect to Cosmos DB: {e}")
    client = None  

DLQ_CONN = os.environ.get("DLQ_CONNECTION")
DLQ_NAME = os.environ.get("DLQ_NAME")

try:
    dlq_producer = EventHubProducerClient.from_connection_string(
        conn_str=DLQ_CONN,
        eventhub_name=DLQ_NAME
    )
except Exception as e:
    logging.error(f"Cannot connect to DLQ Event Hub: {e}")
    dlq_producer = None

def send_to_dlq(data, reason):
    payload = {
        "failedEvent": data,
        "reason": reason,
        "failedAt": datetime.utcnow().isoformat() + "Z"
    }
    if dlq_producer is None:
        logging.error(f"DLQ producer not available. Cannot send: {reason}")
        return

    try:
        with dlq_producer:
            dlq_producer.send_batch([EventData(json.dumps(payload))])
        logging.warning(f"Message sent to DLQ: {reason}")
    except Exception as e:
        logging.error(f"Failed to send to DLQ: {e}")

def validate_event(data):
    required_fields = ["sensorId", "sensorType", "value", "timestamp"]
    for f in required_fields:
        if f not in data:
            return False, f"Missing field: {f}"

    if not isinstance(data["sensorId"], str):
        return False, "sensorId must be a string"
    if not isinstance(data["sensorType"], str):
        return False, "sensorType must be a string"
    if not isinstance(data["value"], (int, float)):
        return False, "value must be numeric"
    if not isinstance(data["timestamp"], (int, float)):
        return False, "timestamp must be numeric"

    return True, ""

def main(events: List[func.EventHubEvent]):
    logging.info("EventHub trigger received event(s)")

    if client is None:
        logging.error("Cosmos client not initialized. Exiting function.")
        return

    db_client = client.get_database_client(COSMOS_DB)
    container = db_client.get_container_client(COSMOS_CONTAINER)

    for event in events:
        body = event.get_body().decode("utf-8")

        try:
            data = json.loads(body)
        except Exception:
            send_to_dlq(body, "Invalid JSON")
            continue

        is_valid, reason = validate_event(data)
        if not is_valid:
            send_to_dlq(data, reason)
            continue

        try:
            doc = {
                "id": str(uuid.uuid4()),
                "sensorId": data["sensorId"],
                "sensorType": data["sensorType"],
                "value": data["value"],
                "unit": data.get("unit"),
                "timestamp": data["timestamp"],
                "location": data.get("location"),
                "ingestTime": datetime.utcnow().isoformat() + "Z",
                "raw": data
            }
            container.create_item(doc)
            logging.info(f"Saved event from {data['sensorId']}")
        except Exception as ex:
            send_to_dlq(data, f"Cosmos DB error: {ex}")
