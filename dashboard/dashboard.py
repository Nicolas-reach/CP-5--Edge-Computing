from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# ===== CREDENCIAIS RAILWAY =====
STH_URL      = "https://sth-comet-production.up.railway.app"
SERVICE      = "vinheria"
SERVICE_PATH = "/"
ENTITY_ID    = "Vinheria:esp32_001"
ENTITY_TYPE  = "Vinheria"
HEADERS      = {"fiware-service": SERVICE, "fiware-servicepath": SERVICE_PATH}

THRESHOLDS = {
    "temperature": {"min": 10, "max": 15},
    "humidity":    {"min": 50, "max": 100},
    "luminosity":  {"min": 0,  "max": 300}
}

def get_historico(atributo, limite=20):
    url = (f"{STH_URL}/STH/v1/contextEntities/type/{ENTITY_TYPE}"
           f"/id/{ENTITY_ID}/attributes/{atributo}"
           f"?hLimit={limite}&hOffset=0&dateFrom=2000-01-01T00:00:00.000Z")
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        valores = r.json()["contextResponses"][0]["contextElement"]["attributes"][0]["values"]
        return [{"time": v["recvTime"], "value": v["attrValue"]} for v in valores]
    except Exception as e:
        print(f"Erro ao buscar {atributo}: {e}")
        return []

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/dados")
def dados():
    temp = get_historico("temperature")
    umid = get_historico("humidity")
    lux  = get_historico("luminosity")
    alertas = []
    
    for nome, lista in [("temperature",temp),("humidity",umid),("luminosity",lux)]:
        if lista:
            v = lista[-1]["value"]
            t = THRESHOLDS[nome]
            if v < t["min"] or v > t["max"]:
                alertas.append(f"⚠️ {nome.upper()}: {v} fora do range [{t['min']} – {t['max']}]")
    
    return jsonify({"temperature":temp,"humidity":umid,"luminosity":lux,"alertas":alertas,"updated":datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Vinheria IoT</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:Arial;background:#1a1a2e;color:#eee}
    header{background:#16213e;padding:20px;text-align:center}
    header h1{color:#e94560;font-size:2em}
    .cards{display:flex;gap:20px;padding:20px;justify-content:center;flex-wrap:wrap}
    .card{background:#16213e;padding:20px;border-radius:8px;min-width:150px;text-align:center}
    .card .valor{font-size:2em;font-weight:bold}
    .temp .valor{color:#ff6b6b}
    .umid .valor{color:#4ecdc4}
    .lux .valor{color:#ffe66d}
    .charts{display:flex;gap:20px;padding:20px;flex-wrap:wrap}
    .chart-box{background:#16213e;padding:20px;border-radius:8px;flex:1;min-width:300px}
    .alertas{background:#16213e;padding:20px;margin:20px;border-radius:8px}
  </style>
</head>
<body>
  <header><h1>Vinheria IoT Dashboard</h1></header>
  <div class="cards">
    <div class="card temp"><h3>Temperatura</h3><div class="valor" id="vt">--</div><small>C</small></div>
    <div class="card umid"><h3>Umidade</h3><div class="valor" id="vu">--</div><small>%</small></div>
    <div class="card lux"><h3>Luminosidade</h3><div class="valor" id="vl">--</div><small>lux</small></div>
  </div>
  <div class="alertas"><h3>Alertas</h3><div id="alertas-box">Aguardando dados...</div></div>
  <div class="charts">
    <div class="chart-box"><h3>Temperatura</h3><canvas id="ct"></canvas></div>
    <div class="chart-box"><h3>Umidade</h3><canvas id="cu"></canvas></div>
    <div class="chart-box"><h3>Luminosidade</h3><canvas id="cl"></canvas></div>
  </div>
<script>
const mk=(id,color)=>new Chart(document.getElementById(id),{type:'line',data:{labels:[],datasets:[{data:[],borderColor:color,backgroundColor:color+'22',tension:.4,fill:true}]},options:{responsive:true,plugins:{legend:{display:false}}}});
const C={t:mk('ct','#ff6b6b'),u:mk('cu','#4ecdc4'),l:mk('cl','#ffe66d')};
const upd=(c,d)=>{c.data.labels=d.map(x=>new Date(x.time).toLocaleTimeString());c.data.datasets[0].data=d.map(x=>x.value);c.update()};
async function refresh(){const d=await(await fetch('/api/dados')).json();const last=a=>a.length?a[a.length-1].value:'--';document.getElementById('vt').textContent=last(d.temperature);document.getElementById('vu').textContent=last(d.humidity);document.getElementById('vl').textContent=last(d.luminosity);upd(C.t,d.temperature);upd(C.u,d.humidity);upd(C.l,d.luminosity);const box=document.getElementById('alertas-box');box.innerHTML=d.alertas.length?d.alertas.map(a=>'<div>'+a+'</div>').join(''):'OK';}
refresh();setInterval(refresh,10000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
