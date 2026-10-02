from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite llamadas desde el dashboard LicitaAPC

TICKET = "E617551C-3BAB-439A-8048-5BAC2A0202A8"
BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico"

@app.route("/")
def index():
    return jsonify({
        "servicio": "LicitaAPC API",
        "empresa": "Advance APC",
        "estado": "activo",
        "version": "1.0"
    })

@app.route("/licitaciones")
def licitaciones():
    """Busca licitaciones activas del día en Mercado Público"""
    hoy = datetime.now()
    fecha = request.args.get("fecha", hoy.strftime("%d%m%Y"))
    estado = request.args.get("estado", "activas")
    
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {
            "ticket": TICKET,
            "estado": estado,
            "fecha": fecha
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        listado = data.get("Listado", [])
        cantidad = data.get("Cantidad", 0)
        
        return jsonify({
            "ok": True,
            "fecha": fecha,
            "cantidad": cantidad,
            "listado": listado
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/licitacion/<codigo>")
def detalle_licitacion(codigo):
    """Obtiene el detalle completo de una licitación por código"""
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {"ticket": TICKET, "codigo": codigo}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        return jsonify({
            "ok": True,
            "licitacion": listado[0] if listado else None
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/buscar")
def buscar():
    """Busca licitaciones por palabra clave"""
    q = request.args.get("q", "")
    fecha = request.args.get("fecha", datetime.now().strftime("%d%m%Y"))
    
    # Términos clave APC
    TERMINOS_APC = [
        "personal externo", "outsourcing", "suministro de personal",
        "dotación de personal", "TENS", "enfermería", "EPP",
        "vestuario trabajo", "calzado seguridad", "artículos de oficina",
        "elementos de escritorio", "economato"
    ]
    terminos = [q] if q else TERMINOS_APC

    # Buscar licitaciones activas del día
    try:
        url = f"{BASE_URL}/licitaciones.json"
        params = {"ticket": TICKET, "estado": "activas", "fecha": fecha}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    # Filtrar por términos
    if q:
        q_lower = q.lower()
        listado = [l for l in listado if
            q_lower in (l.get("Nombre","") or "").lower() or
            q_lower in (l.get("Descripcion","") or "").lower()
        ]

    return jsonify({
        "ok": True,
        "fecha": fecha,
        "terminos": terminos,
        "cantidad": len(listado),
        "listado": listado
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
