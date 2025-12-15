# Plantilla MLOps - Configuración Rápida

## Qué se Implementó

 **Configuración de App Platform** (`.do/app.yaml`)
- Definición del servicio API de detección de fraude
- Nivel básico ($5/mes) con 512MB RAM
- Comprobaciones de salud en el endpoint `/health`
- Auto-despliegue al hacer git push

 **Flujos de Trabajo de GitHub Actions**
- **CI** (`.github/workflows/ci.yml`):
  - Escaneos de seguridad, calidad de código, pruebas unitarias
  - Se ejecuta en cada push/PR
  - NO entrena modelos ni despliega
- **Reentrenamiento de Modelo** (`.github/workflows/model-retrain.yml`):
  - Solo activación manual
  - Entrena el modelo y despliega al entorno seleccionado
  - Creación opcional de release en GitHub
- **Monitoreo de Deriva** (`.github/workflows/drift-monitoring.yml`):
  - Detección diaria de deriva a las 2 AM UTC
  - Crea issues en GitHub sobre alertas de deriva

 **Documentación**
- Guía completa de despliegue (`DEPLOYMENT_GUIDE.md`)
- Documentación técnica de mecánica (`docs/DEPLOYMENT_MECHANICS.md`)
- README actualizado con sección de despliegue
- Consejos de solución de problemas incluidos

## Próximos Pasos para Desplegar

>  **¡Obtén $200 de Crédito Gratis!** Regístrate en https://m.do.co/c/eddc62174250 para recibir $200 en créditos gratis por 60 días - ¡ejecuta todo este proyecto del curso gratis!

### 1. Instalar y Autenticar doctl CLI
```bash
# macOS
brew install doctl

# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
tar xf ~/doctl-1.94.0-linux-amd64.tar.gz
sudo mv ~/doctl /usr/local/bin

# Autenticar
doctl auth init
```

### 2. Crear Apps en DigitalOcean
```bash
# Ejecutar el script de inicialización
./scripts/init_digitalocean_apps.sh

# Esto crea tres apps:
# - fraud-detection-api (producción - rama master)
# - fraud-detection-api-staging (staging - rama staging)
# - fraud-detection-api-dev (desarrollo - rama develop)
```

### 3. Subir Código (Activa CI)
```bash
# Subir cambios de código - activa solo flujo de trabajo CI
git add .
git commit -m "Configurar despliegue DigitalOcean"
git push origin develop

# Ver ejecución de CI en:
# https://github.com/iamdgarcia/mlops_template/actions
```

### 4. Entrenar y Desplegar Modelo (Manual)
```bash
# Ir a GitHub Actions:
# https://github.com/iamdgarcia/mlops_template/actions/workflows/model-retrain.yml

# Clic en "Run workflow"
# - Seleccionar entorno: development
# - Crear release: false (opcional)
# - Clic en botón "Run workflow"

# Esto hará:
# 1. Entrenar un nuevo modelo
# 2. Hacer commit del modelo a git
# 3. Activar auto-despliegue de DigitalOcean
```

### 5. Acceder a Tu API
Después de que el despliegue se complete (60-90 segundos), obtendrás una URL como:
```
https://fraud-detection-api-xxxxx.ondigitalocean.app
```

Pruébalo:
```bash
# Comprobación de salud
curl https://TU-URL-APP/health

# Ver documentación API
open https://TU-URL-APP/docs

# Hacer una predicción
curl -X POST https://TU-URL-APP/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.0,
    "merchant_category": "retail",
    "transaction_type": "purchase",
    "location": "US",
    "device_type": "mobile",
    "hour_of_day": 14,
    "day_of_week": 3,
    "user_transaction_frequency": 10.5,
    "user_avg_amount": 250.0,
    "user_transaction_count": 25
  }'
```

## Archivos Modificados/Creados

### Nuevos Archivos
- `.do/app.yaml` - Configuración de DigitalOcean App Platform
- `.github/workflows/ci.yml` - Integración continua (solo pruebas)
- `.github/workflows/model-retrain.yml` - Reentrenamiento manual de modelo
- `.github/workflows/drift-monitoring.yml` - Detección diaria de deriva
- `DEPLOYMENT_GUIDE.md` - Documentación completa de despliegue
- `SETUP_SUMMARY.md` - Esta guía de referencia rápida
- `docs/DEPLOYMENT_MECHANICS.md` - Documentación de arquitectura técnica

### Archivos Modificados
- `README.md` - Sección de despliegue añadida
- `DEPLOYMENT_SUMMARY.md` - Actualizado para enfoque de auto-despliegue

### Archivos Eliminados
- `.github/workflows/mlops_pipeline.yml` - Dividido en flujos de trabajo separados

## Arquitectura de Despliegue

```
Subida de Código → Flujo de Trabajo CI (solo pruebas)
    ↓
Activación Manual → Flujo de Trabajo Reentrenamiento Modelo
    ↓
1. Ejecutar pipeline de datos
2. Entrenar modelo
3. Hacer commit del modelo a git [skip ci]
4. Subir al repositorio
    ↓
Webhook de Git Push → DigitalOcean App Platform
    ↓
1. Clonar repositorio (con modelo)
2. Construir imagen Docker
3. Ejecutar comprobaciones de salud
4. Desplegar (cero tiempo de inactividad)
    ↓
API en vivo en *.ondigitalocean.app

Diario: Monitoreo de Deriva → Alerta si se detecta deriva
```

## Resumen de Flujos de Trabajo

| Flujo de Trabajo | Activador | Propósito | Duración |
|----------|---------|---------|----------|
| **CI** | Cada push/PR | Pruebas y comprobaciones de calidad | 2-3 min |
| **Reentrenamiento Modelo** | Solo manual | Entrenar y desplegar modelo | 8-12 min |
| **Monitoreo de Deriva** | Diario 2 AM UTC | Detectar deriva de datos | 1-2 min |

## Desglose de Costos

| Componente | Costo |
|-----------|------|
| App Platform (Nivel básico) | $5/mes |
| Ancho de banda (1TB incluido) | $0 |
| Certificado SSL | $0 |
| GitHub Actions (2000 min/mes gratis) | $0 |
| **Total** | **$5/mes** |

**Con $200 de crédito**: ¡40 meses gratis para 1 entorno!

## Características Habilitadas

 CI automático en cada push (sin despliegue)
 Reentrenamiento manual de modelo con selección de entorno
 Auto-despliegue al hacer commit del modelo vía webhook de git
 Monitoreo diario de deriva con alertas de issues en GitHub
 HTTPS con certificado SSL gratuito
 Monitoreo y registros integrados
 Comprobaciones de salud y auto-recuperación
 Despliegues con cero tiempo de inactividad
 Releases opcionales de GitHub para versionado de modelos
 Despliegues específicos por entorno (prod/staging/dev)

## Solución de Problemas

**El despliegue falla con "Could not find app"**
- Solución: Autorizar GitHub con DigitalOcean (ver DEPLOYMENT_GUIDE.md Paso 3)

**Falla la comprobación de salud**
- Esperar 1-2 minutos para que la app inicie completamente
- Revisar registros en el panel de DigitalOcean
- Verificar que los archivos del modelo estén incluidos en el paquete de despliegue

**Tiempo de espera de construcción o falta de memoria**
- Actualizar tamaño de instancia en `app.yaml`:
  ```yaml
  instance_size_slug: apps-s-1vcpu-1gb  # $12/mes
  ```

## Recursos de Soporte

- **Guía Completa**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **GitHub Actions**: https://github.com/iamdgarcia/mlops_template/actions
- **Panel de DigitalOcean**: https://cloud.digitalocean.com/apps
- **Documentación de App Platform**: https://docs.digitalocean.com/products/app-platform/

---

**¿Listo para desplegar?** ¡Sigue los 4 pasos anteriores! 
