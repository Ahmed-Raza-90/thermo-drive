from flask import Flask, render_template, jsonify, request
import random, csv
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "system_log.csv"

# Create log file if not exists
try:
    open(LOG_FILE, "r")
except:
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "System", "Value", "Status"])

# --------- STATES ----------
temperature = 25.0
temp_direction = 1

# --------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/temperature")
def temperature_api():
    global temperature, temp_direction
    threshold = float(request.args.get("threshold", 45))

    temperature += random.uniform(0.4, 1.0) * temp_direction

    if temperature >= 60:
        temp_direction = -1
    if temperature <= 22:
        temp_direction = 1

    if temperature < 36:
        status = "NORMAL"
    elif temperature <= threshold:
        status = "WARNING"
    else:
        status = "ALERT"

    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(
            [datetime.now(), "Temperature", round(temperature,2), status]
        )

    return jsonify({"value": round(temperature,2), "status": status})

@app.route("/vehicle")
def vehicle_api():
    safe = int(request.args.get("safe", 20))
    vehicles = []

    for i in range(random.randint(1,4)):
        dist = random.uniform(5, 150)

        if dist < 10:
            status = "ALERT"
        elif dist <= safe:
            status = "WARNING"
        else:
            status = "SAFE"

        vehicles.append({
            "id": i+1,
            "distance": round(dist,2),
            "status": status
        })

        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow(
                [datetime.now(), f"Vehicle-{i+1}", round(dist,2), status]
            )

    return jsonify(vehicles)

@app.route("/logs/<system>")
def logs(system):
    values = []
    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[1].startswith(system):
                values.append(row[2])
    return jsonify(values)

if __name__ == "__main__":
    app.run(debug=True)
