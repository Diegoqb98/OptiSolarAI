# Datos del Proyecto

Este directorio contiene todos los datos utilizados en OptiSolarAI.

## Estructura

- **`raw/`**: Datos originales sin procesar
  - Precios históricos de electricidad
  - Datos de producción solar
  - Datos meteorológicos históricos

- **`processed/`**: Datos procesados y listos para el modelo
  - Datos normalizados
  - Features engineering
  - Datos de entrenamiento/validación/test

## Fuentes de Datos

- **Precios eléctricos**: [Especificar fuente]
- **Producción solar**: [Especificar fuente]
- **Datos meteorológicos**: OpenWeatherMap API

## Notas

Los archivos de datos grandes no se suben al repositorio (ver `.gitignore`).
Para obtener los datos, ejecutar los scripts de descarga en `/src/data/`.
