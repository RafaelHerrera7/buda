# Documentación API - Portfolio Valuation

API REST para calcular el valor total de un portafolio de criptomonedas en moneda fiat.

---

## ⚠️ Nota de Seguridad

Esta API es una **prueba de concepto**. Se han saltado varios pasos de seguridad en producción:
-  Sin autenticación/autorización
-  Sin rate limiting
-  Sin validación avanzada de CORS
-  Sin logs persistentes
-  Sin monitoreo en tiempo real

**No usar en ambiente de producción real sin implementar estas medidas.**

---

## Base URL

**Desarrollo:**
```
http://localhost:8000
```

**Producción:**
```
https://buda-production.up.railway.app
```

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /`

Verifica que el servidor está activo.

**Response (200 OK):**
```json
{
  "Hello": "Hello Buda!"
}
```

---

### 2. Calcular Valor de Portafolio

**Endpoint:** `POST /v1/portfolio/value`

Calcula el valor total de un portafolio de criptomonedas en una moneda fiat específica.

---

## Request

**Content-Type:** `application/json`

**Body:**
```json
{
  "portfolio": {
    "BTC": 0.5,
    "ETH": 2.0,
    "USDT": 1000
  },
  "fiat_currency": "CLP"
}
```

### Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `portfolio` | Object | Sí | Objeto con pares cripto:cantidad |
| `fiat_currency` | String | Sí | Moneda fiat destino (CLP, COP, PEN, etc.) |

### Criptomonedas Soportadas

- **BTC** → CLP, COP, PEN
- **ETH** → CLP, COP, PEN
- **BCH** → CLP, COP, PEN
- **LTC** → CLP, COP, PEN
- **USDC** → CLP, COP, PEN
- **USDT** → CLP, COP, PEN 

---

## Response

### Success (200 OK)

```json
{
  "portfolio_value": 46312554.0,
  "fiat_currency": "CLP"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `portfolio_value` | Float | Valor total del portafolio |
| `fiat_currency` | String | Moneda utilizada |

---

## Códigos de Error

### 400 Bad Request

**Cuando:** Criptomoneda o par no soportado

**Response:**
```json
{
  "detail": "Buda API Error (400): Par BTC-USD no soportado"
}
```

**Casos:**
- Criptomoneda no existe en VALID_PAIRS
- Par cripto-fiat no es válido
- Estructura JSON inválida

---

### 404 Not Found

**Cuando:** El par no existe en Buda.com

**Response:**
```json
{
  "detail": "Buda API Error (404): Par BTC-INVALID no encontrado"
}
```

---

### 500 Internal Server Error

**Cuando:** Precio con formato inválido o error de conexión

**Response:**
```json
{
  "detail": "Buda API Error (500): Error de conexión o formato inválido"
}
```

---

## Ejemplos

### Ejemplo 1: Portafolio Básico (BTC en CLP)

**Request:**
```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {"BTC": 1.0},
    "fiat_currency": "CLP"
  }'
```

**Response:**
```json
{
  "portfolio_value": 46312554.36,
  "fiat_currency": "CLP"
}
```

---

### Ejemplo 2: Múltiples Criptomonedas

**Request:**
```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {
      "BTC": 0.5,
      "ETH": 10.0,
      "USDT": 5000
    },
    "fiat_currency": "CLP"
  }'
```

**Response:**
```json
{
  "portfolio_value": 38000000.50,
  "fiat_currency": "CLP"
}
```

---

### Ejemplo 3: Moneda Fiat Diferente (COP)

**Request:**
```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {"BTC": 0.1},
    "fiat_currency": "COP"
  }'
```

**Response:**
```json
{
  "portfolio_value": 234000000.0,
  "fiat_currency": "COP"
}
```

---

### Ejemplo 4: Error - Criptomoneda Inválida

**Request:**
```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {"XYZ": 1.0},
    "fiat_currency": "CLP"
  }'
```

**Response (400):**
```json
{
  "detail": "Buda API Error (400): XYZ no es una criptomoneda válida"
}
```

---

### Ejemplo 5: Error - Par No Soportado

**Request:**
```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {"BTC": 1.0},
    "fiat_currency": "USD"
  }'
```

**Response (400):**
```json
{
  "detail": "Buda API Error (400): Par BTC-USD no soportado"
}
```

---

## Comportamiento del Cache

El sistema utiliza caché en memoria con **TTL de 30 segundos**.

### Console Output

Cada llamada imprime el estado:

```
[API] Llamada a BTC-CLP        # Primera llamada → consulta API
[CACHE] Usando datos cacheados para ETH-CLP   # Segunda llamada dentro de 30s
[API] Llamada a BTC-COP        # 30s después o par diferente → consulta API
```

### Ventajas

- Reduce carga en API de Buda.com
- Mejora latencia de respuesta
- Automático y transparente

---

## Casos de Uso

### 1. Valor Total del Portafolio

Calcular patrimonio neto en moneda local.

```bash
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {
      "BTC": 0.5,
      "ETH": 5.0,
      "USDT": 10000
    },
    "fiat_currency": "CLP"
  }'
```

---

### 2. Monitoreo de Precio

Seguimiento de cambios de precio en tiempo real.

```bash
# Primer llamado
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 1}, "fiat_currency": "CLP"}'

# Después de 30 segundos
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 1}, "fiat_currency": "CLP"}'
```

---

### 3. Comparación de Monedas Fiat

Valor del mismo portafolio en diferentes monedas.

```bash
# En CLP
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 1}, "fiat_currency": "CLP"}'

# En COP
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 1}, "fiat_currency": "COP"}'

# En PEN
curl -X POST http://localhost:8000/v1/portfolio/value \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"BTC": 1}, "fiat_currency": "PEN"}'
```

---

## Validación de Input

### Portfolio

- **Tipo:** Objeto con pares string:float
- **Valores permitidos:** Cualquier número (positivo, negativo, cero)
- **Ejemplo válido:** `{"BTC": 0.5, "ETH": -2.0, "USDT": 1000}`

### Fiat Currency

- **Tipo:** String (case-insensitive)
- **Valores permitidos:** CLP, COP, PEN, USDC, BTC
- **Ejemplo válido:** `"CLP"`, `"clp"`, `"Clp"`

---

## Performance

| Métrica | Valor |
|---------|-------|
| Timeout | 5 segundos |
| Cache TTL | 30 segundos |
| Máximo reintentos | 0 (sin reintentos) |
| Compresión | No |

---

## Limitaciones

1. **Pares limitados:** Solo los pares en VALID_PAIRS son soportados
2. **Monedas limitadas:** Solo criptomonedas y fiats en los mapeos
3. **Sin autenticación:** API pública, sin restricción de rate limiting
4. **Dependencia externa:** Requiere conexión a Buda.com

---

## Troubleshooting

### Error: "Connection refused"
- Verificar que el servidor está corriendo
- Verificar puerto 8000

### Error: "Timeout"
- API de Buda.com puede estar lento
- Reintentar en unos segundos

### Error: "Invalid pair"
- Verificar que cripto y fiat están en VALID_PAIRS
- Verificar combinación es válida

---

## Versión

- **API Version:** 1.0
- **Base URL:** `/v1/`
- **Última actualización:** Diciembre 2025
