# Registro de Cambios

Todos los cambios notables en la Plantilla de Detección de Fraude MLOps se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-11

### Añadido - Mejoras de Preparación para Producción

#### Infraestructura
- **`.dockerignore`**: Construcciones de Docker optimizadas excluyendo archivos innecesarios (notebooks, tests, .git)
- **`pyproject.toml`**: Configuración adecuada del paquete Python con setuptools, puntos de entrada y metadatos
- **`requirements-dev.txt`**: Dependencias de desarrollo separadas de los requisitos de producción
- **`.env.example`**: Documentación completa de variables de entorno para todas las opciones de configuración
- **`data/.gitignore`**: Prevención de commit de archivos de datos grandes preservando la estructura de directorios

#### CI/CD y Calidad
- **`.github/dependabot.yml`**: Actualizaciones automatizadas de dependencias y escaneo de seguridad para pip, GitHub Actions y Docker
- **`pytest.ini`**: Configuración completa de pruebas con marcadores, umbrales de cobertura y registro
- **`.coveragerc`**: Configuración detallada de cobertura de código con cobertura de ramas y exclusiones
- **Pipeline CI/CD completo**: Flujo de trabajo de 7 trabajos con calidad de código, pruebas, entrenamiento, construcción de Docker y despliegues

#### Documentación
- **Fuente única de verdad para ingeniería de características**: Patrón de arquitectura documentado asegurando paridad entre entrenamiento/servicio
- **Diagramas de arquitectura**: Diagramas de flujo Mermaid añadidos mostrando flujo de datos e interacciones de componentes
- **Expansión de guía de usuario**: Patrones de ingeniería de características y estrategias de validación añadidos
- **Este CHANGELOG.md**: Historial de versiones y notas de lanzamiento

#### Pruebas
- **`tests/test_feature_parity.py`**: Suite de pruebas completa (330+ líneas, 14 métodos de prueba) validando consistencia de ingeniería de características entre contextos de entrenamiento, inferencia y servicio
- **Pruebas de casos límite**: Dataframes vacíos, columnas faltantes, procesamiento de una sola fila
- **Pruebas de integración**: Integración de InferencePipeline y FastAPI con FeatureEngineer

### Cambiado

#### Configuración
- **`.pre-commit-config.yaml`**: Referencia rota arreglada a `test_integration.py` inexistente
- **Estructura de documentación**: README.md actualizado para eliminar referencias a notebooks inexistentes 06-10

#### Calidad de Código
- **Ingeniería de características**: Patrón de fuente única de verdad verificado (sin duplicación entre entrenamiento/servicio)
- **Consistencia de importación**: Todos los módulos usan importaciones de paquete adecuadas (`from src.features import ...`)

### Arreglado
- Hooks de pre-commit ahora funcionales (referencia de prueba rota eliminada)
- Construcciones de Docker optimizadas (tamaño de imagen reducido excluyendo archivos dev)
- Protección de repositorio Git contra commits de archivos grandes
- Instalabilidad del paquete con pyproject.toml adecuado

### Seguridad
- Configuración de Dependabot para escaneo automatizado de vulnerabilidades
- Gestión de variables de entorno con plantilla .env.example
- Dependencias de producción y desarrollo separadas
- Optimización de imagen Docker reduciendo superficie de ataque

---

## [0.9.0] - 2025-12-01 (Estado Pre-Producción)

### Añadido
- Pipeline MLOps completo con 5 notebooks Jupyter educativos
- Aplicación de servicio FastAPI con comprobaciones de salud y endpoints de predicción
- Integración MLflow para seguimiento de experimentos y registro de modelos
- Marco de detección de deriva con pruebas estadísticas
- Documentación completa (README, USER_GUIDE, arquitectura, guías de despliegue)
- Soporte para Docker y Docker Compose
- CI/CD básico con GitHub Actions
- Suite de pruebas cubriendo procesamiento de datos, características, entrenamiento y pipelines

### Problemas Conocidos (Abordados en v1.0.0)
- Sin .dockerignore (imágenes Docker innecesariamente grandes)
- Falta pyproject.toml (paquete no instalable)
- Hook de pre-commit roto
- Sin escaneo de dependencias
- Dependencias dev y prod mezcladas
- Falta documentación de variables de entorno

---

## Resumen del Historial de Versiones

- **v1.0.0** (2025-12-11): Lanzamiento listo para producción con infraestructura completa, seguridad y mejoras de calidad
- **v0.9.0** (2025-12-01): Lanzamiento educativo con pipeline funcional pero faltando endurecimiento para producción

---

## Contribuyendo

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para pautas sobre cómo contribuir a este proyecto.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
