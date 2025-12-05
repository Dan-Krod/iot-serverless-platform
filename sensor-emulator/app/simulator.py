from threading import Thread, Event
import time, random, requests

class SensorSimulator:
    def __init__(self, config, endpoint):
        self.config = config
        self.endpoint = endpoint
        self.thread = None
        self.stop_event = Event()
        self.last_value = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            # Генерація даних
            if self.config.get("bad"):
                choice = random.choice([0,1,2,3])
                if choice == 0:
                    data = {}
                elif choice == 1:
                    data = {
                        "sensorId": self.config["sensorId"],
                        "sensorType": self.config["sensorType"],
                        "value": "bad_value"
                    }
                elif choice == 2:
                    data = {
                        "sensorId": self.config["sensorId"],
                        "sensorType": self.config["sensorType"],
                        "value": "NaN",
                        "timestamp": "not_a_timestamp"
                    }
                else:
                    data = {
                        "sensorId": self.config["sensorId"],
                        "sensorType": self.config["sensorType"],
                        "value": 100,
                        "timestamp": time.time()
                    }
            else:
                data = {
                    "sensorId": self.config["sensorId"],
                    "sensorType": self.config["sensorType"],
                    "value": round(random.uniform(0, 100), 2),
                    "timestamp": time.time()
                }

            self.last_value = data  # <- Зберігаємо останнє значення

            try:
                requests.post(self.endpoint, json=data, headers={"Content-Type": "application/json"}, timeout=5)
            except Exception as e:
                print(f"[{self.config['sensorId']}] Send error:", e)

            time.sleep(self.config.get("freq_ms", 100)/1000.0)
