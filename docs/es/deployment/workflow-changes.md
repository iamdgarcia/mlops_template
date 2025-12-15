# Cambios en el Flujo de Trabajo de GitHub Actions

## Resumen

El pipeline de MLOps ha sido refactorizado en tres flujos de trabajo separados y enfocados para una mejor separación de preocupaciones y control.

## Nueva Estructura de Flujo de Trabajo

### 1. Flujo de Trabajo CI (`ci.yml`)
**Disparador**: Cada push o pull request a ramas principales
**Propósito**: Retroalimentación rápida sobre la calidad del código
**Trabajos**:
- Escaneo de vulnerabilidades de seguridad
- Verificaciones de calidad de código (black, isort, flake8)
- Pruebas unitarias con cobertura

**Duración**: ~2-3 minutos
**Sin entrenamiento de modelo ni despliegue**

### 2. Flujo de Trabajo de Reentrenamiento de Modelo (`model-retrain.yml`)
**Disparador**: Solo manual (workflow_dispatch)
**Propósito**: Entrenar y desplegar modelos bajo demanda
**Opciones**:
- Seleccionar entorno (desarrollo/staging/producción)
- Elegir si crear lanzamiento en GitHub

**Trabajos**:
1. Determinar entorno y mapear a rama
2. Ejecutar pipeline de datos
3. Entrenar modelo
4. Confirmar modelo en git
5. Auto-desplegar vía webhook de DigitalOcean
6. (Opcional) Crear lanzamiento en GitHub

**Duración**: ~8-12 minutos

### 3. Flujo de Trabajo de Monitoreo de Deriva (`drift-monitoring.yml`)
**Disparador**: Diariamente a las 2 AM UTC (o manual)
**Propósito**: Detectar deriva de datos y alertar
**Acciones**:
- Ejecutar pruebas de detección de deriva
- Crear problema en GitHub si se detecta deriva
- El problema incluye instrucciones para reentrenamiento manual

**Duración**: ~1-2 minutos

## Beneficios Clave

 **CI Más Rápido**: Los cambios de código obtienen retroalimentación de prueba en 2-3 minutos
 **Actualizaciones de Modelo Controladas**: Reentrenar solo cuando sea necesario, activado manualmente
 **Selección de Entorno**: Desplegar a dev/staging/prod según sea necesario
 **Sin Secretos Requeridos**: Auto-despliegue vía webhook de git
 **Monitoreo Proactivo**: Detección diaria de deriva con alertas
 **Versionado de Modelos**: Lanzamientos opcionales en GitHub con artefactos

## Cómo Usar

### Ejecutando CI (Automático)
```bash
# Solo envíe código - CI se ejecuta automáticamente
git push origin develop
```

### Reentrenando un Modelo (Manual)
1. Vaya a la pestaña GitHub Actions
2. Seleccione "Model Retraining & Deployment"
3. Haga clic en "Run workflow"
4. Elija entorno y opciones
5. Haga clic en el botón "Run workflow"

### Verificando Deriva (Automático Diario)
- Se ejecuta automáticamente a las 2 AM UTC
- Verifique la pestaña Issues para alertas de deriva
- Siga las instrucciones del problema para reentrenar

## Notas de Migración

**Eliminado**:
- `.github/workflows/mlops_pipeline.yml` (flujo de trabajo monolítico)

**Agregado**:
- `.github/workflows/ci.yml`
- `.github/workflows/model-retrain.yml`
- `.github/workflows/drift-monitoring.yml`

**Actualizado**:
- `docs/DEPLOYMENT_MECHANICS.md` - Refleja la nueva estructura de flujo de trabajo
- `SETUP_SUMMARY.md` - Instrucciones de configuración actualizadas
- `DEPLOYMENT_GUIDE.md` - Enfoque de auto-despliegue
- `README.md` - Sección de despliegue simplificada

## Flujo de Despliegue

```
Push del Desarrollador → CI (pruebas) 
                 ↓
            (código es bueno)
                 ↓
Disparador Manual → Reentrenamiento de Modelo
                 ↓
            Entrenar Modelo
                 ↓
         Confirmar en Git [skip ci]
                 ↓
            Git Push
                 ↓
        Webhook DO Detecta
                 ↓
         Auto-Despliegue 
```

## Ejemplo de Ejecución de Flujo de Trabajo

**Escenario**: Reentrenar modelo de producción

1. **Disparador**: Ir a Actions → Model Retraining & Deployment → Run workflow
2. **Seleccionar**: Entorno: production, Crear lanzamiento: true
3. **Ejecutar**: Clic en "Run workflow"
4. **Monitorear**: Ver progreso en pestaña Actions
5. **Resultado**: Modelo entrenado, confirmado en master, desplegado a producción
6. **Lanzamiento**: Lanzamiento en GitHub creado con artefactos del modelo
7. **Verificar**: Verificar app en https://fraud-detection-api.ondigitalocean.app/health

**Línea de Tiempo**:
- 0:00 - Inicia flujo de trabajo
- 2:00 - Pipeline de datos completo
- 8:00 - Entrenamiento de modelo completo
- 9:00 - Modelo confirmado en git
- 9:30 - Inicia despliegue en DigitalOcean
- 11:00 - Despliegue completo, app saludable
- 12:00 - Lanzamiento en GitHub creado

## Solución de Problemas

**CI falla en push**:
- Verifique escaneo de seguridad, calidad de código o fallas de prueba
- Corrija problemas y envíe de nuevo

**Reentrenamiento de modelo falla**:
- Verifique registros de flujo de trabajo en pestaña Actions
- Verifique que el pipeline de datos se ejecutó exitosamente
- Asegúrese de que el entrenamiento del modelo se completó

**Despliegue no ocurre**:
- Verifique `deploy_on_push: true` en `.do/app.yaml`
- Verifique estado de despliegue en panel de DigitalOcean
- Asegúrese de que el modelo fue confirmado en git

**Alertas de deriva demasiado ruidosas**:
- Ajuste umbrales de detección de deriva en `drift-monitoring.yml`
- Considere ejecuciones semanales en lugar de diarias
