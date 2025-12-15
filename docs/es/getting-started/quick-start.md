# Plantilla MLOps - Configuración Rápida

## Qué Se Implementó

 **Configuración de App Platform** (`.do/app.yaml`)
- Definición del servicio API de detección de fraude
- Nivel básico ($5/mes) con 512MB RAM
- Chequeos de salud en endpoint `/health`
- Auto-despliegue en git push

 **Flujos de Trabajo de GitHub Actions**
- **CI** (`.github/workflows/ci.yml`):
  - Escaneos de seguridad, calidad de código, pruebas unitarias
  - Corre en cada push/PR
  - NO entrenamiento de modelo o despliegue
- **Reentreno Modelo** (`.github/workflows/model-retrain.yml`):
  - Disparador manual solamente
  - Entrena modelo y despliega al entorno seleccionado
  - Creación de release de GitHub opcional
- **Monitoreo de Drift** (`.github/workflows/drift-monitoring.yml`):
  - Detección de drift diaria a las 2 AM UTC
  - Crea issues de GitHub sobre alertas de drift

 **Documentación**
- Guía de despliegue completa (`DEPLOYMENT_GUIDE.md`)
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

### 2. Crear Apps de DigitalOcean
```bash
# Ejecutar el script de inicialización
./scripts/init_digitalocean_apps.sh

# Esto crea tres apps:
# - fraud-detection-api (producción - rama master)
# - fraud-detection-api-staging (staging - rama staging)
# - fraud-detection-api-dev (desarrollo - rama develop)
```

### 3. Push de Código (Dispara CI)
```bash
# Push de cambios de código - dispara flujo de trabajo CI solamente
git add .
git commit -m "Configurar despliegue DigitalOcean"
git push origin develop

# Mira la ejecución de CI en:
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
# 2. Commitear modelo a git
# 3. Disparar auto-despliegue de DigitalOcean
```

### 5. Acceder a Tu API
Después de que el despliegue se complete (60-90 segundos), obtendrás una URL como:
```
https://fraud-detection-api-xxxxx.ondigitalocean.app
```

Pruébalo:
```bash
# Chequeo de salud
curl https://TU-URL-APP/health

# Ver docs de API
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
- `.github/workflows/ci.yml` - Integración continua (pruebas solamente)
- `.github/workflows/model-retrain.yml` - Reentrenamiento manual de modelo
- `.github/workflows/drift-monitoring.yml` - Detección diaria de drift
- `DEPLOYMENT_GUIDE.md` - Documentación completa de despliegue
- `SETUP_SUMMARY.md` - Esta guía de referencia rápida
- `docs/DEPLOYMENT_MECHANICS.md` - Documentación técnica de arquitectura

### Archivos Modificados
- `README.md` - Sección de despliegue agregada
- `DEPLOYMENT_SUMMARY.md` - Actualizado para enfoque de auto-despliegue

### Archivos Eliminados
- `.github/workflows/mlops_pipeline.yml` - Dividido en flujos de trabajo separados

## Arquitectura de Despliegue

```
Push de Código → Flujo de Trabajo CI (pruebas solamente)
    ↓
Disparador Manual → Flujo de Trabajo Reentreno Modelo
    ↓
1. Ejecutar pipeline de datos
2. Entrenar modelo
3. Commitear modelo a git [skip ci]
4. Push al repositorio
    ↓
Webhook Git Push → DigitalOcean App Platform
    ↓
1. Clonar repositorio (con modelo)
2. Construir imagen Docker
3. Ejecutar chequeos de salud
4. Desplegar (cero tiempo de inactividad)
    ↓
API Viva en *.ondigitalocean.app

Diario: Monitoreo de Drift → Alertar si se detecta drift
```

## Resumen de Flujo de Trabajo

| Flujo de Trabajo | Disparador | Propósito | Duración |
|----------|---------|---------|----------|
| **CI** | Cada push/PR | Pruebas y chequeos de calidad | 2-3 min |
| **Reentreno Modelo** | Manual solamente | Entrenar y desplegar modelo | 8-12 min |
| **Monitoreo de Drift** | Diario 2 AM UTC | Detectar drift de datos | 1-2 min |

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
 Auto-despliegue en commit de modelo vía webhook git
 Monitoreo diario de drift con alertas de issues de GitHub
 HTTPS con certificado SSL gratuito  
 Monitoreo y logs integrados
 Chequeos de salud y auto-recuperación
 Despliegues sin tiempo de inactividad
 Releases de GitHub opcionales para versionado de modelos
 Despliegues específicos por entorno (prod/staging/dev)

## Solución de Problemas

**El despliegue falla con "Could not find app"**
- Solución: Autorizar GitHub con DigitalOcean (ver DEPLOYMENT_GUIDE.md Paso 3)

**El chequeo de salud falla**
- Esperar 1-2 minutos para que la app inicie completamente
- Chequear logs en tablero de DigitalOcean
- Verificar que archivos de modelo estén incluidos en paquete de despliegue

**Tiempo de espera de construcción o memoria insuficiente**
- Actualizar tamaño de instancia en `app.yaml`:
  ```yaml
  instance_size_slug: apps-s-1vcpu-1gb  # $12/mes
  ```

## Recursos de Soporte

- **Guía Completa**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **GitHub Actions**: https://github.com/iamdgarcia/mlops_template/actions
- **Tablero DigitalOcean**: https://cloud.digitalocean.com/apps
- **Docs App Platform**: https://docs.digitalocean.com/products/app-platform/

---

**¿Listo para desplegar?** ¡Sigue los 4 pasos de arriba! 
