# Curso MLOps: Guía de Despliegue

## Resumen
Esta guía explica cómo desplegar el pipeline completo de MLOps, incluyendo el servicio de modelos, la contenedorización y la automatización de CI/CD.

## Prerrequisitos
- Docker instalado
- Python 3.8+
- Cuenta de GitHub (para CI/CD)

## Pasos

### 1. Construir y Ejecutar el Contenedor Docker
```
docker build -t fraud-detection:latest .
docker run -p 8000:8000 fraud-detection:latest
```

### 2. Desplegar la API del Modelo
- La aplicación FastAPI se sirve en `http://localhost:8000`
- Endpoint de verificación de salud: `/health`
- Endpoint de predicción: `/predict`

### 3. Habilitar CI/CD
- Enviar código a GitHub
- El flujo de trabajo de GitHub Actions (`.github/workflows/mlops_pipeline.yml`) ejecutará pruebas y desplegará automáticamente

### 4. Monitoreo
- Monitorear registros y métricas a través del notebook del panel de control
- Las alertas e informes se generan automáticamente

## Solución de Problemas
- Ver `troubleshooting.md` para problemas comunes

---
Esta guía asegura un despliegue fluido desde el desarrollo hasta la producción para su sistema de ML.
