# API de Detección de Fraude - Guía de Uso

Guía completa para interactuar con la API de detección de fraude desplegada, ejecutar inferencias y entender los requisitos de datos.

---

## Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Endpoints de la API](#endpoints-de-la-api)
3. [Ejecutando Inferencia](#ejecutando-inferencia)
4. [Requisitos de Datos](#requisitos-de-datos)
5. [Formato de Respuesta](#formato-de-respuesta)
6. [Manejo de Errores](#manejo-de-errores)
7. [Ejemplos](#ejemplos)
8. [Mejores Prácticas](#mejores-prácticas)
9. [Solución de Problemas](#solución-de-problemas)

---

## Inicio Rápido

### Accediendo a la API

**URL de Producción**: `https://fraud-detection-api-[your-app-id].ondigitalocean.app`

**Desarrollo Local**: `http://localhost:8000`

**Documentación Interactiva**: Visite `/docs` para Swagger UI o `/redoc` para ReDoc

```bash
# Verificar salud de la API
curl https://your-app-url.ondigitalocean.app/health

# Obtener documentación interactiva
open https://your-app-url.ondigitalocean.app/docs
```

---

## Endpoints de la API

### 1. Endpoint Raíz

**GET** `/`

Devuelve información básica de la API.

```bash
curl https://your-app-url.ondigitalocean.app/
```

**Respuesta:**
```json
{
  "message": "Fraud Detection API",
  "version": "1.1.0",
  "docs": "/docs"
}
```

---

### 2. Verificación de Salud

**GET** `/health`

Verifica el estado de la API y la disponibilidad del modelo.

```bash
curl https://your-app-url.ondigitalocean.app/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_loaded": true,
  "version": "1.1.0",
  "uptime_seconds": 3600.5
}
```

**Valores de Estado:**
- `healthy` - La API está operativa y el modelo está cargado
- `unhealthy` - La API se está ejecutando pero el modelo falló al cargar

---

### 3. Transacción de Muestra

**GET** `/sample-transaction`

Obtiene una transacción de muestra con todos los campos requeridos poblados.

```bash
curl https://your-app-url.ondigitalocean.app/sample-transaction
```

**Respuesta:**
```json
{
  "transaction_id": "txn_159662",
  "user_id": "user_03471",
  "device_id": "device_01026",
  "amount": 29.07,
  "merchant_category": "online",
  "transaction_type": "transfer",
  "location": "denver_co",
  "device_type": "mobile",
  "hour_of_day": 6,
  "day_of_week": 2,
  "user_transaction_frequency": 18.40,
  "user_avg_amount": 169.94,
  "user_transaction_count": 60,
  "timestamp": "2025-11-16T04:46:25.359813"
}
```

**Caso de Uso:** Use este endpoint para entender la estructura de datos esperada y probar la API.

---

### 4. Predicción de Fraude

**POST** `/predict`

Envía una transacción para detección de fraude.

```bash
curl -X POST https://your-app-url.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d @transaction.json
```

**Respuesta:**
```json
{
  "fraud_probability": 0.0234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_a1b2c3d4e5f6",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_version": "models/random_forest_final_model.joblib",
  "processing_time_ms": 45.2
}
```

---

## Ejecutando Inferencia

### Campos Requeridos

Cada solicitud de predicción **debe** incluir estos campos:

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `amount` | float | Monto de la transacción (debe ser > 0) | `150.50` |
| `merchant_category` | string | Categoría del comerciante | `"grocery"`, `"online"`, `"retail"` |
| `transaction_type` | string | Tipo de transacción | `"purchase"`, `"transfer"`, `"withdrawal"` |
| `location` | string | Ubicación de la transacción | `"new_york_ny"`, `"denver_co"` |
| `device_type` | string | Dispositivo usado para la transacción | `"mobile"`, `"desktop"`, `"atm"` |
| `hour_of_day` | integer | Hora (0-23) | `14` |
| `day_of_week` | integer | Día de la semana (0-6, Lunes=0) | `2` |

### Campos Opcionales (Recomendado)

Estos campos mejoran la precisión de la predicción proporcionando contexto del usuario:

| Campo | Tipo | Descripción | Por Defecto |
|-------|------|-------------|---------|
| `user_id` | string | Identificador de usuario | `"anonymous_user"` |
| `transaction_id` | string | Identificador de transacción | Auto-generado |
| `timestamp` | string | Marca de tiempo ISO | Hora UTC actual |
| `device_id` | string | Identificador de dispositivo | `"device_{user_id}"` |
| `user_transaction_frequency` | float | Transacciones por día | `0.0` |
| `user_avg_amount` | float | Monto promedio de transacción | Igual a `amount` |
| `user_transaction_count` | integer | Total de transacciones del usuario | `1` |

### Ejemplo Completo

```json
{
  "amount": 250.75,
  "merchant_category": "electronics",
  "transaction_type": "purchase",
  "location": "san_francisco_ca",
  "device_type": "desktop",
  "hour_of_day": 14,
  "day_of_week": 3,
  "user_id": "user_12345",
  "transaction_id": "txn_abc123",
  "timestamp": "2025-12-12T14:30:00Z",
  "device_id": "device_xyz789",
  "user_transaction_frequency": 5.2,
  "user_avg_amount": 125.50,
  "user_transaction_count": 47
}
```

### Ejemplo Mínimo

```json
{
  "amount": 250.75,
  "merchant_category": "electronics",
  "transaction_type": "purchase",
  "location": "san_francisco_ca",
  "device_type": "desktop",
  "hour_of_day": 14,
  "day_of_week": 3
}
```

**Nota:** Los ejemplos mínimos funcionan pero pueden producir predicciones menos precisas debido a la falta de contexto del usuario.

---

## Requisitos de Datos

### Restricciones de Campos

#### Amount (Monto)
- Debe ser mayor que 0
- Tipo: `float`
- Ejemplo: `150.50`, `1000.00`, `25.99`

#### Merchant Category (Categoría de Comerciante)
- Cadena no vacía
- Valores comunes: `"grocery"`, `"online"`, `"retail"`, `"restaurant"`, `"gas_station"`, `"electronics"`, `"entertainment"`, `"travel"`, `"healthcare"`, `"utilities"`
- El modelo acepta cualquier cadena pero fue entrenado en estas categorías

#### Transaction Type (Tipo de Transacción)
- Cadena no vacía
- Valores comunes: `"purchase"`, `"transfer"`, `"withdrawal"`, `"deposit"`, `"payment"`
- El modelo acepta cualquier cadena pero fue entrenado en estos tipos

#### Location (Ubicación)
- Cadena no vacía
- Formato: `"city_state"` (minúsculas, guiones bajos)
- Ejemplos: `"new_york_ny"`, `"los_angeles_ca"`, `"chicago_il"`, `"houston_tx"`, `"denver_co"`

#### Device Type (Tipo de Dispositivo)
- Cadena no vacía
- Valores válidos: `"mobile"`, `"desktop"`, `"atm"`

#### Hour of Day (Hora del Día)
- Entero entre 0 y 23
- 0 = medianoche, 12 = mediodía, 23 = 11 PM

#### Day of Week (Día de la Semana)
- Entero entre 0 y 6
- 0 = Lunes, 1 = Martes, ..., 6 = Domingo

---

## Formato de Respuesta

### Respuesta Exitosa

```json
{
  "fraud_probability": 0.0234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_a1b2c3d4e5f6",
  "timestamp": "2025-12-12T10:00:00.000000",
  "model_version": "models/random_forest_final_model.joblib",
  "processing_time_ms": 45.2
}
```

**Descripciones de Campos:**

- `fraud_probability` (float): Probabilidad de fraude (0.0 a 1.0)
- `is_fraud` (boolean): Clasificación binaria de fraude
  - `true` si `fraud_probability >= 0.5`
  - `false` si `fraud_probability < 0.5`
- `risk_level` (string): Evaluación de riesgo
  - `"low"` - probabilidad < 0.3
  - `"medium"` - probabilidad 0.3 a 0.7
  - `"high"` - probabilidad > 0.7
- `prediction_id` (string): Identificador único para esta predicción
- `timestamp` (string): Cuándo se realizó la predicción
- `model_version` (string): Identificador del modelo
- `processing_time_ms` (float): Latencia de inferencia en milisegundos

---

## Manejo de Errores

### Errores de Validación (422)

Cuando faltan campos requeridos o son inválidos:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "amount"],
      "msg": "Field required",
      "input": {...},
      "url": "https://errors.pydantic.dev/2.0.3/v/missing"
    }
  ]
}
```

**Errores de Validación Comunes:**
- Faltan campos requeridos
- Tipos de datos inválidos (ej., cadena en lugar de número)
- Valores fuera de rango (ej., `hour_of_day = 25`)
- Montos negativos

### Errores del Servidor (500)

```json
{
  "detail": "Internal server error"
}
```

**Causas Comunes:**
- El modelo no se cargó correctamente
- Falla en ingeniería de características
- Formato de datos inesperado

---

## Ejemplos

### Ejemplo 1: Python con requests

```python
import requests
import json

# Endpoint de API
url = "https://your-app-url.ondigitalocean.app/predict"

# Datos de transacción
transaction = {
    "amount": 500.00,
    "merchant_category": "electronics",
    "transaction_type": "purchase",
    "location": "new_york_ny",
    "device_type": "mobile",
    "hour_of_day": 18,
    "day_of_week": 4,
    "user_id": "user_42",
    "user_transaction_frequency": 8.5,
    "user_avg_amount": 200.00,
    "user_transaction_count": 120
}

# Hacer solicitud de predicción
response = requests.post(url, json=transaction)

# Verificar respuesta
if response.status_code == 200:
    result = response.json()
    print(f"Fraud Probability: {result['fraud_probability']:.2%}")
    print(f"Is Fraud: {result['is_fraud']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Ejemplo 2: cURL

```bash
curl -X POST https://your-app-url.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "merchant_category": "electronics",
    "transaction_type": "purchase",
    "location": "new_york_ny",
    "device_type": "mobile",
    "hour_of_day": 18,
    "day_of_week": 4,
    "user_id": "user_42",
    "user_transaction_frequency": 8.5,
    "user_avg_amount": 200.00,
    "user_transaction_count": 120
  }'
```

### Ejemplo 3: JavaScript/Node.js

```javascript
const axios = require('axios');

const transaction = {
  amount: 500.00,
  merchant_category: "electronics",
  transaction_type: "purchase",
  location: "new_york_ny",
  device_type: "mobile",
  hour_of_day: 18,
  day_of_week": 4,
  user_id: "user_42",
  user_transaction_frequency: 8.5,
  user_avg_amount: 200.00,
  user_transaction_count: 120
};

axios.post('https://your-app-url.ondigitalocean.app/predict', transaction)
  .then(response => {
    const result = response.data;
    console.log(`Fraud Probability: ${(result.fraud_probability * 100).toFixed(2)}%`);
    console.log(`Is Fraud: ${result.is_fraud}`);
    console.log(`Risk Level: ${result.risk_level}`);
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### Ejemplo 4: Procesamiento por Lotes

```python
import requests
import pandas as pd

# Cargar transacciones desde CSV
transactions = pd.read_csv('transactions.csv')

# Endpoint de API
url = "https://your-app-url.ondigitalocean.app/predict"

# Procesar cada transacción
results = []
for _, row in transactions.iterrows():
    transaction = row.to_dict()
    response = requests.post(url, json=transaction)
    
    if response.status_code == 200:
        result = response.json()
        results.append({
            'transaction_id': transaction.get('transaction_id', 'N/A'),
            'fraud_probability': result['fraud_probability'],
            'is_fraud': result['is_fraud'],
            'risk_level': result['risk_level']
        })

# Guardar resultados
results_df = pd.DataFrame(results)
results_df.to_csv('fraud_predictions.csv', index=False)
print(f"Processed {len(results)} transactions")
```

---

## Mejores Prácticas

### 1. Siempre Incluya Contexto del Usuario

Para la mejor precisión de predicción, siempre incluya estadísticas del usuario:
- `user_transaction_frequency`
- `user_avg_amount`
- `user_transaction_count`

Estos campos ayudan al modelo a detectar patrones de comportamiento inusuales.

### 2. Use Formatos de Datos Consistentes

- **Ubicaciones**: Use minúsculas con guiones bajos (ej., `"los_angeles_ca"`)
- **Categorías**: Use nombres en minúsculas y consistentes
- **Marcas de tiempo**: Use formato ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)

### 3. Maneje Errores con Gracia

```python
try:
    response = requests.post(url, json=transaction, timeout=5)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Request timeout - API may be overloaded")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Monitoree Tiempos de Respuesta

Rastree `processing_time_ms` para detectar problemas de rendimiento:

```python
if result['processing_time_ms'] > 1000:
    print("Warning: Slow prediction detected")
```

### 5. Implemente Lógica de Reintento

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def predict_with_retry(transaction):
    response = requests.post(url, json=transaction)
    response.raise_for_status()
    return response.json()
```

### 6. Caché de Predicciones

Para la misma transacción, almacene en caché las predicciones para reducir llamadas a la API:

```python
import hashlib
import json

def get_cache_key(transaction):
    return hashlib.md5(json.dumps(transaction, sort_keys=True).encode()).hexdigest()

cache = {}

def predict_with_cache(transaction):
    key = get_cache_key(transaction)
    if key in cache:
        return cache[key]
    
    result = requests.post(url, json=transaction).json()
    cache[key] = result
    return result
```

---

## Solución de Problemas

### Problema: Errores "Field required"

**Causa:** Faltan campos requeridos en la solicitud

**Solución:** Asegúrese de que todos los campos requeridos estén presentes:
```python
required_fields = [
    'amount', 'merchant_category', 'transaction_type',
    'location', 'device_type', 'hour_of_day', 'day_of_week'
]

for field in required_fields:
    if field not in transaction:
        print(f"Missing required field: {field}")
```

### Problema: "Internal Server Error"

**Causa:** Falla en ingeniería de características o error del modelo

**Solución:** 
1. Verifique que todos los campos requeridos tengan valores válidos
2. Use `/sample-transaction` para obtener un ejemplo conocido y bueno
3. Verifique que los tipos de datos coincidan con los tipos esperados

### Problema: Las predicciones parecen inexactas

**Causa:** Falta de campos de contexto del usuario

**Solución:** Incluya estadísticas del usuario:
```python
# Calcular estadísticas de usuario a partir de datos históricos
user_stats = calculate_user_stats(user_id)

transaction.update({
    'user_transaction_frequency': user_stats['frequency'],
    'user_avg_amount': user_stats['avg_amount'],
    'user_transaction_count': user_stats['count']
})
```

### Problema: Tiempos de respuesta lentos

**Causa:** Arranque en frío o alta carga

**Solución:**
1. Implemente tiempo de espera de solicitud (5-10 segundos)
2. Use solicitudes asíncronas/paralelas para procesamiento por lotes
3. Monitoree el endpoint `/health` para el estado de la API

### Problema: Errores de conexión

**Causa:** Problemas de red o tiempo de inactividad de la API

**Solución:**
```python
# Verificar endpoint de salud primero
try:
    health = requests.get(f"{base_url}/health", timeout=5)
    if health.json()['status'] != 'healthy':
        print("API is unhealthy")
except:
    print("Cannot reach API")
```

---

## Probando Localmente

### 1. Ejecutar el Contenedor Docker

```bash
# Construir la imagen
docker build -t fraud-detection-api:test .

# Ejecutar el contenedor
docker run -d --name fraud-test -p 8000:8000 fraud-detection-api:test

# Verificar registros
docker logs -f fraud-test

# Probar endpoint de salud
curl http://localhost:8000/health
```

### 2. Obtener una Transacción de Muestra

```bash
# Obtener datos de muestra
curl http://localhost:8000/sample-transaction > sample.json

# Usarlo para predicción
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @sample.json
```

### 3. Detener el Contenedor

```bash
docker stop fraud-test
docker rm fraud-test
```

---

## Lista de Verificación de Integración

- [ ] Entender campos requeridos vs opcionales
- [ ] Probar con transacción de muestra de `/sample-transaction`
- [ ] Implementar manejo de errores para errores de validación
- [ ] Agregar lógica de reintento para fallas de red
- [ ] Monitorear tiempos de respuesta y salud de la API
- [ ] Incluir contexto del usuario para mejores predicciones
- [ ] Usar formatos de datos consistentes
- [ ] Establecer tiempos de espera de solicitud apropiados
- [ ] Registrar predicciones para auditoría
- [ ] Manejar casos extremos (nuevos usuarios, montos inusuales, etc.)

---

## Soporte y Recursos

- **Documentación de API**: `https://your-app-url.ondigitalocean.app/docs`
- **Guía de Despliegue**: Ver `DEPLOYMENT_GUIDE.md`
- **Repositorio de GitHub**: `https://github.com/iamdgarcia/mlops_template`
- **Verificación de Salud**: `https://your-app-url.ondigitalocean.app/health`

Para problemas o preguntas, por favor abra un problema en GitHub o contacte al equipo de desarrollo.

---

## Información del Modelo

**Algoritmo**: Random Forest Classifier

**Características**: El modelo usa 40+ características diseñadas incluyendo:
- Monto de transacción y estadísticas
- Patrones de comportamiento del usuario
- Características temporales (hora, día, fin de semana)
- Codificaciones categóricas
- Ratios de monto y puntuaciones z

**Métricas de Rendimiento** (Conjunto de Prueba):
- Exactitud: 81.9%
- ROC AUC: 67.3%
- Precisión: 4.4%
- Recall: 38.8%
- F1 Score: 7.9%

**Nota**: El modelo está optimizado para recall (detectar fraude) a expensas de la precisión (falsos positivos). Use el campo `risk_level` para implementar estrategias de respuesta escalonadas.

---

**Última Actualización**: 12 de Diciembre, 2025  
**Versión de API**: 1.1.0
