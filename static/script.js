let tempAuto = false, tempInterval = null;
let vehicleAuto = false, vehicleInterval = null;

function showSection(sec) {
    ["home", "temperature", "vehicle"].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    });
    document.getElementById(sec).classList.remove("hidden");
}

// ---------- TEMPERATURE ----------
function readTemp() {
    let t = document.getElementById("tempThreshold").value;

    fetch(`/temperature?threshold=${t}`)
        .then(r => r.json())
        .then(d => {
            document.getElementById("tempValue").innerText = d.value;

            let s = document.getElementById("tempStatus");
            s.innerText = d.status;

            s.className =
                d.status === "TOO COLD" ? "status cold" :
                d.status === "ALERT" ? "status alert" :
                d.status === "WARNING" ? "status warning" :
                "status normal";

            updateTempGraph();
        });
}

function toggleTempAuto() {
    if (tempInterval) clearInterval(tempInterval);
    tempAuto = !tempAuto;
    if (tempAuto) tempInterval = setInterval(readTemp, 2000);
}

function updateTempGraph() {
    fetch("/logs/Temperature")
        .then(r => r.json())
        .then(d => {

            let traces = [];
            let x = d.values.map((_, i) => i);

            let colorMap = {
                "TOO COLD": "blue",
                "NORMAL": "green",
                "WARNING": "orange",
                "ALERT": "red"
            };

            for (let i = 0; i < d.values.length; i++) {
                let color = colorMap[d.statuses[i]];

                // dot
                traces.push({
                    x: [x[i]],
                    y: [d.values[i]],
                    mode: "markers",
                    marker: { color: color, size: 8 },
                    showlegend: false
                });

                // line segment
                if (i > 0) {
                    traces.push({
                        x: [x[i - 1], x[i]],
                        y: [d.values[i - 1], d.values[i]],
                        mode: "lines",
                        line: { color: color, width: 3 },
                        showlegend: false
                    });
                }
            }

            Plotly.newPlot("tempGraph", traces, {
                title: "Temperature",
                margin: { t: 40 }
            });
        });
}

// ---------- VEHICLE ----------
function scanVehicle() {
    let s = document.getElementById("safeDistance").value;

    fetch(`/vehicle?safe=${s}`)
        .then(r => r.json())
        .then(d => {
            let out = "<ul>";

            d.forEach(v => {
                out += `<li class="${
                    v.status === "ALERT" ? "alert" :
                    v.status === "WARNING" ? "warning" : "normal"
                }">
                    Vehicle ${v.id}: ${v.distance} cm (${v.status})
                </li>`;
            });

            out += "</ul>";
            document.getElementById("vehicleOutput").innerHTML = out;

            updateVehicleGraph();
        });
}

function toggleVehicleAuto() {
    if (vehicleInterval) clearInterval(vehicleInterval);
    vehicleAuto = !vehicleAuto;
    if (vehicleAuto) vehicleInterval = setInterval(scanVehicle, 1500);
}

function updateVehicleGraph() {
    fetch("/logs/Vehicle")
        .then(r => r.json())
        .then(d => {

            let traces = [];
            let x = d.values.map((_, i) => i);

            let colorMap = {
                "NORMAL": "green",
                "WARNING": "orange",
                "ALERT": "red"
            };

            for (let i = 0; i < d.values.length; i++) {
                let color = colorMap[d.statuses[i]];

                // dot
                traces.push({
                    x: [x[i]],
                    y: [d.values[i]],
                    mode: "markers",
                    marker: { color: color, size: 8 },
                    showlegend: false
                });

                // line segment
                if (i > 0) {
                    traces.push({
                        x: [x[i - 1], x[i]],
                        y: [d.values[i - 1], d.values[i]],
                        mode: "lines",
                        line: { color: color, width: 2 },
                        showlegend: false
                    });
                }
            }

            Plotly.newPlot("vehicleGraph", traces, {
                title: "Vehicle Distance",
                margin: { t: 40 }
            });
        });
}

showSection("home");