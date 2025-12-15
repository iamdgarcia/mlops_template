# Resumen de Despliegue

## Referencia Rápida

Este documento proporciona una visión general de alto nivel de la arquitectura de despliegue. Para información detallada, consulte la documentación vinculada.

## Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI/CD                     │
│                                                               │
│  1. El push de código activa el flujo de trabajo             │
│  2. Entrenar modelo con los últimos datos                    │
│  3. Empaquetar modelo + código como artefacto                │
│  4. Descargar artefacto y confirmar en git [skip ci]         │
│  5. Enviar al repositorio                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Git Push (webhook)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              DigitalOcean App Platform                       │
│                                                               │
│  1. Detecta git push vía webhook de GitHub                   │
│  2. Clona el repositorio (incluye modelo)                    │
│  3. Construye imagen Docker                                  │
│  4. Despliega en infraestructura en la nube                  │
│  5. Configura verificaciones de salud y HTTPS                │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
               Endpoint HTTPS Público
         https://your-app.ondigitalocean.app
```

## Características Clave

 **Auto-Despliegue basado en Git**: Despliegue automático al hacer git push - no se requieren secretos  
 **Versionado de Modelos**: Modelos confirmados en git para control de versiones  
 **Cero tiempo de inactividad**: DigitalOcean maneja el despliegue blue-green  
 **Verificaciones de Salud**: Validación automatizada después del despliegue  
 **Multi-entorno**: Producción, Staging, Desarrollo  
 **Rentable**: ~$5/mes (GRATIS con crédito de $200)  
 **Configuración Simple**: Sin tokens de API o secretos que gestionar después de la configuración inicial

## Configuración Inicial

**Configuración única usando doctl CLI:**

```bash
# Instalar y autenticar doctl (DigitalOcean CLI)
doctl auth init

# Ejecutar el script de inicialización
./scripts/init_digitalocean_apps.sh
```

Esto crea los tres entornos de aplicación y configura el auto-despliegue. ¡No se necesitan secretos de GitHub ni tokens de API en su flujo de trabajo!

## Flujo de Trabajo de Despliegue

### Producción (rama master)
```bash
git push origin master
```
1. Activa el flujo de trabajo de GitHub Actions
2. Entrena el modelo, confirma en el repositorio
3. Git push activa el webhook de DigitalOcean
4. DigitalOcean auto-construye y despliega en ~90 segundos
5. App Platform ejecuta verificaciones de salud automáticamente

### Staging (rama staging)
```bash
git push origin staging
```
Mismo proceso, despliega en el entorno de staging

### Desarrollo (rama develop)
```bash
git push origin develop
```
Mismo proceso, despliega en el entorno de desarrollo

## Índice de Documentación

| Documento | Propósito |
|----------|---------|
| [README.md](./README.md) | Resumen del proyecto e inicio rápido |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Instrucciones de configuración paso a paso |
| [DEPLOYMENT_MECHANICS.md](./docs/DEPLOYMENT_MECHANICS.md) | Detalles técnicos de la arquitectura |
| [DEPLOYMENT_ARTIFACTS.md](./DEPLOYMENT_ARTIFACTS.md) | Por qué los modelos se confirman en git |
| [API_GUIDE.md](./API_GUIDE.md) | Uso de la API y ejemplos |

## Desglose de Costos

**DigitalOcean App Platform - Nivel Básico:**
- 512 MB RAM
- 0.5 vCPU
- **Costo**: $5.00/mes por entorno

**Para estudiantes del curso:**
- Regístrese en https://m.do.co/c/eddc62174250
- Obtenga $200 de crédito gratis (60 días)
- **40 meses GRATIS** si ejecuta 1 entorno
- **13 meses GRATIS** si ejecuta 3 entornos (prod + staging + dev)

## Lista de Verificación de Despliegue

Antes de su primer despliegue:

- [ ] Crear cuenta en DigitalOcean (use el enlace de afiliado para crédito de $200)
- [ ] Instalar doctl CLI: `brew install doctl` o ver [guía de instalación](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- [ ] Autenticar doctl: `doctl auth init`
- [ ] Ejecutar script de inicialización: `./scripts/init_digitalocean_apps.sh`
- [ ] Autorizar a DigitalOcean para acceder al repositorio de GitHub (hecho durante el script)
- [ ] Hacer push a la rama `master` para activar el primer despliegue
- [ ] Monitorear el despliegue en el panel de DigitalOcean: https://cloud.digitalocean.com/apps
- [ ] Probar endpoints de la API usando API_GUIDE.md

## Monitoreo de Despliegues

**GitHub Actions:**
- Ver ejecuciones de flujo de trabajo: https://github.com/iamdgarcia/mlops_template/actions
- Verificar estado de entrenamiento del modelo y confirmación

**Panel de DigitalOcean:**
- Ver estado de despliegue: https://cloud.digitalocean.com/apps
- Verificar registros de construcción y registros de ejecución
- Monitorear uso de recursos y verificaciones de salud

## Solución de Problemas

**¿El despliegue no se activa?**
→ Verifique [DEPLOYMENT_MECHANICS.md](./docs/DEPLOYMENT_MECHANICS.md#troubleshooting)

**¿Falla la verificación de salud?**
→ Verifique la consola de DigitalOcean: https://cloud.digitalocean.com/apps

**¿Error de modelo no encontrado?**
→ Asegúrese de que los modelos estén confirmados en git (verifique .gitignore)

**¿Necesita más ayuda?**
→ Vea la guía completa de solución de problemas en DEPLOYMENT_GUIDE.md

## Próximos Pasos

1. Complete la configuración inicial usando [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Entienda la arquitectura en [DEPLOYMENT_MECHANICS.md](./docs/DEPLOYMENT_MECHANICS.md)
3. Pruebe su API usando [API_GUIDE.md](./API_GUIDE.md)
4. Monitoree su despliegue en https://cloud.digitalocean.com/apps

---

 **Consejo Pro**: ¡Marque esta página para referencia rápida durante el curso!
