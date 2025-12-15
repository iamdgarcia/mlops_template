# Curso MLOps: Guía de Solución de Problemas

## Problemas Comunes y Soluciones

### 1. Falla la Construcción de Docker
- **Solución:** Verifique la sintaxis del Dockerfile y asegúrese de que todas las dependencias estén listadas en `requirements.txt`.

### 2. La API No Responde
- **Solución:** Asegúrese de que el contenedor esté ejecutándose y el puerto 8000 esté abierto. Verifique los registros en busca de errores.

### 3. Falla el Pipeline de CI/CD
- **Solución:** Revise los registros de GitHub Actions. Asegúrese de que todos los archivos de prueba y scripts estén presentes y pasen localmente.

### 4. Modelo No Encontrado
- **Solución:** Confirme que existe un artefacto de modelo bajo `models/` y que el servidor apunta a él.
  - Rutas predeterminadas:
    - Aplicación completa: `configs/serving_config.yaml -> model.local_model_path` (por defecto `models/random_forest_final_model.joblib`)
    - Servidor mínimo: misma ruta predeterminada
  - Si falta, vuelva a ejecutar los notebooks 03 (entrenamiento) y 04 (inferencia).

### 5. Ruta de Importación para API
- **Síntoma:** `uvicorn` falla con `ModuleNotFoundError: src.serving.api`.
- **Solución:** Use la ruta de aplicación correcta:
  - Aplicación completa: `uvicorn src.serving.main:app --reload --port 8000`
  - Demo mínima: `uvicorn scripts.minimal_serve:app --reload --port 8000`

### 6. Desajuste de Características en Inferencia
- **Síntoma:** El notebook imprime "Missing features relative to model".
- **Solución:** Asegúrese de que `data/selected_features.json` coincida con el modelo entrenado.
  - Vuelva a ejecutar 02 (ingeniería de características) y 03 (entrenamiento); luego 04 (inferencia).
  - Evite editar manualmente `selected_features.json`.

### 7. Alertas de Monitoreo Activadas
- **Solución:** Revise los detalles de la alerta en el panel de control. Investigue la deriva de datos, caídas de rendimiento o problemas de salud del sistema.

## Obtener Ayuda
- Revise los notebooks del curso para detalles de implementación
- Consulte la documentación oficial para MLflow, FastAPI, Docker y GitHub Actions

---
Esta guía le ayuda a resolver rápidamente problemas comunes en su pipeline de MLOps.
