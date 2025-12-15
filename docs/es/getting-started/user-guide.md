# Pipeline de Detección de Fraude MLOps - Guía de Usuario

Bienvenido al pipeline completo de detección de fraude MLOps. Esta guía te llevará a través de toda la estructura del proyecto, secuencia de ejecución y conceptos clave de aprendizaje.

## Guía de Inicio Rápido

### Prerrequisitos
- Python 3.8+ instalado
- Conocimiento básico de conceptos de aprendizaje automático
- Familiaridad con notebooks Jupyter

### Instalación
1. **Clonar y Configurar Entorno**
   ```bash
   git clone <repository-url>
   cd mlops_template
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Verificar Instalación**
   ```bash
   python -c "import mlflow; import pandas; import sklearn; print('Configuración completa')"
   ```

## Ruta de Aprendizaje - Ejecutar en Orden

### Módulo 1: Preparación de Datos
**Archivo**: `notebooks/01_data_preparation.ipynb`
**Duración**: 30-45 minutos
**Conceptos Aprendidos**:
- Generación de datos sintéticos para proyectos ML
- Evaluación y validación de calidad de datos
- Técnicas de análisis exploratorio de datos (EDA)
- Análisis estadístico de patrones de fraude
- Exportación de datos y preparación del pipeline

**Salidas Clave**:
- `data/transactions_raw.csv` - Dataset de transacciones generado
- Reporte de calidad de datos y visualizaciones
- Entendimiento de patrones de fraude vs transacciones normales

### Módulo 2: Ingeniería de Características
**Archivo**: `notebooks/02_feature_engineering.ipynb`
**Duración**: 45-60 minutos
**Conceptos Aprendidos**:
- Técnicas avanzadas de creación de características
- Ingeniería de características temporales y de comportamiento
- Métodos de selección de características (estadísticos y basados en ML)
- Validación de características y análisis de correlación
- Preparación del pipeline para entrenamiento de modelos

**Salidas Clave**:
- `data/transactions_final.csv` - Dataset con ingeniería de características
- `data/selected_features.json` - Metadatos de características
- Rankings de importancia de características y análisis de correlación

### Módulo 3: Entrenamiento de Modelos y Rastreo MLflow
**Archivo**: `notebooks/03_model_training.ipynb`
**Duración**: 60-90 minutos
**Conceptos Aprendidos**:
- Comparación de múltiples algoritmos
- Optimización de hiperparámetros con GridSearchCV
- Rastreo de experimentos y logging con MLflow
- Métricas de evaluación de modelos para detección de fraude
- Validación cruzada y selección de modelos

**Salidas Clave**:
- Modelos entrenados registrados en MLflow
- Reportes de comparación de rendimiento
- Selección y registro del mejor modelo
- Directorio `models/` con modelos guardados

### Módulo 4: Inferencia y Servicio de Modelos
**Archivo**: `notebooks/04_model_inference.ipynb`
**Duración**: 45-60 minutos
**Conceptos Aprendidos**:
- Diseño de pipeline de inferencia para producción
- Patrones de predicción por lotes y en tiempo real
- Carga y optimización de modelos
- Desarrollo de API con FastAPI
- Monitoreo de rendimiento y logging

**Salidas Clave**:
- Pipeline de inferencia listo para producción
- Implementación de servidor FastAPI
- Benchmarks de rendimiento de predicción

### Módulo 5: Detección de Drift y Monitoreo
**Archivo**: `notebooks/05_drift_detection.ipynb`
**Duración**: 45-60 minutos
**Conceptos Aprendidos**:
- Técnicas de detección de drift de datos
- Métodos estadísticos para comparación de distribuciones
- Monitoreo de rendimiento del modelo
- Sistemas de alerta y umbrales
- Integración con MLflow para rastreo

**Salidas Clave**:
- Framework de detección de drift
- Tableros de monitoreo y alertas
- Rastreo de rendimiento histórico

## Integración MLflow

### Iniciando UI de MLflow
```bash
mlflow ui --port 5000
```
Acceder en: http://localhost:5000

### Características Clave de MLflow Usadas
- **Rastreo de Experimentos**: Todas las ejecuciones de entrenamiento de modelos
- **Registro de Modelos**: Versionado del mejor modelo
- **Logging de Métricas**: Métricas de rendimiento a lo largo del tiempo
- **Almacenamiento de Artefactos**: Modelos, gráficos y datos

## Despliegue de API

### Iniciando la API de Inferencia
```bash
# Usando el script de inicio
./start_api.sh

# O directamente con uvicorn
uvicorn src.serving.main:app --reload --port 8000

# Servidor demo mínimo (opcional)
uvicorn scripts.minimal_serve:app --reload --port 8000
```

### Endpoints de API
- `GET /` - Información de API y enlace a documentación
- `GET /health` - Chequeo de salud con estado del modelo
- `POST /predict` - Predicción de fraude para una sola transacción
- `GET /sample-transaction` - Obtener una transacción de muestra para pruebas
- `GET /metrics` - Métricas de rendimiento de la API
- `POST /save-logs` - Guardar manualmente logs de predicción

**Nota**: El endpoint `/model/info` mencionado en documentación anterior ha sido reemplazado con `/metrics` que incluye información de versión del modelo.

### Ejemplo de Uso de API
```python
import requests

# Obtener una transacción de muestra para probar
sample = requests.get('http://localhost:8000/sample-transaction').json()
print("Transacción de muestra:", sample)

# Predicción única
response = requests.post('http://localhost:8000/predict', json=sample)
result = response.json()
print(f"Probabilidad de fraude: {result['fraud_probability']}")
print(f"Nivel de riesgo: {result['risk_level']}")

# Chequear salud de API
health = requests.get('http://localhost:8000/health').json()
print(f"Modelo cargado: {health['model_loaded']}")
```

## Despliegue Docker

### Construyendo y Ejecutando con Docker
```bash
# Construir imagen
docker build -t fraud-detection-api .

# Ejecutar contenedor
docker run -p 8000:8000 fraud-detection-api

# O usar Docker Compose
docker-compose up
```

## Profundización en Estructura del Proyecto

### `/notebooks/` - Secuencia Educativa
Notebooks Jupyter secuenciales que se construyen uno sobre otro. Cada notebook es autocontenido pero diseñado para ser ejecutado en orden.

### `/src/` - Código de Producción
Código Python modularizado y reutilizable extraído de notebooks:
- `data_generation/` - Creación de datos sintéticos
- `features.py` - **Fuente única de verdad para ingeniería de características** (usado por entrenamiento, inferencia y servicio)
- `inference.py` - Pipeline de predicción que usa `FeatureEngineer`
- `serving/` - Aplicación FastAPI
- `pipelines/` - Orquestación de alto nivel para preparación de datos y entrenamiento

**Patrón de Diseño Clave**: Todo el flujo de ingeniería de características pasa a través de la clase `FeatureEngineer` de `src/features.py` para asegurar paridad entrenamiento/servicio.

### `/configs/` - Gestión de Configuración
Archivos de configuración YAML para diferentes entornos y componentes.

### `/data/` - Almacenamiento de Datos
Generado durante la ejecución de notebooks:
- `raw/` - Datos generados originales
- `processed/` - Datos limpios y transformados
- Metadatos de características y artefactos del pipeline

### `/models/` - Artefactos de Modelo
Modelos entrenados, escaladores y metadatos guardados para uso en producción.

## Conceptos Clave de Aprendizaje

### Mejores Prácticas MLOps Demostradas
1. **Reproducibilidad**: Gestión de semillas y configuración
2. **Rastreo de Experimentos**: Integración completa con MLflow
3. **Organización de Código**: Estructura modular con notebooks + src/
4. **Control de Versiones**: Estructura de proyecto amigable con Git
5. **Documentación**: Documentación en línea completa
6. **Pruebas**: Framework para pruebas unitarias y de integración
7. **Despliegue**: Patrones de servicio API y Docker
8. **Monitoreo**: Rastreo de drift de datos y rendimiento del modelo

### Conocimiento de Dominio de Detección de Fraude
1. **Clasificación Desbalanceada**: Técnicas para detección de eventos raros
2. **Ingeniería de Características**: Creación de características específicas del dominio
3. **Métricas de Evaluación**: Precisión, recall, F1 para detección de fraude
4. **Patrones Temporales**: Análisis de fraude basado en tiempo
5. **Análisis de Comportamiento**: Reconocimiento de patrones de usuario

## Ingeniería de Características: Fuente Única de Verdad

### Patrón de Arquitectura
Este proyecto implementa una mejor práctica crítica de MLOps: **paridad de ingeniería de características** entre entrenamiento y servicio.

**Cómo funciona**:
1. **Implementación Canónica**: Toda la lógica de ingeniería de características vive en `src/features.py` en la clase `FeatureEngineer`
2. **Ruta de Entrenamiento**: Notebooks y scripts de entrenamiento importan y usan `FeatureEngineer.create_all_features()`
3. **Ruta de Inferencia**: `InferencePipeline` en `src/inference.py` usa `FeatureEngineer` para preprocesamiento
4. **Ruta de Servicio**: La aplicación FastAPI delega a `InferencePipeline`, que usa `FeatureEngineer`

### Por Qué Importa Esto
**Sesgo Entrenamiento/Servicio** es un modo de fallo común en MLOps donde las características calculadas de manera diferente en entrenamiento vs. producción causan degradación del rendimiento del modelo. Al usar el mismo camino de código, eliminamos este riesgo.

### Ejemplo de Uso

**En Entrenamiento** (notebooks/03_model_training.ipynb):
```python
from src.features import FeatureEngineer

engineer = FeatureEngineer(config)
features_df = engineer.create_all_features(raw_data)
# Usar features_df para entrenamiento...
```

**En Inferencia** (src/inference.py):
```python
from src.features import FeatureEngineer

class InferencePipeline:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
    
    def preprocess_data(self, raw_data):
        return self.feature_engineer.create_all_features(raw_data)
```

**En Servicio** (src/serving/main.py):
```python
# Endpoint FastAPI
@app.post("/predict")
async def predict_fraud(transaction: TransactionRequest):
    # InferencePipeline maneja ingeniería de características internamente
    predictions = inference_pipeline.predict_batch(transaction_df)
    return predictions
```

### Validación
La suite de pruebas `tests/test_feature_parity.py` valida que:
- La ingeniería de características produce resultados consistentes a través de todos los contextos
- Ninguna característica se calcula diferente en entrenamiento vs. servicio
- Los casos borde se manejan correctamente
- Los esquemas de características permanecen compatibles

## Integración de Tutoriales en Video

Este proyecto está diseñado para soportar tutoriales en video para conceptos clave:

### Temas de Video Recomendados
1. **"Descripción General del Pipeline MLOps"** - Recorrido completo de la estructura de 5 módulos
2. **"MLflow en Práctica"** - Profundización en rastreo de experimentos y registro de modelos
3. **"Ingeniería de Características para Detección de Fraude"** - Técnicas de creación de características específicas del dominio
4. **"Despliegue ML en Producción"** - Desarrollo de API y despliegue Docker
5. **"Monitoreo de Modelos ML"** - Detección de drift y monitoreo de rendimiento

### Guías para Tutoriales en Video
- Cada video debe corresponder a 1-2 notebooks
- Incluir demostraciones de codificación en vivo
- Explicar tanto el código como los conceptos ML subyacentes
- Mostrar la UI de MLflow e interacciones de API
- Demostrar solución de problemas comunes

## Guía de Solución de Problemas

### Problemas Comunes

1. **Errores de Importación**
   ```bash
   # Asegurar que el entorno virtual está activado
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Problemas de MLflow**
## Solución de Problemas

### Problemas Comunes y Soluciones

1. **Archivo de Modelo No Encontrado**
   ```bash
   # Error: Model file not found at models/random_forest_final_model.joblib
   # Solución: Ejecutar el notebook de entrenamiento primero para generar el modelo
   jupyter notebook notebooks/03_model_training.ipynb
   ```

2. **Conflicto de Puerto MLflow**
   ```bash
   # Error: Address already in use
   # Solución: Matar el proceso existente o usar un puerto diferente
   lsof -i :5000  # Encontrar el proceso usando puerto 5000
   kill -9 <PID>  # Matar el proceso
   # O usar un puerto diferente:
   mlflow ui --port 5001
   ```

3. **Errores de Permiso en directorios data/ o models/**
   ```bash
   # Error: Permission denied when writing to data/ or models/
   # Solución: Asegurar que los directorios existen y tienen permisos apropiados
   mkdir -p data/logs data/inference_results data/drift_alerts models logs
   chmod -R u+w data models logs
   ```

4. **Docker HEALTHCHECK Falla**
   ```bash
   # Error: Container marked as unhealthy
   # Causa: curl no instalado en contenedor (arreglado en último Dockerfile)
   # Solución: Reconstruir la imagen Docker
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

5. **Dependencias Faltantes en Notebooks**
   ```bash
   # Error: ModuleNotFoundError
   # Solución: Asegurar que el entorno virtual está activado y paquetes instalados
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   # Para Jupyter, asegurar que el kernel usa el entorno correcto
   python -m ipykernel install --user --name=mlops_env
   ```

6. **Datos No Encontrados**
   ```bash
   # Error: File not found: data/transactions_raw.csv
   # Solución: Ejecutar notebooks en secuencia - cada uno genera datos para el siguiente
   # Empezar con 01_data_preparation.ipynb
   ```

7. **Problemas de Conexión de API**
  ```bash
  # Chequear si el puerto está disponible
  lsof -i :8000
  # Matar proceso si es necesario
  kill -9 <PID>
  # O usar puerto diferente
  uvicorn src.serving.main:app --port 8001
  ```

8. **Problemas de Rastreo de Experimentos MLflow**
   ```bash
   # Error: Failed to create experiment
   # Solución: Limpiar caché de MLflow y reiniciar
   rm -rf mlruns/
   # MLflow recreará experimentos cuando ejecutes el notebook de entrenamiento
   ```

### Optimización de Rendimiento
- Reducir tamaño del dataset en archivos de configuración para ejecución más rápida
- Usar multiprocesamiento para ingeniería de características
- Considerar aceleración GPU para modelos grandes

## Próximos Pasos y Extensiones

### Mejoras Potenciales
1. **Modelos Avanzados**: Enfoques de aprendizaje profundo (redes neuronales)
2. **Streaming en Tiempo Real**: Integración con Kafka o similar
3. **Monitoreo Avanzado**: Integración con Prometheus y Grafana
4. **Despliegue en Nube**: Patrones de despliegue AWS/GCP/Azure
5. **Pruebas A/B**: Patrones de modelo campeón/retador
6. **Detección de Drift Avanzada**: Métodos estadísticos más sofisticados

### Consideraciones de Producción
1. **Seguridad**: Autenticación y autorización
2. **Escalabilidad**: Balanceo de carga y auto-escalado
3. **Confiabilidad**: Circuit breakers y mecanismos de fallback
4. **Cumplimiento**: Pistas de auditoría y explicabilidad del modelo
5. **Optimización de Costos**: Gestión de recursos y monitoreo

## Soporte y Comunidad

### Obteniendo Ayuda
1. Revisar la documentación de notebooks y comentarios
2. Chequear la UI de MLflow para detalles de experimentos
3. Consultar la documentación de API en endpoint `/docs`
4. Revisar la sección de solución de problemas arriba

### Contribuyendo
1. Seguir la estructura de código existente y estilo de documentación
2. Agregar comentarios completos para valor educativo
3. Incluir pruebas para nueva funcionalidad
4. Actualizar esta guía con nuevas características

Este proyecto sirve como una fundación completa para entender e implementar prácticas MLOps en un escenario de detección de fraude del mundo real. La estructura modular permite fácil personalización y extensión basada en requisitos específicos y objetivos de aprendizaje.
