import logging, os, json
import azure.functions as func
from azure.cosmos import CosmosClient

COSMOS_URI = os.environ["COSMOS_DB_CONNECTION"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = os.environ.get("COSMOS_DB_NAME")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER")

client = CosmosClient(COSMOS_URI, COSMOS_KEY)
container = client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

def main(req: func.HttpRequest) -> func.HttpResponse:
    sensor_type = req.params.get("sensorType")
    if not sensor_type:
        return func.HttpResponse("Please pass sensorType=<type>", status_code=400)

    sensor_id = req.params.get("sensorId")
    start_ts = req.params.get("start")
    end_ts = req.params.get("end")
    limit = int(req.params.get("limit", 100))

    query = "SELECT TOP @limit * FROM c WHERE c.sensorType=@sensorType"
    params = [
        {"name":"@sensorType","value":sensor_type},
        {"name":"@limit","value":limit}
    ]

    if sensor_id:
        query += " AND c.sensorId=@sensorId"
        params.append({"name":"@sensorId","value":sensor_id})
    if start_ts:
        query += " AND c.timestamp >= @start"
        params.append({"name":"@start","value":float(start_ts)})
    if end_ts:
        query += " AND c.timestamp <= @end"
        params.append({"name":"@end","value":float(end_ts)})

    query += " ORDER BY c.timestamp DESC"

    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return func.HttpResponse(json.dumps(items), status_code=200, mimetype="application/json")
