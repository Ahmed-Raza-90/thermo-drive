from flask import Flask, render_template, jsonify, request
import csv, random, math
from datetime import datetime

app = Flask(__name__)
log_file = "system_log.csv"

# Ensure CSV header exists
try:
    with open(log_file, "r") as f:
        pass
except:
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "System", "Value", "Status"])

# ----------------- Pages -----------------
@app.route("/")
def home():
    return render_template("temperature.html")

@app.route("/temperature")
def temperature_page():
    return render_template("temperature.html")

@app.route("/vehicle")
def vehicle_page():
    return render_template("vehicle.html")

@app.route("/graphs")
def graphs_page():
    return render_template("graphs.html")

# ----------------- Temperature Simulation -----------------
temp_current = 25.0
temp_direction = 1  # 1: heating, -1: cooling

@app.route("/read_temperature")
def read_temperature():
    global temp_current, temp_direction
    threshold = float(request.args.get("threshold", 40))

    # Realistic fluctuation
    change = random.uniform(0.2, 0.8) * temp_direction
    temp_current += change

    # Reverse direction if hitting bounds
    if temp_current >= 60: temp_direction = -1
    if temp_current <= 20: temp_direction = 1

    # Status logic
    if temp_current < 36:
        status = "NORMAL"
    elif 36 <= temp_current <= threshold:
        status = "WARNING"
    else:
        status = "ALERT"

    # Log
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), "Temperature", round(temp_current,2), status])

    return jsonify({"value": round(temp_current,2), "status": status})

# ----------------- Vehicle Simulation -----------------
@app.route("/scan_vehicle")
def scan_vehicle():
    safe = int(request.args.get("safe", 20))
    num_vehicles = random.randint(1,5)
    vehicles = []

    for i in range(num_vehicles):
        # realistic distance between 5–150cm
        dist = random.uniform(5, 150)
        if dist < 10: status="ALERT"
        elif dist <= safe: status="WARNING"
        else: status="SAFE"
        vehicles.append({"vehicle_id": i+1, "distance": round(dist,2), "status": status})
        # Log each vehicle
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), f"Vehicle-{i+1}", round(dist,2), status])

    return jsonify(vehicles)

# ----------------- Logs for Graphs -----------------
@app.route("/get_logs/<system>")
def get_logs(system):
    times, values, statuses = [], [], []
    try:
        with open(log_file,"r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row[1].startswith(system):
                    times.append(row[0])
                    values.append(float(row[2]))
                    statuses.append(row[3])
    except:
        pass
    return jsonify({"times": times, "values": values, "statuses": statuses})

@app.route("/latest_logs")
def latest_logs():
    rows=[]
    try:
        with open(log_file,"r") as f:
            reader = list(csv.reader(f))
            for row in reader[-20:]:
                rows.append(row)
    except:
        pass
    return jsonify(rows)

if __name__=="__main__":
    app.run(debug=True)
