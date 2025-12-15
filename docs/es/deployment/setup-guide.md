# Guía de Despliegue en DigitalOcean App Platform

Esta guía le acompaña en el despliegue de la API de detección de fraude en DigitalOcean App Platform usando GitHub Actions.

## Resumen

El despliegue utiliza:
- **Plataforma**: DigitalOcean App Platform (PaaS)
- **CI/CD**: GitHub Actions para entrenamiento y versionado de modelos
- **Método de Despliegue**: Despliegue automático vía git push (webhook de DigitalOcean)
- **Costo**: ~$5/mes por entorno (Nivel Básico: 512MB RAM, 0.5 vCPU)
  - **¡GRATIS para estudiantes del curso!** Los nuevos registros obtienen $200 de crédito (40 meses gratis para 1 app)
- **Entornos**: Producción (master), Staging (staging), Desarrollo (develop)

## Prerrequisitos

1. **Repositorio de GitHub**: Código enviado a GitHub
2. **Cuenta de DigitalOcean**: Regístrese en [cloud.digitalocean.com](https://m.do.co/c/eddc62174250)
   -  **¡Los nuevos usuarios obtienen $200 en créditos gratis por 60 días!**
   - Más que suficiente para ejecutar este proyecto durante todo el curso
3. **doctl CLI**: Herramienta de línea de comandos de DigitalOcean ([guía de instalación](https://docs.digitalocean.com/reference/doctl/how-to/install/)) - solo para configuración inicial de la app

## Configuración Rápida (Automatizada)

Proporcionamos un script que crea automáticamente los tres entornos de aplicación:

```bash
# Asegúrese de estar autenticado con doctl primero
doctl auth init

# Ejecutar el script de inicialización
./scripts/init_digitalocean_apps.sh
```

Este script:
1.  Creará tres aplicaciones (producción, staging, desarrollo)
2.  Configurará cada aplicación con la rama correcta de GitHub y auto-despliegue
3.  Autorizará el acceso al repositorio de GitHub
4.  Generará URLs e IDs de la aplicación
5.  Creará el archivo `.env.digitalocean` con toda la configuración

**Después de ejecutar el script**, ¡el despliegue está listo! Simplemente haga push a `master`, `staging` o `develop` para activar el despliegue automático.

## Configuración Manual (Paso a Paso)

Si prefiere la configuración manual o el script no funciona para su entorno:

### Paso 1: Autenticar GitHub con App Platform

DigitalOcean App Platform necesita permiso para acceder a su repositorio de GitHub para el auto-despliegue.

**Opción A: Vía Panel de Control de DigitalOcean (Más fácil)**

1. Vaya a https://cloud.digitalocean.com/apps
2. Haga clic en **Create App**
3. Seleccione **GitHub** como fuente
4. Haga clic en **Authorize DigitalOcean** y conceda permisos
5. Puede cancelar la creación de la aplicación después de la autorización

**Opción B: Primer Despliegue (Automático)**

La primera vez que haga push a `master`, la GitHub Action le pedirá que autorice la conexión. Verifique los registros de despliegue para instrucciones.

### Paso 4: Desplegar Su Aplicación

Una vez configurados los secretos, el despliegue ocurre automáticamente:

```bash
# Desplegar a producción (rama master)
git add .
git commit -m "Habilitar despliegue en DigitalOcean"
git push origin master
```

**Flujo de Despliegue:**
1. GitHub Actions ejecuta todas las pruebas y validaciones
2. Entrena el modelo ML
3. Confirma el modelo entrenado en el repositorio
4. Git push activa el webhook de DigitalOcean
5. DigitalOcean construye automáticamente el contenedor Docker y despliega
6. App Platform ejecuta verificaciones de salud y enruta el tráfico

### Paso 5: Monitorear Despliegue

1. **GitHub Actions**: https://github.com/iamdgarcia/mlops_template/actions
   - Observe el flujo de trabajo `MLOps Pipeline`
   - Verifique los registros del trabajo `Deploy to Production`
   - Busque la URL de despliegue en los registros

2. **Panel de DigitalOcean**: https://cloud.digitalocean.com/apps
   - Vea el estado de la aplicación y registros
   - Acceda al historial de despliegue
   - Monitoree el uso de recursos

### Paso 6: Acceder a Su API Desplegada

Después de un despliegue exitoso, obtendrá una URL como:
```
https://fraud-detection-api-xxxxx.ondigitalocean.app
```

**Probar la API:**

```bash
# Verificación de salud
curl https://YOUR-APP-URL.ondigitalocean.app/health

# Documentación de API (Swagger UI)
open https://YOUR-APP-URL.ondigitalocean.app/docs

# Hacer una predicción
curl -X POST https://YOUR-APP-URL.ondigitalocean.app/predict \
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

## Despliegue Multi-Entorno

El pipeline soporta tres entornos:

| Rama | Entorno | Patrón de URL | Auto-Despliegue |
|--------|-------------|-------------|-------------|
| `master` | Producción | `fraud-detection-api.ondigitalocean.app` |  Sí |
| `staging` | Staging | `fraud-detection-api-staging.ondigitalocean.app` |  Sí |
| `develop` | Desarrollo | `fraud-detection-api-dev.ondigitalocean.app` |  Sí |

**Desplegar a staging:**
```bash
git checkout -b staging
git push origin staging
```

**Desplegar a desarrollo:**
```bash
git checkout -b develop
git push origin develop
```

## Archivos de Configuración

### `.do/app.yaml` - Especificación de App Platform

Define la configuración de la aplicación:
- **Nombre del servicio**: `fraud-detection-api`
- **Región**: NYC (Nueva York)
- **Tamaño de instancia**: `apps-s-1vcpu-0.5gb` ($5/mes)
- **Verificación de salud**: endpoint `/health`
- **Variables de entorno**: `PYTHONPATH`, `ENVIRONMENT`, `PYTHONUNBUFFERED`

**Actualizar tamaño de instancia** (si la app necesita más recursos):

Edite `.do/app.yaml`:
```yaml
instance_size_slug: apps-s-1vcpu-1gb  # $12/mes: 1GB RAM, 1 vCPU
```

Niveles disponibles:
- `apps-s-1vcpu-0.5gb` - $5/mes (512MB RAM)
- `apps-s-1vcpu-1gb` - $12/mes (1GB RAM)
- `apps-s-1vcpu-2gb` - $24/mes (2GB RAM)

### `.github/workflows/mlops_pipeline.yml` - Pipeline de CI/CD

Flujo de trabajo automatizado:
1. **Escaneo de seguridad** - Bandit, Safety
2. **Calidad de código** - Black, isort, flake8
3. **Pruebas unitarias** - pytest con cobertura
4. **Pipeline de datos** - Generar y validar datos
5. **Entrenamiento de modelo** - Entrenar y guardar modelo
6. **Despliegue** - Desplegar a DigitalOcean
7. **Verificaciones de salud** - Verificar despliegue

## Solución de Problemas

### Problema: "Error: Could not find app"

**Solución**: App Platform necesita autorización de GitHub. Siga el Paso 1 para autorizar.

### Problema: "Deployment not triggering"

**Síntomas**: Hizo push del código pero DigitalOcean no está desplegando

**Soluciones:**
1. Verifique que `deploy_on_push: true` esté configurado en `.do/app.yaml`
2. Verifique que GitHub esté autorizado en DigitalOcean: https://cloud.digitalocean.com/apps
3. Verifique la configuración de la aplicación en el panel de DigitalOcean para la configuración del webhook
4. Verifique que el git push fue exitoso y llegó a GitHub

### Problema: "Health check failed"

**Posibles causas:**
1. La aplicación todavía se está iniciando (espere 1-2 minutos)
2. Recursos insuficientes (actualice el tamaño de la instancia)
3. Archivo de modelo faltante (verifique la carga de artefactos)

**Pasos de depuración:**
```bash
# Verifique registros en el panel de DigitalOcean
# O use doctl CLI:
doctl apps list
doctl apps logs <APP_ID>
```

### Problema: "Build failed - Out of memory"

**Solución**: Actualice el tamaño de la instancia en `.do/app.yaml`:
```yaml
instance_size_slug: apps-s-1vcpu-1gb
```

### Problema: "Deployment timeout"

**Solución**: Aumente el retraso inicial de la verificación de salud en `.do/app.yaml`:
```yaml
health_check:
  initial_delay_seconds: 90  # Aumentado desde 60
```

## Gestión de Costos

### Configuración Actual
- **Instancia**: $5/mes (Nivel Básico)
- **Ancho de banda**: 1TB incluido
- **Minutos de construcción**: Ilimitados
- **Total**: ~$5/mes

### Consejos de Optimización de Costos

1. **Use una instancia más pequeña** para desarrollo:
   ```yaml
   # En .do/app.yaml para staging/dev
   instance_size_slug: apps-s-1vcpu-0.5gb
   ```

2. **Pause aplicaciones no utilizadas**:
   - Vaya al panel de App Platform
   - Seleccione app → Settings → Destroy
   - Redespliegue en cualquier momento desde GitHub

3. **Monitoree el uso**:
   - Verifique el panel de DigitalOcean para métricas
   - Configure alertas de facturación

## Características Avanzadas (Opcional)

### Dominio Personalizado

1. Agregue dominio en `.do/app.yaml`:
   ```yaml
   domains:
   - domain: api.yourdomain.com
     type: PRIMARY
   ```

2. Configure DNS:
   - Agregue registro CNAME apuntando a la URL de App Platform

### Variables de Entorno

Agregue secretos en el panel de DigitalOcean:
1. Vaya a App → Settings → App-Level Environment Variables
2. Agregue variables (ej., claves API, URLs de base de datos)
3. Marque como **Encrypted** para valores sensibles

### Escalado

Habilite auto-escalado en `.do/app.yaml`:
```yaml
instance_count: 1
autoscaling:
  min_instances: 1
  max_instances: 3
  metrics:
    cpu:
      percent: 75
```

### Monitoreo y Alertas

1. **Métricas integradas**: CPU, memoria, tasa de solicitudes
2. **Registros**: Tiempo real en el panel o vía `doctl apps logs`
3. **Alertas**: Configure en App Settings → Alerts

## Recursos Adicionales

- **Documentación de DigitalOcean App Platform**: https://docs.digitalocean.com/products/app-platform/
- **Referencia de Especificación de App**: https://docs.digitalocean.com/products/app-platform/reference/app-spec/
- **Documentación de GitHub Action**: https://github.com/digitalocean/app_action
- **doctl CLI**: https://docs.digitalocean.com/reference/doctl/

## Soporte

Para preguntas relacionadas con el curso o problemas de despliegue:
1. Verifique los registros de GitHub Actions
2. Revise los registros de la aplicación DigitalOcean
3. Consulte la sección de solución de problemas de esta guía
4. Contacte al instructor del curso

---

**Lista de Verificación de Inicio Rápido:**
- [ ] Cuenta de DigitalOcean creada
- [ ] Token de API generado
- [ ] Token agregado a Secretos de GitHub (`DIGITALOCEAN_ACCESS_TOKEN`)
- [ ] GitHub autorizado con App Platform
- [ ] Push a la rama `master` realizado
- [ ] Despliegue verificado en GitHub Actions
- [ ] Endpoint de salud de API probado
- [ ] Documentación Swagger UI accedida

**¡Despliegue exitoso!** 
