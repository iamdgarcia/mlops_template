# Guía de Dependencias

Este documento explica las dependencias usadas en este proyecto de detección de fraude MLOps y sus propósitos.

## Dependencias Principales

### Ciencia de Datos y Aprendizaje Automático
- **pandas (~=1.5.0)**: La librería fundamental para manipulación y análisis de datos. Usada para cargar, limpiar y transformar datos de transacciones.
- **numpy (~=1.24.0)**: Provee operaciones numéricas eficientes y manejo de arrays. Usada en todo el proyecto para computaciones matemáticas.
- **scikit-learn (~=1.3.0)**: La librería principal de aprendizaje automático que contiene:
  - Algoritmos de clasificación (Regresión Logística, Random Forest)
  - Métricas de evaluación de modelos
  - Utilidades de preprocesamiento de datos
  - Herramientas de validación cruzada
- **xgboost (~=2.0.0)**: Librería avanzada de gradient boosting. Opcional - puede ser deshabilitada en la configuración si no se necesita.

### Herramientas MLOps
- **mlflow (~=2.7.0)**: Plataforma MLOps completa que provee:
  - Rastreo de experimentos (registrar parámetros, métricas, artefactos)
  - Registro de modelos (control de versiones para modelos)
  - Utilidades de despliegue de modelos
  - UI para visualizar experimentos

### API y Framework Web
- **fastapi (~=0.100.0)**: Framework web moderno y rápido para construir APIs con:
  - Documentación automática de API (Swagger UI)
  - Validación de datos vía Pydantic
  - Soporte asíncrono para alto rendimiento
- **uvicorn (~=0.23.0)**: Servidor ASGI ultra rápido para ejecutar aplicaciones FastAPI
- **pydantic (~=2.0.0)**: Validación de datos y gestión de configuraciones usando anotaciones de tipo de Python

### Configuración y Utilidades
- **pyyaml (~=6.0)**: Analizar archivos de configuración YAML (training_config.yaml, serving_config.yaml)
- **python-multipart (~=0.0.6)**: Manejar datos de formularios multipart en peticiones API

## Herramientas de Desarrollo

### Pruebas
- **pytest (~=7.4.0)**: Framework de pruebas moderno con:
  - Descubrimiento de pruebas simple
  - Fixtures potentes
  - Reporte de fallos detallado
- **pytest-cov (~=4.1.0)**: Plugin de cobertura de código para pytest para medir la cobertura de las pruebas

### Calidad de Código
- **black (~=23.0.0)**: Formateador de código obstinado que asegura un estilo consistente
- **flake8 (~=6.0.0)**: Herramienta de linting para detectar errores comunes y problemas de estilo
- **isort (~=5.12.0)**: Organiza y ordena automáticamente las declaraciones de importación

## Visualización (Soporte Notebook)

- **matplotlib (~=3.7.0)**: Librería de gráficos básica para cuadros y gráficos
- **seaborn (~=0.12.0)**: Visualización estadística construida sobre matplotlib con hermosos valores por defecto
- **plotly (~=5.15.0)**: Visualizaciones interactivas y tableros

## Entorno Jupyter

- **jupyter (~=1.0.0)**: Entorno completo de notebook Jupyter
- **ipykernel (~=6.25.0)**: Kernel IPython que permite la ejecución de código Python en notebooks

## Clientes HTTP

- **requests (~=2.31.0)**: Librería HTTP simple y elegante para pruebas e interacción con API
- **httpx (~=0.24.0)**: Cliente HTTP moderno con capacidad asíncrona (usado por el cliente de pruebas de FastAPI)

## Estrategia de Fijación de Versiones

Este proyecto usa fijación de **lanzamiento compatible** (`~=`):
- `pandas~=1.5.0` permite versiones `>=1.5.0` y `<1.6.0`
- Esto permite correcciones de errores pero previene cambios que rompen compatibilidad
- Para una reproducibilidad más estricta en producción, considere fijación exacta (`==`)

## Dependencias Opcionales

Las siguientes se mencionan en la configuración pero no se instalan por defecto:

### Monitoreo (Características Planeadas)
- **prometheus-client**: Exportar métricas al sistema de monitoreo Prometheus
- **streamlit**: Construir tableros interactivos para monitoreo de modelos

Para instalar dependencias opcionales:
```bash
pip install prometheus-client~=0.17.0
pip install streamlit~=1.25.0
```

## Instalación

### Instalación Estándar
```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar todas las dependencias
pip install -r requirements.txt
```

### Instalación Mínima (Solo API)
Si solo necesitas ejecutar la API con un modelo pre-entrenado:
```bash
pip install pandas numpy scikit-learn mlflow fastapi uvicorn pydantic pyyaml
```

### Instalación de Desarrollo
Para contribuir al proyecto:
```bash
pip install -r requirements.txt
# Todas las herramientas incluyendo pytest, black, flake8 están incluidas
```

## Solución de Problemas

### Errores de Importación
Si obtienes `ModuleNotFoundError`, asegura:
1. El entorno virtual está activado
2. Las dependencias están instaladas: `pip install -r requirements.txt`
3. Para Jupyter, el kernel apunta a tu venv: `python -m ipykernel install --user --name=mlops_env`

### Conflictos de Versión
Si pip reporta conflictos de versión:
1. Crea un entorno virtual fresco
2. Actualiza pip: `pip install --upgrade pip`
3. Instala dependencias: `pip install -r requirements.txt`

### Problemas de Instalación de XGBoost
XGBoost puede requerir dependencias de sistema adicionales en algunas plataformas:
- **Linux**: Usualmente funciona de inmediato
- **macOS**: Puede necesitar `brew install libomp`
- **Windows**: Usa wheels pre-construidos de PyPI

Si la instalación de XGBoost falla, puedes deshabilitarlo:
1. Comenta `xgboost~=2.0.0` en requirements.txt
2. Establece `enabled: false` para XGBoost en `configs/training_config.yaml`

## Actualizaciones de Dependencias

Para verificar paquetes desactualizados:
```bash
pip list --outdated
```

Para actualizar un paquete específico:
```bash
pip install --upgrade package-name
```

**Nota**: Siempre prueba exhaustivamente después de actualizar dependencias, ya que las nuevas versiones pueden introducir cambios que rompen compatibilidad.

## Consideraciones de Seguridad

Para despliegues en producción:
1. Actualiza regularmente las dependencias para obtener parches de seguridad
2. Usa herramientas como `pip-audit` o `safety` para verificar vulnerabilidades conocidas
3. Considera usar `pip-tools` o `poetry` para una gestión de dependencias más avanzada

```bash
# Verificar vulnerabilidades de seguridad
pip install pip-audit
pip-audit
```
