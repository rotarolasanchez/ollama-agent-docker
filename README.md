# Facturas AI — Guía de inicio rápido

## Requisitos

* Docker Desktop instalado y corriendo

## 1\. Preparar el proyecto

```bash
# Clona o copia esta carpeta en tu máquina
# Luego crea tu archivo de variables:
cp .env.example .env
# Edita .env con tu editor y cambia las contraseñas
```

## 2\. Levantar todo el stack

```bash
docker compose up -d
```

Esto levanta automáticamente:

* SQL Server en el puerto 1433
* Ollama en el puerto 11434 (descarga el modelo la primera vez \~4GB)
* La API en http://localhost:8000

## 3\. Verificar que todo esté corriendo

```bash
# Ver estado de los contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f api

# Probar el health check
curl http://localhost:8000/health/
```

## 4\. Probar la API

Abre en tu navegador: **http://localhost:8000/docs**

Verás la documentación interactiva con todos los endpoints.

### Ejemplos de uso:

**Consulta en lenguaje natural:**

```bash
curl -X POST http://localhost:8000/query/ \\
  -H "Content-Type: application/json" \\
  -d '{"pregunta": "¿Cuánto gasté en total este año?"}'
```

**Reporte de facturas pendientes:**

```bash
curl http://localhost:8000/reportes/pendientes
```

**Top proveedores:**

```bash
curl http://localhost:8000/reportes/top-proveedores?top=5
```

## 5\. Pasar al servidor corporativo

```bash
# En el servidor, copia la carpeta del proyecto y ejecuta:
docker compose up -d

# Para migrar la base de datos desde tu laptop:
# En tu laptop (genera el backup):
docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd \\
  -S localhost -U sa -P TuPassword \\
  -Q "BACKUP DATABASE \[FacturasDB] TO DISK='/var/opt/mssql/backup.bak' WITH INIT"
docker cp sqlserver:/var/opt/mssql/backup.bak ./backup.bak

# Copia backup.bak al servidor y restaura:
docker cp backup.bak sqlserver:/var/opt/mssql/backup.bak
docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd \\
  -S localhost -U sa -P TuPassword \\
  -Q "RESTORE DATABASE \[FacturasDB] FROM DISK='/var/opt/mssql/backup.bak' WITH REPLACE"
```

## Endpoints disponibles

|Método|Ruta|Descripción|
|-|-|-|
|GET|/health/|Estado de todos los servicios|
|POST|/query/|Pregunta en lenguaje natural|
|GET|/reportes/resumen-mensual|Resumen del mes|
|GET|/reportes/top-proveedores|Top N proveedores por monto|
|GET|/reportes/pendientes|Facturas pendientes de pago|
|GET|/docs|Documentación interactiva Swagger|



