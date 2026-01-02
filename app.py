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

# --------- STATE ----------
temperature = 36.0
temp_direction = 1

# --------- CONSTANTS ----------
MIN_SAFE_TEMP = 22       # below this, TOO COLD
MAX_REALISTIC_TEMP = 60  # realistic max temp
MIN_REALISTIC_TEMP = -10 # realistic min temp

# --------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/temperature")
def temperature_api():
    global temperature

    # Get user threshold
    try:
        threshold = float(request.args.get("threshold", 45))
    except:
        threshold = 45

    # Clamp threshold within realistic limits
    threshold = max(36, min(threshold, MAX_REALISTIC_TEMP))

    # Simulate realistic temperature fluctuation (+/-1.5°C per reading)
    temperature += random.uniform(-1.5, 1.5)
    temperature = max(MIN_REALISTIC_TEMP, min(temperature, MAX_REALISTIC_TEMP))

    # Determine status
    if temperature < MIN_SAFE_TEMP:
        status = "TOO COLD"
    elif temperature < 36:
        status = "NORMAL"
    elif temperature <= threshold:
        status = "WARNING"
    else:
        status = "ALERT"

    # Log to CSV
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([datetime.now(), "Temperature", round(temperature,2), status])

    return jsonify({"value": round(temperature,2), "status": status})

@app.route("/vehicle")
def vehicle_api():
    try:
        safe = float(request.args.get("safe", 20))
    except:
        safe = 20

    SAFE_MIN = 10
    SAFE_MAX = 150
    safe = max(SAFE_MIN, min(safe, SAFE_MAX))

    vehicles = []
    for i in range(random.randint(1,4)):
        dist = random.uniform(5, 150)
        if dist < SAFE_MIN:
            status = "ALERT"
        elif dist <= safe:
            status = "WARNING"
        else:
            status = "SAFE"

        vehicles.append({"id": i+1, "distance": round(dist,2), "status": status})

        # Log to CSV
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([datetime.now(), f"Vehicle-{i+1}", round(dist,2), status])

    return jsonify(vehicles)

@app.route("/logs/<system>")
def logs(system):
    values, statuses = [], []
    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[1].startswith(system):
                values.append(float(row[2]))
                statuses.append(row[3])
    return jsonify({"values": values, "statuses": statuses})

if __name__ == "__main__":
    app.run(debug=True)
