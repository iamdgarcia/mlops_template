# Estrategia de Artefactos de Despliegue

## Resumen

Este documento explica cómo se manejan los artefactos del modelo en el pipeline de CI/CD para el despliegue.

## El Desafío

Al desplegar modelos de ML, nos enfrentamos a una pregunta clave: **¿Cómo llevamos el modelo entrenado al contenedor desplegado?**

### Opciones Consideradas

1. **Confirmar modelos en Git**  (Enfoque actual)
   - Pros: Simple, funciona con todos los sistemas CI/CD, control de versiones
   - Contras: Git no está optimizado para archivos binarios grandes
   
2. **Usar Git LFS**
   - Pros: Mejor para archivos grandes, aún con control de versiones
   - Contras: Complejidad adicional, costos de almacenamiento, requiere configuración
   
3. **Almacenamiento de artefactos externo (S3, GCS, etc.)**
   - Pros: Escalable, no infla el repositorio
   - Contras: Más complejo, requiere credenciales en la nube, costo adicional
   
4. **Registro de Contenedores** 
   - Pros: Diseñado específicamente para artefactos
   - Contras: Requiere configuración de registro, más pasos en el pipeline

## Enfoque Actual: Confirmaciones en Git

Para esta plantilla/curso, usamos el enfoque más simple que funciona:

### Cómo Funciona

1. **Fase de Entrenamiento** (GitHub Actions)
   ```yaml
   - Entrenar modelo usando scripts/run_training.py
   - Guardar modelo en models/random_forest_final_model.joblib (~10MB)
   - Subir como artefacto de GitHub Actions
   ```

2. **Fase de Despliegue** (GitHub Actions)
   ```yaml
   - Descargar artefacto del trabajo de entrenamiento
   - Confirmar archivo del modelo en repositorio git
   - Enviar a GitHub (activa reconstrucción en DigitalOcean)
   - DigitalOcean descarga el último código + modelo
   - Docker construye el contenedor con el modelo incluido
   ```

### Por Qué Funciona Esto

- **Tamaño del modelo**: ~10MB (aceptable para Git)
- **Frecuencia de actualización**: Solo en ejecuciones de entrenamiento (no en cada commit)
- **Simplicidad**: Sin dependencias externas ni configuración compleja
- **Transparencia**: La versión del modelo coincide con el commit de git
- **Amigable para el curso**: Fácil de entender y replicar

### Manejo de Archivos

**Configuración de .gitignore:**
```gitignore
# Por defecto, ignorar archivos joblib
*.joblib

# Pero permitir modelos en el directorio models/ (comentado)
# Esto permite a CI confirmar modelos entrenados
# !models/*.joblib
```

**Modelos Confirmados:**
- `models/random_forest_final_model.joblib` - Clasificador entrenado
- `data/selected_features.json` - Configuración de características  
- `data/training_summary.json` - Métricas de entrenamiento

### Mensaje de Confirmación de Git

El CI usa `[skip ci]` para prevenir bucles infinitos:
```bash
git commit -m "chore: update trained model [skip ci]"
```

Esto evita que la confirmación active otra ejecución de CI.

## Alternativa: Almacenamiento de Artefactos (Mejora Futura)

Para sistemas de producción con modelos más grandes o reentrenamiento frecuente, considere:

### Usando S3/GCS

```python
# En código de servicio
import boto3

def load_model_from_s3():
    s3 = boto3.client('s3')
    s3.download_file(
        'my-models-bucket',
        'fraud-detector/v1.0.0/model.joblib',
        '/tmp/model.joblib'
    )
    return joblib.load('/tmp/model.joblib')
```

### Usando MLflow Model Registry

```python
# En código de servicio  
import mlflow

model_uri = "models:/fraud-detector/production"
model = mlflow.pyfunc.load_model(model_uri)
```

### Usando DigitalOcean Spaces

```python
# Similar a S3, usando Spaces API
import boto3

spaces = boto3.client('s3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id=os.getenv('SPACES_KEY'),
    aws_secret_access_key=os.getenv('SPACES_SECRET')
)
```

## Mejores Prácticas

### Cuándo Usar Confirmaciones en Git
- Modelos < 50MB
- Reentrenamiento poco frecuente (diario/semanal)
- Tamaño del equipo < 10
- Proyectos educativos/plantillas
- Pipelines de despliegue simples

### Cuándo Usar Almacenamiento de Artefactos
- Modelos > 50MB
- Reentrenamiento frecuente (horario)
- Equipos grandes
- Múltiples versiones de modelos en producción
- Requisitos de pruebas A/B
- Necesidades de cumplimiento normativo

## Monitoreo del Tamaño de Artefactos

Vigile el tamaño del repositorio:

```bash
# Verificar tamaño del repositorio
du -sh .git/

# Verificar tamaños de archivos de modelo
ls -lh models/*.joblib

# Ver archivos más grandes en el historial
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -10
```

Si `.git/` excede 500MB, considere:
1. Usar Git LFS
2. Mover a almacenamiento de artefactos
3. Limpiar historial de git (¡con cuidado!)

## Ruta de Migración

Para migrar de confirmaciones en Git a almacenamiento de artefactos:

1. Configurar almacenamiento de artefactos (S3/Spaces/MLflow)
2. Actualizar `src/serving/main.py` para descargar desde almacenamiento
3. Agregar credenciales al entorno de despliegue
4. Eliminar archivos de modelo del repositorio
5. Actualizar `.gitignore` para ignorar modelos
6. Actualizar CI para enviar al almacenamiento de artefactos en lugar de git

## Conclusión

Para esta plantilla de MLOps, **las confirmaciones en Git proporcionan el mejor equilibrio entre simplicidad y funcionalidad**. El enfoque es:

 Fácil de entender  
 Fácil de replicar  
 Controlado por versiones  
 Sin dependencias externas  
 Funciona con servicios de nivel gratuito  

Esto lo hace ideal para aprender, enseñar y pequeños despliegues de producción.

---

**Última Actualización**: 12 de Diciembre, 2025  
**Tamaño del Modelo**: ~10MB  
**Tamaño del Repositorio**: <100MB
