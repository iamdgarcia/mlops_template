# Mecánica de Despliegue - Documentación Técnica

Este documento explica la arquitectura técnica y la mecánica del despliegue de la API de detección de fraude en DigitalOcean App Platform.

## Descripción General

**Método de Despliegue**: Despliegue automático vía git push (Webhook de DigitalOcean)

**¿Por qué auto-despliegue?**
-  Configuración más simple - sin tokens de API o secretos que gestionar
-  DigitalOcean maneja todo el ciclo de vida del despliegue
-  Flujo de trabajo basado en git se alinea con prácticas estándar
-  Despliegues automáticos en cada push a ramas rastreadas
-  No se requieren secretos de GitHub Actions después de la configuración inicial
-  Más fácil de mantener y auditar

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flujo de Trabajo del Desarrollador          │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                  │
             │ git push (código)                │ Manual: Reentrenar Modelo
             ▼                                  ▼
┌─────────────────────────────┐  ┌──────────────────────────────────┐
│   GitHub Actions - CI       │  │  GitHub Actions - Reentreno Modelo│
│                             │  │                                  │
│  1. Escaneo de seguridad    │  │  1. Seleccionar entorno (manual) │
│  2. Chequeos calidad código │  │  2. Ejecutar pipeline de datos   │
│  3. Pruebas unitarias       │  │  3. Entrenar modelo              │
│  4.  Feedback Pasa/Falla  │  │  4. Commit modelo a git [skip ci]│
│                             │  │  5. Push al repositorio          │
│  NO entrenamiento modelo    │  │  6. Opcional: Crear release      │
│  NO despliegue              │  │                                  │
└─────────────────────────────┘  └──────────────┬───────────────────┘
                                                 │
                                                 │ Git Push (commit modelo)
                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              DigitalOcean App Platform                           │
│                                                                  │
│  1. Detecta git push vía webhook de GitHub                      │
│  2. Verifica que la rama coincida con la configuración de la app│
│  3. Clona repositorio (incluye modelo commiteado)               │
│  4. Lee especificación .do/app.yaml                             │
│  5. Construye imagen Docker desde Dockerfile                    │
│  6. Ejecuta chequeos de salud del contenedor                    │
│  7. Despliega a infraestructura en la nube (blue-green)         │
│  8. Actualiza enrutamiento (cero tiempo de inactividad)         │
│  9. Configura HTTPS y dominio                                   │
│ 10. La App está viva y sirviendo peticiones                     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
               Endpoint HTTPS Público
         https://fraud-detection-api.ondigitalocean.app
```

---

## Desglose del Flujo de Trabajo de Despliegue

### Flujo de Trabajo 1: Integración Continua (CI)

**Disparador**: Cada push o pull request a las ramas `master`, `staging` o `develop`

**Archivo de flujo de trabajo**: `.github/workflows/ci.yml`

**Propósito**: Validar calidad de código y asegurar que las pruebas pasen - NO entrenamiento de modelo o despliegue

**Trabajos:**
1. **Escaneo de Seguridad**: Chequeos de seguridad y linting de seguridad con Bandit
2. **Calidad de Código**: Formateo Black, importaciones isort, linting flake8
3. **Pruebas Unitarias**: pytest con reporte de cobertura

**Resultado**: Feedback rápido sobre calidad de código (típicamente se completa en 2-3 minutos)

---

### Flujo de Trabajo 2: Reentrenamiento de Modelo y Despliegue

**Disparador**: **Solo manual** vía UI de GitHub Actions

**Archivo de flujo de trabajo**: `.github/workflows/model-retrain.yml`

**Propósito**: Entrenar un nuevo modelo y desplegarlo a un entorno específico

**Cómo disparar:**
1. Ir a la pestaña GitHub Actions
2. Seleccionar flujo de trabajo "Model Retraining & Deployment"
3. Clic en "Run workflow"
4. Elegir:
   - **Environment**: development, staging, o production
   - **Create release**: true/false (release de GitHub opcional con artefactos)
5. Clic en botón "Run workflow"

**Trabajos:**

#### 1. Determinar Entorno
Mapea el entorno seleccionado a la rama apropiada:
- `production` → rama `master`
- `staging` → rama `staging`  
- `development` → rama `develop`

#### 2. Pipeline de Datos
- Hace checkout de la rama objetivo
- Ejecuta generación y procesamiento de datos
- Crea dataset de entrenamiento
- Sube artefactos para el siguiente trabajo

#### 3. Entrenamiento de Modelo
- Descarga artefactos de datos
- Entrena modelo con últimos datos
- Valida rendimiento del modelo
- Sube artefactos del modelo entrenado

#### 4. Desplegar a Git
- Descarga modelo entrenado
- Hace commit del modelo a la rama objetivo con `[skip ci]`
- Hace push al repositorio
- Dispara auto-despliegue de DigitalOcean vía webhook

#### 5. Crear Release (Opcional)
- Crea release de GitHub con artefactos del modelo
- Incluye metadatos de entrenamiento y métricas
- Etiqueta release con marca de tiempo y entorno

**Flujo de despliegue:**
```
Disparador Manual → Entrenar Modelo → Commit a Git → Push → Webhook DO → Auto-Despliegue
```

---

### Flujo de Trabajo 3: Monitoreo de Drift

**Disparador**: Diario a las 2 AM UTC (o manual)

**Archivo de flujo de trabajo**: `.github/workflows/drift-monitoring.yml`

**Propósito**: Monitorear drift de datos y alertar cuando se detecte

**Trabajos:**
1. **Detección de Drift**: Ejecuta pruebas estadísticas en datos de producción
2. **Crear Issue**: Crea automáticamente issue de GitHub si se detecta drift

**El issue incluye**:
- Resultados de detección de drift
- Marca de tiempo y enlace a ejecución del flujo de trabajo
- Instrucciones para reentrenamiento manual del modelo

---

### Paso 1: Cambios de Código (Pipeline CI)

Cuando haces push de código a cualquier rama:

```bash
git push origin develop  # Dispara flujo de trabajo CI solamente
```

GitHub Actions ejecuta flujo de trabajo CI (`.github/workflows/ci.yml`):
-  Escaneos de seguridad
-  Chequeos de calidad de código  
-  Pruebas unitarias
-  NO entrenamiento de modelo
-  NO despliegue

**Feedback rápido** - se completa en 2-3 minutos

---

### Paso 2: Reentrenamiento Manual de Modelo

Cuando necesitas reentrenar el modelo:

1. **Navegar a Actions**: Ir a repositorio → pestaña Actions
2. **Seleccionar flujo de trabajo**: Clic en "Model Retraining & Deployment"
3. **Ejecutar flujo de trabajo**: Clic en botón "Run workflow"
4. **Configurar**:
   - Seleccionar entorno (dev/staging/prod)
   - Elegir si crear release
5. **Ejecutar**: Clic en "Run workflow"

**Qué sucede:**

1. **Procesamiento de Datos**: Carga y prepara datos de entrenamiento
2. **Ingeniería de Características**: Crea características usando `selected_features.json`
3. **Entrenamiento de Modelo**: Entrena modelo(s) y selecciona el mejor
4. **Creación de Artefactos**: Empaqueta modelo y archivos de configuración
5. **Git Commit**: Hace commit del modelo a la rama objetivo con mensaje detallado
6. **Git Push**: Push dispara webhook de DigitalOcean
7. **Auto-despliegue**: DigitalOcean detecta push y despliega automáticamente

**Artefactos creados:**
- `trained-models/` - Archivos de modelo (*.joblib)
- `data/selected_features.json` - Configuración de características
- `data/training_summary.json` - Métricas de entrenamiento

---

### Paso 3: Commit de Modelo al Repositorio

```yaml
- name: Commit model to repository
  run: |
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git config user.name "github-actions[bot]"
    git add models/*.joblib data/selected_features.json
    git diff --staged --quiet || git commit -m "chore: update trained model [skip ci]"
    git push
```

**Puntos clave:**
- `[skip ci]` en mensaje de commit previene bucle infinito de CI (no disparará flujo de trabajo CI)
- Los archivos de modelo se commitean a git para control de versiones
- El push actualiza el repositorio con el último modelo entrenado
- Mensaje de commit detallado incluye entorno, marca de tiempo y enlace a ejecución del flujo de trabajo

---

### Paso 4: Despliegue Automático vía Webhook

Después de que el modelo es commiteado y pusheado, DigitalOcean detecta automáticamente el push vía webhook de GitHub.

**Configuración en `.do/app.yaml`:**
```yaml
services:
- name: api
  github:
    repo: iamdgarcia/mlops_template
    branch: master
    deploy_on_push: true  # Habilita despliegue automático
```

**Esto dispara:**
1. DigitalOcean detecta push a rama configurada (`master`, `staging`, o `develop`)
2. Clona el repositorio (incluyendo el modelo recién commiteado)
3. Lee `.do/app.yaml` para configuración de construcción
4. Construye imagen Docker desde `Dockerfile`
5. Despliega usando despliegue blue-green (cero tiempo de inactividad)
6. Ejecuta chequeos de salud en endpoint `/health`
7. Enruta tráfico al nuevo despliegue una vez saludable

**El despliegue típicamente se completa en 60-90 segundos.**

### Paso 5: Monitorear Despliegue

**Tablero DigitalOcean:**
- Ver progreso de despliegue: https://cloud.digitalocean.com/apps
- Chequear logs de construcción por errores
- Monitorear logs de ejecución
- Ver historial de despliegue

**Verificar despliegue:**
```bash
# Chequeo de salud
curl https://your-app.ondigitalocean.app/health

# Chequear info de app con doctl
doctl apps list
doctl apps get <APP_ID>
```

---

## Configuración Inicial vía doctl CLI

### Configuración Única Requerida

Antes de desplegar, necesitas crear las apps de DigitalOcean y autorizar acceso a GitHub.

**Usando el script automatizado:**

```bash
# Instalar y autenticar doctl
doctl auth init

# Ejecutar script de inicialización
./scripts/init_digitalocean_apps.sh
```

**Este script:**
1. Crea tres apps (producción, staging, desarrollo)
2. Configura cada una con la rama correcta y `deploy_on_push: true`
3. Configura autorización de repositorio GitHub
4. Genera `.env.digitalocean` con URLs e IDs de apps

**¡No se requieren secretos de GitHub!** Después de la configuración, los despliegues ocurren automáticamente vía git push.

---

## Configuración Multi-Entorno

### Tres Apps Separadas

El proyecto usa tres apps independientes de DigitalOcean:

1. **Producción** (`fraud-detection-api`)
   - Rama: `master`
   - Entorno: production
   - URL: https://fraud-detection-api-xxxxx.ondigitalocean.app

2. **Staging** (`fraud-detection-api-staging`)
   - Rama: `staging`
   - Entorno: staging
   - URL: https://fraud-detection-api-staging-xxxxx.ondigitalocean.app

3. **Desarrollo** (`fraud-detection-api-dev`)
   - Rama: `develop`
   - Entorno: development
   - URL: https://fraud-detection-api-dev-xxxxx.ondigitalocean.app

### Estrategia de Ramas

```
develop     →  App Desarrollo    (iteración rápida)
   ↓
staging     →  App Staging       (pruebas pre-producción)
   ↓
master      →  App Producción    (lanzamientos estables)
```

**Flujo de trabajo:**
1. Desarrollar características en rama `develop`
2. Probar en entorno de desarrollo
3. Fusionar a `staging` para pruebas de integración
4. Fusionar a `master` para lanzamiento a producción

---

## Script de Inicialización

### Usando `./scripts/init_digitalocean_apps.sh`

Este script automatizado crea las tres apps:

```bash
# Autenticar con DigitalOcean
doctl auth init

# Ejecutar inicialización
./scripts/init_digitalocean_apps.sh
```

**Lo que hace:**

1.  Valida prerrequisitos (doctl instalado, autenticado, archivo spec existe)
2.  Crea app de producción desde `.do/app.yaml`
3.  Crea app de staging (modificada para rama `staging`)
4.  Crea app de desarrollo (modificada para rama `develop`)
5.  Recupera IDs y URLs de apps
6.  Genera `.env.digitalocean` con toda la configuración
7.  Muestra instrucciones de configuración

**Salida:**
```
 Production App
   Name: fraud-detection-api
   ID:   abc123...
   URL:  https://fraud-detection-api-xxxxx.ondigitalocean.app
   Branch: master

 Staging App
   Name: fraud-detection-api-staging
   ID:   def456...
   URL:  https://fraud-detection-api-staging-xxxxx.ondigitalocean.app
   Branch: staging

 Development App
   Name: fraud-detection-api-dev
   ID:   ghi789...
   URL:  https://fraud-detection-api-dev-xxxxx.ondigitalocean.app
   Branch: develop
```

---

## Especificación de App (`.do/app.yaml`)

### Configuración Clave

```yaml
name: fraud-detection-api
region: nyc

services:
- name: api
  github:
    repo: iamdgarcia/mlops_template
    branch: master
    deploy_on_push: false  # Usamos despliegue explícito
  
  dockerfile_path: Dockerfile
  
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb  # $5/mes
  
  http_port: 8000
  
  health_check:
    http_path: /health
    initial_delay_seconds: 10
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  
  envs:
  - key: MODEL_PATH
    value: models/random_forest_final_model.joblib
    type: GENERAL
  - key: FEATURES_PATH
    value: data/selected_features.json
    type: GENERAL
```

**Ajustes importantes:**
- `deploy_on_push: false` - Controlamos despliegue vía GitHub Actions
- `instance_size_slug` - Controla costo ($5/mes para nivel básico)
- `health_check` - Asegura que la app esté saludable antes de enrutar tráfico

---

## Solución de Problemas

### Despliegue No Se Dispara

**Síntomas**: GitHub Actions corre pero el despliegue no ocurre

**Soluciones:**
1. Chequear que `DIGITALOCEAN_ACCESS_TOKEN` esté configurado correctamente
2. Verificar que el nombre de la app coincida en flujo de trabajo y DigitalOcean
3. Chequear logs de GitHub Actions por mensajes de error
4. Asegurar que la app existe: `doctl apps list`

### Chequeo de Salud Fallando

**Síntomas**: Despliegue se completa pero chequeo de salud retorna no-200

**Soluciones:**
1. Chequear logs de app: `doctl apps logs <app-id> --type run`
2. Verificar que archivo de modelo existe en repositorio: `ls models/*.joblib`
3. Chequear que Dockerfile construye exitosamente: `docker build -t test .`
4. Verificar endpoint de salud localmente: `curl http://localhost:8000/health`
5. Chequear consola de DigitalOcean por errores de construcción

### Error Modelo No Encontrado

**Síntomas**: `FileNotFoundError: models/random_forest_final_model.joblib`

**Soluciones:**
1. Verificar que modelo fue commiteado: `git log --oneline | grep "update trained model"`
2. Chequear .gitignore permite archivos de modelo (debería tener `# *.joblib` comentado)
3. Verificar paquete de despliegue incluye modelo: Chequear artefactos de GitHub Actions
4. Re-ejecutar pipeline de entrenamiento: Push cambio de código para disparar re-entrenamiento

### Despliegue Toma Demasiado Tiempo

**Síntomas**: Paso de despliegue expira o toma 5+ minutos

**Soluciones:**
1. Chequear página de estado de DigitalOcean: https://status.digitalocean.com
2. Reducir tamaño de imagen Docker (chequear optimización Dockerfile)
3. Usar `.dockerignore` para excluir archivos innecesarios
4. Considerar pre-construir imágenes base

---

## Mejores Prácticas

### 1. Usar `[skip ci]` en Commits de Modelo

Siempre incluir `[skip ci]` al commitear modelos para prevenir bucles infinitos de CI:

```bash
git commit -m "chore: update trained model [skip ci]"
```

### 2. Monitorear Logs de Despliegue

Chequear estado de despliegue en GitHub Actions:
- Ir a repositorio → pestaña Actions
- Seleccionar última ejecución de flujo de trabajo
- Revisar logs de trabajo "Deploy to Production/Staging/Dev"

### 3. Probar Antes de Producción

Seguir la estrategia de ramas:
1. Probar en entorno `develop` primero
2. Promover a `staging` para pruebas de integración
3. Desplegar a `master` solo cuando staging sea estable

### 4. Mantener Secretos Seguros

- Nunca commitear secretos al repositorio
- Rotar tokens de API periódicamente
- Usar reglas de protección de entorno de GitHub para producción

### 5. Versionar Tus Modelos

Commits de modelo proveen versionado automático:
```bash
git log --oneline models/
# Muestra historial de actualizaciones de modelo
```

Para rollback a un modelo previo:
```bash
git checkout <commit-hash> -- models/
git commit -m "chore: rollback to previous model [skip ci]"
```

---

## Comparación: Despliegue Explícito vs Auto-Despliegue

### Enfoque Actual: Auto-Despliegue (Basado en Git)

**Ventajas:**
-  Configuración más simple (no se necesita acción de despliegue)
-  DigitalOcean maneja ciclo de vida completo
-  No se necesitan secretos en GitHub Actions
-  Flujo de trabajo basado en git estándar
-  Más fácil de mantener y auditar

**Compromisos:**
-  Retrasos en detección de webhook (30-90 segundos)
-  Menos visibilidad en estado de despliegue desde GitHub Actions
-  Debe chequear tablero de DigitalOcean para progreso de despliegue

### Alternativa: Despliegue Explícito (GitHub Actions)

**Ventajas:**
-  Despliegue inmediato después de entrenamiento de modelo
-  Estado de despliegue claro en logs de GitHub Actions
-  Puede ejecutar chequeos de salud directamente en flujo de trabajo
-  Depuración más fácil con logs de acción

**Compromisos:**
-  Requiere DIGITALOCEAN_ACCESS_TOKEN en GitHub
-  Requiere secretos APP_URL para chequeos de salud
-  Flujo de trabajo más complejo
-  Potencial para doble despliegue si ambos habilitados

---

## Resumen

**Tres Flujos de Trabajo Separados:**

1. **CI (`ci.yml`)** - Corre en cada push/PR
   - Escaneos de seguridad, calidad de código, pruebas unitarias
   - Feedback rápido (2-3 minutos)
   - NO entrenamiento de modelo o despliegue

2. **Reentreno Modelo (`model-retrain.yml`)** - Disparador manual solamente
   - Elegir entorno (dev/staging/prod)
   - Entrenar modelo → Commit a git → Auto-despliegue
   - Opcional: Crear release de GitHub
   - Actualizaciones de modelo controladas, bajo demanda

3. **Monitoreo de Drift (`drift-monitoring.yml`)** - Diario a las 2 AM UTC
   - Detecta drift de datos
   - Crea issues de GitHub con alertas
   - Enlaces a flujo de trabajo de reentrenamiento manual

**Flujo de Despliegue:**
1. Push código → Dispara CI (pruebas solamente)
2. Manual: Disparar reentreno modelo → Entrena modelo
3. Modelo commiteado → Controlado por versión en git
4. Git push → Dispara webhook DigitalOcean
5. DigitalOcean → Construye y despliega automáticamente
6. Chequeo de salud → Valida despliegue (vía DigitalOcean)
7. API viva → Lista para peticiones

**Archivos Clave:**
- `.github/workflows/ci.yml` - Integración continua
- `.github/workflows/model-retrain.yml` - Reentrenamiento de modelo (manual)
- `.github/workflows/drift-monitoring.yml` - Chequeos de drift diarios
- `.do/app.yaml` - Configuración de App Platform con `deploy_on_push: true`
- `scripts/init_digitalocean_apps.sh` - Automatización de configuración
- `.env.digitalocean` - URLs e IDs de apps generados (no commiteado)

**Próximos Pasos:**
1. Ejecutar script de inicialización: `./scripts/init_digitalocean_apps.sh`
2. Push código para disparar CI y verificar que pruebas pasen
3. Disparar manualmente reentreno de modelo para despliegue inicial
4. Monitorear despliegue en consola DigitalOcean: https://cloud.digitalocean.com/apps
5. Verificar salud de API: `curl https://your-app.ondigitalocean.app/health`
