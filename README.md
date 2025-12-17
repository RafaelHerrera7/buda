# Portfolio Valuation — Resumen Rápido

API mínima para calcular el valor total de un portafolio de criptomonedas en una moneda fiat.

---

## Enlace útil
- Local: http://localhost:8000
- Producción: https://buda-production.up.railway.app

---

## Notas importantes
- Proyecto **prueba** (1.5 horas). Se omitieron medidas de seguridad (autenticación, rate limiting, logs persistentes, etc.).
- No usar en producción sin añadir seguridad, monitoreo y validación avanzada.

---

## Endpoints principales

- GET / → Health check (200)
- POST /v1/portfolio/value → Calcula valor total
  - Request body: {"portfolio": {"BTC": 0.5}, "fiat_currency": "CLP"}
  - Success (200): {"portfolio_value": 46312554.0, "fiat_currency": "CLP"}
  - 400: Par no soportado / input inválido
  - 404: Par no encontrado en Buda
  - 503/504: Error externo (Buda) — servicio caído o timeout

---

## Ejemplo rápido

```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 0.5, "ETH": 2}, "fiat_currency": "CLP"}'
```

---

## Comportamiento clave
- Cache en memoria con TTL 30s (reduce llamadas a Buda.com).
- Validación temprana de pares (evita llamadas innecesarias).
- Errores de Buda se normalizan a `BudaAPIError` con códigos HTTP.

---

## Desarrollo y pruebas
- Ejecutar locally:
  - `python main.py` (uvicorn) o `uvicorn main:app --reload`
- Tests: `pytest -q`
- Docker: `docker build -t portfolio-api .` y `docker run -p 8000:8000 portfolio-api`

---

## Limitaciones
- Pares limitados (ver `config/constants.py`).
- Caché por proceso (no compartido entre réplicas).

---


### Error: "Invalid pair"
- Verificar que cripto y fiat están en VALID_PAIRS
- Verificar combinación es válida

---

## Versión

- **API Version:** 1.0
- **Base URL:** `/v1/`
- **Última actualización:** Diciembre 2025
