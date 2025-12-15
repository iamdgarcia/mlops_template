# Documentación de Plantilla MLOps

Documentación completa para el proyecto de Pipeline MLOps de Detección de Fraude.

##  Guía de Documentación

Sigue este orden de lectura para una comprensión completa del proyecto:

### 1 Comenzando (¡Empieza Aquí!)

**¿Nuevo en el proyecto? Empieza aquí:**

1. **[Requisitos](getting-started/requirements_es.md)** - Requisitos del sistema y prerrequisitos
2. **[Guía de Inicio Rápido](getting-started/quick-start_es.md)** - Ponte en marcha en 15 minutos
3. **[Guía de Usuario](getting-started/user-guide_es.md)** - Guía completa para usuarios

**Ruta recomendada**: Requisitos → Inicio Rápido → Guía de Usuario

---

### 2 Despliegue

**Configurando despliegue en producción:**

1. **[Descripción General de Despliegue](deployment/overview.md)** - Arquitectura de despliegue de alto nivel
2. **[Guía de Configuración](deployment/setup-guide.md)** - Despliegue paso a paso en DigitalOcean
3. **[Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md)** - Profundización técnica en flujos de trabajo
4. **[Cambios en Flujo de Trabajo](deployment/workflow-changes.md)** - Entendiendo los pipelines CI/CD
5. **[Estrategia de Artefactos](deployment/artifacts-strategy.md)** - Cómo se versionan los modelos
6. **[Solución de Problemas](deployment/troubleshooting.md)** - Problemas comunes y soluciones

**Ruta recomendada**: Descripción General → Guía de Configuración → Mecánica de Despliegue

---

### 3 Uso de API

**Trabajando con la API desplegada:**

1. **[Guía de API](api/guide.md)** - Referencia completa de API y ejemplos

---

### 4 Desarrollo

**Para contribuidores y desarrolladores:**

1. **[Arquitectura](architecture_es.md)** - Arquitectura del sistema y decisiones de diseño
2. **[Changelog](CHANGELOG.md)** - Historial de versiones y cambios

---

##  Enlaces Rápidos

### Para Usuarios Primerizos
- **Quiero entender qué hace este proyecto** → [README](overview.md)
- **Quiero ejecutar el proyecto localmente** → [Inicio Rápido](getting-started/quick-start_es.md)
- **Quiero desplegar a producción** → [Guía de Configuración](deployment/setup-guide.md)

### Para Desarrolladores
- **Quiero entender la arquitectura** → [Arquitectura](architecture_es.md)
- **Quiero contribuir** → [README](overview.md#contributing)
- **Necesito solucionar problemas** → [Solución de Problemas](deployment/troubleshooting.md)

### Para Operaciones
- **Necesito reentrenar el modelo** → [Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md#flujo-de-trabajo-2-reentrenamiento-de-modelo-y-despliegue)
- **Necesito monitorear drift** → [Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md#flujo-de-trabajo-3-monitoreo-de-drift)
- **Necesito chequear estado de despliegue** → [Solución de Problemas](deployment/troubleshooting.md)

---

##  Estructura de Documentación

```
docs/
├── README_es.md                       # Este archivo - índice de documentación
├── architecture_es.md                 # Arquitectura del sistema
├── DEPLOYMENT_MECHANICS_es.md         # Guía técnica de despliegue
│
├── getting-started/
│   ├── requirements_es.md             # Prerrequisitos y requisitos del sistema
│   ├── quick-start_es.md              # Guía de configuración de 15 minutos
│   └── user-guide_es.md               # Manual de usuario completo
│
├── deployment/
│   ├── overview.md                    # Descripción general de arquitectura de despliegue
│   ├── setup-guide.md                 # Configuración de despliegue DigitalOcean
│   ├── workflow-changes.md            # Documentación de flujo de trabajo CI/CD
│   ├── artifacts-strategy.md          # Enfoque de versionado de modelos
│   ├── troubleshooting.md             # Problemas comunes y arreglos
│   └── legacy-guide.md                # Guía de despliegue antigua (obsoleta)
│
├── api/
│   └── guide.md                       # Referencia de API y ejemplos
│
└── development/
    └── (futuro: guía de contribución, estándares de código, etc.)
```

---

##  Rutas de Aprendizaje

### Ruta 1: Viaje del Usuario (Solo quiero usar la API)
1. [README](overview.md) - Descripción General
2. [Inicio Rápido](getting-started/quick-start_es.md) - Configuración
3. [Guía de API](api/guide.md) - Uso

**Tiempo**: ~30 minutos

---

### Ruta 2: Viaje de Despliegue (Quiero desplegar el mío propio)
1. [README](overview.md) - Descripción General
2. [Requisitos](getting-started/requirements_es.md) - Prerrequisitos
3. [Descripción General de Despliegue](deployment/overview.md) - Arquitectura
4. [Guía de Configuración](deployment/setup-guide.md) - Configuración paso a paso
5. [Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md) - Detalles técnicos

**Tiempo**: ~2 horas

---

### Ruta 3: Viaje del Desarrollador (Quiero contribuir o personalizar)
1. [README](overview.md) - Descripción General
2. [Arquitectura](architecture_es.md) - Diseño del sistema
3. [Guía de Usuario](getting-started/user-guide_es.md) - Características y uso
4. [Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md) - Flujos de trabajo CI/CD
5. [Inicio Rápido](getting-started/quick-start_es.md) - Desarrollo local

**Tiempo**: ~3 horas

---

##  Descripción General del Flujo de Trabajo

### Integración Continua (CI)
Cada push de código dispara pruebas automatizadas:
- Escaneos de seguridad
- Chequeos de calidad de código
- Pruebas unitarias

**Sin entrenamiento de modelo, sin despliegue** - solo feedback rápido (~2-3 minutos)

### Reentrenamiento de Modelo (Manual)
Entrenar y desplegar modelos bajo demanda:
1. Ir a GitHub Actions
2. Seleccionar "Model Retraining & Deployment"
3. Elegir entorno (dev/staging/prod)
4. Disparar flujo de trabajo

**Flujo completo**: Pipeline de datos → Entrenamiento → Commit Git → Auto-despliegue

### Monitoreo de Drift (Diario)
Detección automática de drift:
- Corre diariamente a las 2 AM UTC
- Crea issues de GitHub sobre drift
- Incluye instrucciones de reentrenamiento

---

##  Recursos Externos

- **Docs DigitalOcean**: https://docs.digitalocean.com/products/app-platform/
- **GitHub Actions**: https://docs.github.com/en/actions
- **FastAPI**: https://fastapi.tiangolo.com/
- **MLflow**: https://mlflow.org/docs/latest/index.html

---

##  ¿Necesitas Ayuda?

1. **Revisa los docs** - La mayoría de las preguntas se responden aquí
2. **Busca issues** - Alguien puede haber tenido el mismo problema
3. **Guía de solución de problemas** - [deployment/troubleshooting.md](deployment/troubleshooting.md)
4. **Crea un issue** - Si todo lo demás falla

---

##  Tarjeta de Referencia Rápida

| Tarea | Documentación |
|------|---------------|
| Configuración inicial | [Inicio Rápido](getting-started/quick-start_es.md) |
| Desplegar a producción | [Guía de Configuración](deployment/setup-guide.md) |
| Usar la API | [Guía de API](api/guide.md) |
| Reentrenar modelo | [Mecánica de Despliegue](DEPLOYMENT_MECHANICS_es.md#flujo-de-trabajo-2-reentrenamiento-de-modelo-y-despliegue) |
| Chequear despliegue | [Solución de Problemas](deployment/troubleshooting.md) |
| Entender arquitectura | [Arquitectura](architecture_es.md) |
| Arreglar problemas comunes | [Solución de Problemas](deployment/troubleshooting.md) |

---

**Última Actualización**: 12 de Diciembre, 2025  
**Versión de Documentación**: 2.0
