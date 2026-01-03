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
            let colors = d.statuses.map(s =>
                s === "TOO COLD" ? "blue" :
                s === "NORMAL" ? "green" :
                s === "WARNING" ? "orange" : "red"
            );

            Plotly.newPlot("tempGraph", [{
                x: d.values.map((_, i) => i),
                y: d.values,
                mode: "lines+markers",
                line: { width: 3 },
                marker: { size: 8, color: colors }
            }], { title: "Temperature Trend" });
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
                out += `<li class="${v.status === "ALERT" ? "alert" :
                                   v.status === "WARNING" ? "warning" : "normal"}">
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
            let colors = d.statuses.map(s =>
                s === "ALERT" ? "red" :
                s === "WARNING" ? "orange" : "green"
            );

            Plotly.newPlot("vehicleGraph", [{
                x: d.values.map((_, i) => i),
                y: d.values,
                mode: "lines+markers",
                line: { width: 2 },
                marker: { size: 8, color: colors }
            }], { title: "Vehicle Distance Trend" });
        });
}

showSection("home");
