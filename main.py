from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)

# Permitir CORS desde cualquier origen (incluyendo claude.ai)
CORS(app, origins="*", methods=["GET","POST","OPTIONS"], 
     allow_headers=["Content-Type","Authorization","Accept"])

TICKET = "E617551C-3BAB-439A-8048-5BAC2A0202A8"
BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico"

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
    return response

@app.route("/")
def index():
    return jsonify({
        "servicio": "LicitaAPC API",
        "empresa": "Advance APC",
        "estado": "activo",
        "version": "1.1"
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/licitaciones")
def licitaciones():
    hoy = datetime.now()
    fecha = request.args.get("fecha", hoy.strftime("%d%m%Y"))
    estado = request.args.get("estado", "activas")
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {"ticket": TICKET, "estado": estado, "fecha": fecha}
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        return jsonify({
            "ok": True,
            "fecha": fecha,
            "cantidad": data.get("Cantidad", len(listado)),
            "listado": listado
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "listado": []}), 500

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    fecha = request.args.get("fecha", datetime.now().strftime("%d%m%Y"))
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {"ticket": TICKET, "estado": "activas", "fecha": fecha}
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        if q:
            q_lower = q.lower()
            listado = [l for l in listado if
                q_lower in (l.get("Nombre","") or "").lower() or
                q_lower in (l.get("Descripcion","") or "").lower()]
        return jsonify({
            "ok": True,
            "fecha": fecha,
            "termino": q,
            "cantidad": len(listado),
            "listado": listado
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "listado": []}), 500

@app.route("/licitacion/<codigo>")
def detalle(codigo):
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {"ticket": TICKET, "codigo": codigo}
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        return jsonify({"ok": True, "licitacion": listado[0] if listado else None})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
