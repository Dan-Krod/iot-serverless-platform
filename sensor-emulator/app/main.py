from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from simulator import SensorSimulator
import os

app = FastAPI()
templates = Jinja2Templates(directory="template")
app.mount("/static", StaticFiles(directory="static"), name="static")

ENDPOINT = os.environ.get("INGEST_ENDPOINT",
    "INGEST_ENDPOINT=https://<your-function-app>.azurewebsites.net/api/<your-function-name>"
)

sensors_config = {
    "temp1": {"sensorId":"temp1","sensorType":"temperature","freq_ms":50,"bad":False},
    "weight1": {"sensorId":"weight1","sensorType":"weight","freq_ms":80,"bad":False},
    "volt1": {"sensorId":"volt1","sensorType":"voltage","freq_ms":100,"bad":False},
    "tempBad": {"sensorId":"tempBad","sensorType":"temperature","freq_ms":100,"bad":True},
    "weightBad": {"sensorId":"weightBad","sensorType":"weight","freq_ms":120,"bad":True}
}

simulators = {k: SensorSimulator(cfg, ENDPOINT) for k, cfg in sensors_config.items()}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "sensors": list(sensors_config.keys()),
            "sensors_config": sensors_config 
        }
    )

@app.post("/start/{sensor_id}")
def start_sensor(sensor_id: str):
    sim = simulators.get(sensor_id)
    if sim:
        sim.start()
        return {"status": "started", "sensor": sensor_id}
    return {"error": "sensor not found"}

@app.post("/stop/{sensor_id}")
def stop_sensor(sensor_id: str):
    sim = simulators.get(sensor_id)
    if sim:
        sim.stop()
        return {"status": "stopped", "sensor": sensor_id}
    return {"error": "sensor not found"}

@app.get("/status/{sensor_id}")
def sensor_status(sensor_id: str):
    sim = simulators.get(sensor_id)
    if sim:
        running = sim.thread.is_alive() if sim.thread else False
        return {"running": running, "last_value": sim.last_value}
    return {"error": "sensor not found"}
