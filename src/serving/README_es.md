# 🛡️ API de Detección de Fraude - Servicio de Modelos

Este directorio contiene la infraestructura de servicio lista para producción para el modelo de detección de fraude, incluyendo la aplicación FastAPI, el panel de monitoreo y las configuraciones de despliegue.

## 📋 Resumen

El componente de servicio proporciona:
- **API en tiempo real** para predicciones de detección de fraude
- **Monitoreo integral** con panel de Streamlit
- **Contenedorización Docker** para fácil despliegue
- **Pruebas automatizadas** y validación
- **Registro y manejo de errores** listos para producción

## 🏗️ Arquitectura

```
src/serving/
├── main.py              # Aplicación FastAPI
├── test_api.py          # Suite de pruebas de API
└── monitoring/
    └── dashboard.py     # Panel de monitoreo Streamlit

configs/
└── serving_config.yaml  # Configuración de servicio

Docker/
├── Dockerfile           # Definición de contenedor
├── docker-compose.yml   # Despliegue multi-servicio
└── start_api.sh         # Script de inicio
```

## 🚀 Inicio Rápido

### Opción 1: Ejecutar Localmente

```bash
# Asegúrese de haber entrenado un modelo primero
cd notebooks/
jupyter notebook 03_model_training.ipynb

# Iniciar la API
./start_api.sh start-local
```

### Opción 2: Ejecutar con Docker

```bash
# Construir e iniciar con Docker
./start_api.sh start-docker

# O manualmente
docker-compose up --build
```

### Opción 3: Probar la API

```bash
# Ejecutar suite de pruebas integral
./start_api.sh test

# O manualmente
python src/serving/test_api.py
```

## 📊 Endpoints de la API

### Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información y estado de la API |
| `/health` | GET | Endpoint de verificación de salud |
| `/predict` | POST | Endpoint de predicción de fraude |
| `/metrics` | GET | Métricas de rendimiento de la API |
| `/docs` | GET | Documentación interactiva de la API |

### Formato de Solicitud de Predicción

```json
{
  "amount": 150.0,
  "merchant_category": "grocery",
  "transaction_type": "purchase", 
  "location": "seattle_wa",
  "device_type": "mobile",
  "hour_of_day": 14,
  "day_of_week": 2,
  "user_transaction_frequency": 5.0,
  "user_avg_amount": 100.0,
  "user_transaction_count": 25
}
```

### Formato de Respuesta de Predicción

```json
{
  "fraud_probability": 0.1234,
  "is_fraud": false,
  "risk_level": "low",
  "prediction_id": "pred_1694123456_1",
  "timestamp": "2025-09-12T10:30:45.123456",
  "model_version": "Random_Forest_v1.0",
  "processing_time_ms": 12.34
}
```

## 🧪 Pruebas

### Suite de Pruebas Automatizadas

La suite de pruebas cubre:
- ✅ Verificaciones de salud y conectividad
- ✅ Predicciones de transacciones normales
- ✅ Detección de transacciones sospechosas
- ✅ Validación de entrada y manejo de errores
- ✅ Evaluación de rendimiento

```bash
# Ejecutar todas las pruebas
python src/serving/test_api.py

# Probar escenarios específicos
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500.0,
    "merchant_category": "online",
    "transaction_type": "purchase",
    "location": "unknown_location", 
    "device_type": "mobile",
    "hour_of_day": 3,
    "day_of_week": 6,
    "user_transaction_frequency": 2.0,
    "user_avg_amount": 50.0,
    "user_transaction_count": 5
  }'
```

### Escenarios de Prueba de Muestra

**Transacción Normal (Bajo Riesgo):**
```json
{
  "amount": 45.67,
  "merchant_category": "grocery",
  "transaction_type": "purchase",
  "location": "seattle_wa",
  "device_type": "mobile", 
  "hour_of_day": 10,
  "day_of_week": 2
}
```

**Transacción Sospechosa (Alto Riesgo):**
```json
{
  "amount": 5000.0,
  "merchant_category": "online",
  "transaction_type": "purchase",
  "location": "unknown_location",
  "device_type": "atm",
  "hour_of_day": 3,
  "day_of_week": 6
}
```

## 📊 Panel de Monitoreo

Acceda al panel de monitoreo de Streamlit:

```bash
# Iniciar el panel
streamlit run src/monitoring/dashboard.py --server.port 8501

# Acceder en: http://localhost:8501
```

### Características del Panel

- 🔴🟢 **Estado de salud de la API en tiempo real**
- 📊 **Analítica de predicciones y tendencias**
- ⚡ **Métricas de rendimiento y latencia**
- 🎯 **Tasas de detección de fraude**
- 💰 **Análisis de montos de transacción**
- 📥 **Capacidades de exportación de datos**

## ⚙️ Configuración

Edite `configs/serving_config.yaml` para personalizar:

```yaml
# Configuración de API
api:
  host: "0.0.0.0"
  port: 8000
  workers: 1

# Configuración de Modelo  
model:
  fraud_threshold: 0.5
  cache_model: true

# Monitoreo
monitoring:
  enable_drift_detection: true
  log_predictions: true
  prediction_log_path: "data/logs/predictions.csv"
```

## 🐳 Despliegue Docker

### Construir y Ejecutar

```bash
# Construir la imagen
docker build -t fraud-detection-api .

# Ejecutar contenedor
docker run -p 8000:8000 fraud-detection-api

# O usar docker-compose
docker-compose up --build
```

### Configuración Docker

El Dockerfile incluye:
- ✅ Construcción multi-etapa para optimización
- ✅ Verificaciones de salud para orquestación de contenedores  
- ✅ Configuración adecuada de registros
- ✅ Mejores prácticas de seguridad

## 📈 Rendimiento

### Puntos de Referencia

Basado en ejecuciones de prueba con modelo Random Forest:

| Métrica | Valor |
|--------|-------|
| **Latencia Promedio** | ~15ms |
| **Rendimiento** | ~50 solicitudes/segundo |
| **Uso de Memoria** | ~200MB |
| **Tiempo de Carga del Modelo** | ~2 segundos |

### Consejos de Optimización

1. **Caché de Modelo**: Mantener modelo en memoria (habilitado por defecto)
2. **Ingeniería de Características**: Pre-calcular características de usuario cuando sea posible
3. **Procesamiento Asíncrono**: Usar tareas en segundo plano para registros
4. **Balanceo de Carga**: Usar múltiples trabajadores para alto tráfico

## 🔒 Seguridad

### Validación de Entrada

- ✅ Modelos Pydantic para validación de solicitudes
- ✅ Verificaciones de rango para entradas numéricas
- ✅ Validación Enum para entradas categóricas
- ✅ Prevención de inyección SQL
- ✅ Limitación de tasa (configurable)

### Lista de Verificación de Producción

- [ ] Habilitar HTTPS/TLS
- [ ] Configurar claves API/autenticación
- [ ] Configurar limitación de tasa
- [ ] Habilitar CORS apropiadamente
- [ ] Configurar niveles de registro
- [ ] Configurar alertas de monitoreo

## 📝 Registros

### Ubicaciones de Registros

```
logs/
├── serving.log          # Registros de aplicación API
└── data/logs/
    ├── predictions.csv  # Historial de predicciones
    └── metrics.csv      # Métricas de rendimiento
```

### Niveles de Registro

- `INFO`: Eventos de operación normal
- `WARNING`: Problemas de rendimiento 
- `ERROR`: Fallas de predicción
- `DEBUG`: Información detallada de depuración

## 🚨 Solución de Problemas

### Problemas Comunes

**Modelo No Encontrado:**
```bash
# Asegúrese de que el modelo fue entrenado
ls -la models/Random_Forest_final_model.joblib

# Reentrenar si es necesario
jupyter notebook notebooks/03_model_training.ipynb
```

**API No Iniciando:**
```bash
# Verificar disponibilidad de puerto
lsof -i :8000

# Verificar registros
tail -f logs/serving.log

# Verificar dependencias
pip install -r requirements.txt
```

**Errores de Predicción:**
```bash
# Validar formato de entrada
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "merchant_category": "grocery", ...}'

# Verificar documentación de API
open http://localhost:8000/docs
```

## 🔄 Desarrollo

### Agregando Nuevas Características

1. **Nuevos Endpoints**: Agregar a `src/serving/main.py`
2. **Nuevas Pruebas**: Actualizar `src/serving/test_api.py` 
3. **Nuevo Monitoreo**: Extender `src/monitoring/dashboard.py`
4. **Configuración**: Actualizar `configs/serving_config.yaml`

### Desarrollo Local

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Iniciar en modo desarrollo
uvicorn src.serving.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar pruebas continuamente
pytest src/serving/ --watch
```

## 📚 Documentación de API

- **Docs Interactivos**: http://localhost:8000/docs
- **Esquema OpenAPI**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contribuyendo

1. Siga el estilo de código existente
2. Agregue pruebas para nuevas características
3. Actualice la documentación
4. Pruebe con casos normales y extremos
5. Verifique que el despliegue Docker funcione

## 📄 Licencia

Este proyecto es parte de la plantilla de Detección de Fraude MLOps.
