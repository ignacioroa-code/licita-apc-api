# LicitaAPC API

Servidor backend para conectar LicitaAPC con la API oficial de Mercado Público.

## Endpoints

- `GET /` — Estado del servicio
- `GET /licitaciones` — Licitaciones activas del día
- `GET /licitaciones?fecha=02102026` — Licitaciones por fecha (ddmmaaaa)
- `GET /buscar?q=personal+externo` — Buscar por término
- `GET /licitacion/1234-56-LE26` — Detalle de una licitación
- `GET /health` — Health check

## Deploy en Railway

1. Sube este repositorio a GitHub
2. Entra a railway.app y conecta el repo
3. Railway detecta Python y despliega automáticamente
