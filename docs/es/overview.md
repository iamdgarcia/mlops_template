# Pipeline de Detección de Fraude MLOps

Un pipeline de aprendizaje automático completo de extremo a extremo que demuestra las mejores prácticas de MLOps a través de un caso de uso de detección de fraude.

## Descripción General

Este repositorio contiene una implementación integral de MLOps que cubre todo el ciclo de vida del aprendizaje automático, desde la preparación de datos hasta el monitoreo del modelo en producción. El proyecto utiliza un escenario de detección de fraude para demostrar patrones y mejores prácticas de MLOps del mundo real.

## Módulos de Aprendizaje

El pipeline está estructurado como 5 cuadernos Jupyter secuenciales que se basan uno en el otro:

### 1. Preparación de Datos
**Archivo**: `notebooks/01_data_preparation.ipynb`

- Generar conjunto de datos sintético de detección de fraude
- Realizar validación de datos y comprobaciones de calidad
- Crear divisiones estratificadas de entrenamiento/validación/prueba
- Analizar distribuciones y patrones de datos

### 2. Ingeniería de Características
**Archivo**: `notebooks/02_feature_engineering.ipynb`

- Crear características conductuales y temporales
- Implementar técnicas de selección de características
- Analizar importancia y correlaciones de características
- Preparar características para el entrenamiento del modelo

### 3. Entrenamiento del Modelo
**Archivo**: `notebooks/03_model_training.ipynb`

- Comparar múltiples algoritmos de aprendizaje automático
- Realizar ajuste de hiperparámetros con validación cruzada
- Rastrear experimentos usando MLflow
- Guardar modelos entrenados y métricas de evaluación

### 4. Inferencia del Modelo
**Archivo**: `notebooks/04_model_inference.ipynb`

- Construir pipeline de inferencia listo para producción
- Implementar patrones de predicción por lotes y en tiempo real
- Optimizar carga y rendimiento del modelo
- Manejar solicitudes de predicción eficientemente

### 5. Detección de Deriva y Monitoreo
**Archivo**: `notebooks/05_drift_detection.ipynb`

- Implementar métodos estadísticos de detección de deriva
- Configurar monitoreo y alertas automatizadas
- Rastrear rendimiento del modelo a lo largo del tiempo
- Integrar monitoreo con MLflow

## Requisitos Previos

- Python 3.8 o superior
- Conocimiento básico de conceptos de aprendizaje automático
- Familiaridad con pandas, scikit-learn y cuadernos Jupyter

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd mlops_template
```

2. Crear y activar un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Inicio Rápido

1. Ejecutar los cuadernos principales en secuencia (ruta rápida):
   - `notebooks/01_data_preparation.ipynb`
   - `notebooks/02_feature_engineering.ipynb`
   - `notebooks/03_model_training.ipynb`
   - `notebooks/04_model_inference.ipynb`
   - `notebooks/05_drift_detection.ipynb`

   Este repositorio se centra en estos cinco módulos para la demostración rápida.

2. **Lanzar UI de MLflow** (opcional):
```bash
mlflow ui --port 5000
```
Acceder a la interfaz de MLflow en http://localhost:5000

3. **Iniciar la API de inferencia** (después de completar los cuadernos):
```bash
# Aplicación FastAPI completa
uvicorn src.serving.main:app --reload --port 8000

# O usar el servidor de demostración mínimo
uvicorn scripts.minimal_serve:app --reload --port 8000
```

## Estructura del Proyecto

```
mlops_template/
├── notebooks/              # Cuadernos Jupyter educativos (ejecutar en orden 01-05)
│   ├── 01_data_preparation.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_inference.ipynb
│   └── 05_drift_detection.ipynb
├── src/                     # Módulos Python reutilizables
│   ├── data_generation/     # Utilidades de generación de datos
│   ├── feature_engineering/ # Funciones de creación de características
│   ├── models/             # Entrenamiento y evaluación de modelos
│   ├── inference/          # Pipeline de predicción
│   ├── serving/            # Aplicación FastAPI
│   └── pipelines/          # Orquestación de pipeline de alto nivel
├── scripts/                # Scripts de automatización
│   ├── run_full_pipeline.py  # Ejecución de pipeline de extremo a extremo
│   └── minimal_serve.py      # Demostración de API mínima
├── configs/                # Archivos de configuración YAML
├── data/                   # Conjuntos de datos generados (creados durante la ejecución)
├── models/                 # Artefactos de modelo guardados
├── tests/                  # Pruebas unitarias y de integración
└── requirements.txt        # Dependencias de Python
```

## Tecnologías Clave

- **Procesamiento de Datos**: pandas, numpy
- **Aprendizaje Automático**: scikit-learn, xgboost
- **Rastreo de Experimentos**: MLflow
- **Marco de API**: FastAPI
- **Pruebas**: pytest
- **Visualización**: matplotlib, seaborn

## Resultados de Aprendizaje

Después de completar este proyecto, entenderás:

- Cómo estructurar un pipeline de ML de extremo a extremo
- Mejores prácticas de MLOps para rastreo de experimentos y versionado de modelos
- Patrones de producción para servicio y monitoreo de modelos
- Cómo implementar detección de deriva de datos
- Integración de MLflow para gestión del ciclo de vida de ML

## Caso de Uso: Detección de Fraude

El proyecto simula un sistema bancario que necesita detectar transacciones fraudulentas en tiempo real. El pipeline incluye:

- **Datos Sintéticos**: Datos de transacciones realistas con etiquetas de fraude/legítimo
- **Ingeniería de Características**: Patrones de transacciones, comportamiento del usuario, características temporales
- **Comparación de Modelos**: Múltiples algoritmos con optimización de hiperparámetros
- **Servicio en Producción**: API REST para predicciones en tiempo real
- **Monitoreo**: Detección de deriva de datos y rastreo de rendimiento del modelo

## Enfoque Educativo

Este repositorio está diseñado para:
- Científicos de datos aprendiendo prácticas de MLOps
- Ingenieros de ML haciendo la transición a flujos de trabajo de producción
- Equipos implementando su primer pipeline de ML de extremo a extremo
- Cualquiera interesado en implementación práctica de MLOps

## Despliegue

### Plataforma de Aplicaciones DigitalOcean (Recomendado para el Curso)

Este proyecto incluye despliegue automatizado a la Plataforma de Aplicaciones DigitalOcean con **auto-despliegue basado en git** - ¡sin necesidad de tokens de API o secretos!

>  **¡Obtén $200 de Crédito Gratis!** Regístrate usando [este enlace](https://m.do.co/c/eddc62174250) para recibir $200 en créditos gratis por 60 días - ¡perfecto para ejecutar este proyecto del curso sin costo!

**Cómo funciona:** GitHub Actions entrena el modelo y lo confirma en el repositorio. DigitalOcean detecta automáticamente el push de git y despliega vía webhook - ¡simple y seguro!

**Configuración Rápida (Automatizada):**
```bash
# Instalar CLI doctl y autenticar
doctl auth init

# Ejecutar el script de inicialización para crear las 3 aplicaciones
./scripts/init_digitalocean_apps.sh
```

**Configuración Manual:**
1. Crear una cuenta de DigitalOcean en [cloud.digitalocean.com](https://m.do.co/c/eddc62174250) (incluye $200 de crédito gratis)
2. Instalar CLI doctl: `brew install doctl` o ver [guía de instalación](https://docs.digitalocean.com/reference/doctl/how-to/install/)
3. Autenticar: `doctl auth init`
4. Ejecutar `./scripts/init_digitalocean_apps.sh` para crear aplicaciones automáticamente
5. Hacer push a la rama `master` para activar el primer despliegue

**Documentación:**
- **Script de configuración rápida:** `./scripts/init_digitalocean_apps.sh`
- **Guía paso a paso:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Guía de uso de API:** [API_GUIDE.md](./API_GUIDE.md)

**Costo:** ~$5/mes por entorno (Nivel básico con 512MB RAM)

El despliegue automáticamente:
-  Entrena el modelo en GitHub Actions CI
-  **Valida puertas de calidad del modelo** (evita desplegar modelos peores)
-  Compara contra métricas de línea base de producción
-  Confirma el modelo entrenado al repositorio con `[skip ci]`
-  Activa auto-despliegue de DigitalOcean vía webhook de git
-  Construye contenedor Docker con modelo
-  Despliega aplicación FastAPI con comprobaciones de salud
-  Proporciona punto final HTTPS público
-  Despliegue azul-verde sin tiempo de inactividad

**Accede a tu API desplegada:**
- Comprobación de salud: `https://tu-app.ondigitalocean.app/health`
- Documentos de API: `https://tu-app.ondigitalocean.app/docs`
- Predicciones: `POST https://tu-app.ondigitalocean.app/predict`

## Pruebas

Ejecutar el conjunto de pruebas para validar la implementación:
```bash
pytest tests/
```

##  Documentación

**La documentación completa está disponible en el directorio [`docs/`]().**

### Enlaces Rápidos

- **[Empezando](getting-started/quick-start.md)** - Guía de configuración de 15 minutos
- **[Guía de Despliegue](deployment/setup-guide.md)** - Despliegue en producción
- **[Referencia de API](api/guide.md)** - Uso de API y ejemplos
- **[Arquitectura](architecture.md)** - Diseño del sistema y decisiones

### Estructura de Documentación

```
docs/
├── README.md                      # Índice de documentación y navegación
├── getting-started/               # Guías de configuración y usuario
│   ├── requirements.md            # Requisitos previos
│   ├── quick-start.md             # Guía de configuración rápida
│   └── user-guide.md              # Manual completo
├── deployment/                    # Guías de despliegue
│   ├── overview.md                # Descripción general de arquitectura
│   ├── setup-guide.md             # Configuración de DigitalOcean
│   ├── workflow-changes.md        # Flujos de trabajo CI/CD
│   └── troubleshooting.md         # Problemas comunes
├── api/                           # Documentación de API
│   └── guide.md                   # Referencia de API
└── DEPLOYMENT_MECHANICS.md        # Detalles técnicos de despliegue
```

** Empieza aquí**: [docs/README_es.md](README.md) para el índice completo de documentación.

## Contribuyendo

¡Las contribuciones son bienvenidas! Por favor siéntete libre de enviar problemas o solicitudes de extracción para mejorar el contenido educativo o agregar nuevas características.

## Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## Tutoriales en Video

Explicaciones detalladas en video cubriendo todos los aspectos de este pipeline de MLOps están disponibles exclusivamente dentro del curso:

- **Módulo 1-2**: Fundamentos de Preparación de Datos e Ingeniería de Características
- **Módulo 3**: Integración de MLflow y Rastreo de Experimentos
- **Módulo 4-5**: Estrategias de Despliegue en Producción y Monitoreo

** Acceder a Videos del Curso**: [Scale AI with MLOps - Complete Course](https://iamdgarcia.gumroad.com/l/scale-ai-with-mlops)

*Nota: Los tutoriales en video solo están disponibles para estudiantes inscritos*

## Orquestación del Pipeline

El proyecto ahora expone ayudantes de alto nivel que envuelven los flujos de trabajo reutilizables de datos y entrenamiento:

- `src.pipelines.run_data_preparation` genera conjuntos de datos crudos/limpios/características y divisiones estratificadas.
- `src.pipelines.run_training_pipeline` entrena todos los modelos configurados, registra la mejor ejecución con MLflow y guarda el artefacto de producción.

Puedes ejecutar el pipeline completo localmente con:

```bash
python scripts/run_full_pipeline.py
```

## Pruebas

Ejecuta las pruebas de regresión ligeras para validar el comportamiento del pipeline principal:

```bash
pytest tests/test_pipelines.py
```

(Las pruebas que tocan el pipeline de inferencia requieren que `mlflow` esté instalado; el conjunto las omite automáticamente cuando no está disponible.)
