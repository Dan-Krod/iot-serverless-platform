import logging
import os
import json
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData

EVENTHUB_CONNECTION = os.environ.get("EVENTHUB_CONNECTION")
EVENTHUB_NAME = os.environ.get("EVENTHUB_NAME")

producer = EventHubProducerClient.from_connection_string(conn_str=EVENTHUB_CONNECTION, eventhub_name=EVENTHUB_NAME)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    events = []
    if isinstance(payload, list):
        events = payload
    elif isinstance(payload, dict):
        events = [payload]
    else:
        return func.HttpResponse("JSON must be object or array", status_code=400)

    batch_events = []
    for ev in events:
        if not all(k in ev for k in ("sensorId","sensorType","value","timestamp")):
            return func.HttpResponse("Missing fields in item", status_code=400)
        batch_events.append(EventData(json.dumps(ev)))

    try:
        with producer:
            producer.send_batch(batch_events)
    except Exception as e:
        logging.exception("Failed to send to Event Hub")
        return func.HttpResponse(f"Send failed: {e}", status_code=500)

    return func.HttpResponse("Accepted", status_code=200)
