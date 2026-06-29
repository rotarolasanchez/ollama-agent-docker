-- 01_schema.sql — esquema adaptado al cubo de ventas Vistony
-- Ejecutar: docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "TuPassword" -No -i /docker-entrypoint-initdb.d/01_schema.sql

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'FacturasDB')
    CREATE DATABASE FacturasDB;
GO

USE FacturasDB;
GO

-- ─── TABLA PRINCIPAL DE VENTAS ────────────────────────────────
IF EXISTS (SELECT * FROM sysobjects WHERE name='VentasCubo' AND xtype='U')
    DROP TABLE VentasCubo;
GO

CREATE TABLE VentasCubo (
    -- Identificadores
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    Documento_ID        VARCHAR(20),
    NumeroLegal         VARCHAR(30),
    NumInternoFact      VARCHAR(20),

    -- Fechas
    FechaEmision        DATE,
    FechaVencimiento    DATE,
    DiasVencimiento     INT,
    Anio                INT,
    Mes_Texto           VARCHAR(20),
    Dia_Num             INT,

    -- Tipo de documento y venta
    Documento           VARCHAR(30),         -- Factura, Nota de Credito
    TipoVenta           VARCHAR(50),
    TerminoPago         VARCHAR(50),
    TerminoPago_Resumen VARCHAR(20),         -- Contado, Credito
    CondicionPago       VARCHAR(50),
    Indicador_Impuesto  VARCHAR(20),         -- IGV, IGV_FISE
    Moneda              VARCHAR(5),          -- S/, USD
    Tipo_Cambio         DECIMAL(10,4),
    Almacen             VARCHAR(20),

    -- Cliente
    Cliente_ID          VARCHAR(20),
    Domicilio_ID        VARCHAR(20),
    Cliente             VARCHAR(200),
    RUC                 VARCHAR(20),
    TipoIdentificacion  VARCHAR(20),
    Cliente_Categoria   VARCHAR(5),
    CategoriaPotencial  VARCHAR(5),
    Giro_Negocio        VARCHAR(100),
    Actividad           VARCHAR(100),
    FechaCreacionCliente DATE,
    Linea_Credito       DECIMAL(18,2),
    Correo              VARCHAR(150),
    Telefono            VARCHAR(50),
    Dia_Ruta            VARCHAR(20),
    Dias_Entrega        INT,

    -- Ubicación cliente
    Domicilio           VARCHAR(300),
    Distrito            VARCHAR(50),
    Provincia           VARCHAR(50),
    Departamento        VARCHAR(50),
    Pais                VARCHAR(30),
    Ubigeo              VARCHAR(10),

    -- Zona comercial
    Zona_ID             VARCHAR(20),
    Zona                VARCHAR(100),

    -- Producto
    Producto_ID         VARCHAR(20),
    Producto            VARCHAR(200),
    CodigoBarra         VARCHAR(30),
    UnidadMedida        VARCHAR(20),
    ProductoUnd_ID      VARCHAR(20),
    ProductoUnd         VARCHAR(200),
    Tecnologia          VARCHAR(50),

    -- Jerarquía de producto
    Categoria           VARCHAR(50),
    Categoria_ID        VARCHAR(10),
    Familia             VARCHAR(50),
    Familia_ID          VARCHAR(10),
    SubFamilia          VARCHAR(50),
    SubFamilia_ID       VARCHAR(10),
    Linea               VARCHAR(50),
    Linea_ID            VARCHAR(10),
    Marca               VARCHAR(30),
    GrupoProducto       VARCHAR(50),
    Variable            VARCHAR(50),
    Subcanal            VARCHAR(30),

    -- Vendedor / Equipo comercial
    Vendedor_ID         INT,
    Vendedor            VARCHAR(100),
    Analista            VARCHAR(100),
    Supervisor          VARCHAR(100),
    Gerencia            VARCHAR(50),
    UnidadNegocio       VARCHAR(50),
    GrupoUnidadNegocio  VARCHAR(50),
    Sectorista          VARCHAR(100),
    TipoGerencia        VARCHAR(30),
    TipoGerencia_ID     INT,
    Aprobador           VARCHAR(100),
    CentroCosto         VARCHAR(50),
    LineaProduccion     VARCHAR(50),
    Procedencia         VARCHAR(20),

    -- Promoción
    PromID              VARCHAR(30),
    FISE                VARCHAR(5),
    Motivo_Descuento    VARCHAR(50),
    Motivo_TransGratuita VARCHAR(100),

    -- Montos
    Precio              DECIMAL(18,4),
    PrecioAntesDscto    DECIMAL(18,4),
    Total_con_Impuesto  DECIMAL(18,4),
    Total_sin_Impuesto  DECIMAL(18,4),
    Total_Costo         DECIMAL(18,4),
    Total_Total_Costo   DECIMAL(18,4),
    Cantidad            DECIMAL(18,4),
    Galones             DECIMAL(18,4),
    Barriles            DECIMAL(18,6),
    Descuento           DECIMAL(18,4),
    Descuento_2         DECIMAL(18,4),
    Descuento_Porc      DECIMAL(18,4),
    DescuentoFinanciero DECIMAL(18,4),
    Otros_Descuentos    DECIMAL(18,4),
    Total_Promocion     DECIMAL(18,4),
    Total_Promocion_PV  DECIMAL(18,4),
    Cuenta              VARCHAR(20),
    Sucursal            VARCHAR(30)
);
GO

-- Índices para mejorar velocidad de consultas frecuentes
CREATE INDEX IX_Ventas_Fecha     ON VentasCubo(FechaEmision);
CREATE INDEX IX_Ventas_Cliente   ON VentasCubo(Cliente_ID);
CREATE INDEX IX_Ventas_Producto  ON VentasCubo(Producto_ID);
CREATE INDEX IX_Ventas_Vendedor  ON VentasCubo(Vendedor_ID);
CREATE INDEX IX_Ventas_Zona      ON VentasCubo(Zona_ID);
CREATE INDEX IX_Ventas_Documento ON VentasCubo(Documento);
GO

PRINT 'Tabla VentasCubo creada correctamente.';
GO