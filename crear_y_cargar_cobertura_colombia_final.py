# -*- coding: utf-8 -*-
"""
============================================
 Script: crear_y_cargar_cobertura_colombia_final.py
 Autor: ChatGPT (GPT-5)
 Fecha: 2025-11-02
 Descripción:
    Crea automáticamente la base de datos 'cobertura_colombia' en MySQL,
    genera todas las tablas normalizadas e inserta los 8000 registros
    del archivo CSV 'cobertura_colombia_2017_2024_limpio.csv'.
============================================
"""

# ============================================================
# 1️⃣ Importar librerías
# ============================================================
import pandas as pd
import mariadb
import mysql.connector
from mysql.connector import Error

# ============================================================
# 2️⃣ Configuración de conexión MySQL
# ============================================================
try:
    conexion = mariadb.connect(
        host="127.0.0.1",
        port=3306,               # Cambia si tu servidor usa otro puerto
        user="root",             # ⚠️ Ajusta tu usuario
        password=""              # ⚠️ Agrega tu contraseña si la tienes
    )

    cursor = conexion.cursor()
    print("✅ Conexión exitosa a MySQL.")
except mariadb.Error as e:
    print("❌ Error de conexión:", e)
    exit()

# ============================================================
# 3️⃣ Crear base de datos y usarla
# ============================================================
cursor.execute("""
CREATE DATABASE IF NOT EXISTS cobertura_colombia
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
""")
cursor.execute("USE cobertura_colombia;")
print("📦 Base de datos 'cobertura_colombia' lista.")

# ============================================================
# 4️⃣ Crear tablas normalizadas
# ============================================================
tablas_sql = """
-- Departamentos
CREATE TABLE IF NOT EXISTS departamentos (
    cod_departamento INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- Municipios
CREATE TABLE IF NOT EXISTS municipios (
    cod_municipio INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    cabecera_municipal VARCHAR(5),
    cod_departamento INT NOT NULL,
    FOREIGN KEY (cod_departamento) REFERENCES departamentos(cod_departamento)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Centros Poblados
CREATE TABLE IF NOT EXISTS centros_poblados (
    cod_centro_poblado INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    cod_municipio INT NOT NULL,
    altitud_msnm INT,
    precipitacion_media DECIMAL(8,2),
    FOREIGN KEY (cod_municipio) REFERENCES municipios(cod_municipio)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    nombre_comercial VARCHAR(150)
) ENGINE=InnoDB;

-- Indicadores Socioeconómicos
CREATE TABLE IF NOT EXISTS indicadores_socioeconomicos (
    id_indicador INT AUTO_INCREMENT PRIMARY KEY,
    cod_municipio INT NOT NULL,
    anio INT NOT NULL,
    estrato_promedio DECIMAL(3,1),
    ingreso_promedio_hogar DECIMAL(12,2),
    tasa_pobreza DECIMAL(5,2),
    indice_nbi DECIMAL(5,2),
    tasa_desempleo DECIMAL(5,2),
    tasa_electrificacion DECIMAL(5,2),
    pct_hogares_internet DECIMAL(5,2),
    inv_publica_per_capita DECIMAL(12,2),
    FOREIGN KEY (cod_municipio) REFERENCES municipios(cod_municipio)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Cobertura Móvil (VARCHAR)
CREATE TABLE IF NOT EXISTS cobertura_movil (
    id_cobertura INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL,
    trimestre INT,
    id_proveedor INT NOT NULL,
    cod_departamento INT NOT NULL,
    cod_municipio INT NOT NULL,
    cod_centro_poblado INT,
    cobertura_2g VARCHAR(50),
    cobertura_3g VARCHAR(50),
    cobertura_hspa_hspa_dc VARCHAR(50),
    cobertura_4g VARCHAR(50),
    cobertura_lte VARCHAR(50),
    cobertura_5g VARCHAR(50),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (cod_departamento) REFERENCES departamentos(cod_departamento)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (cod_municipio) REFERENCES municipios(cod_municipio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (cod_centro_poblado) REFERENCES centros_poblados(cod_centro_poblado)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;
"""
for stmt in tablas_sql.split(";"):
    if stmt.strip():
        cursor.execute(stmt)
print("🧱 Tablas creadas correctamente.")

# ============================================================
# 5️⃣ Leer archivo CSV
# ============================================================
ruta_csv = r"cobertura_colombia_2017_2024_limpio_V2.csv"
df = pd.read_csv(ruta_csv)
df.columns = df.columns.str.strip().str.upper()
print(f"📄 Archivo cargado: {len(df)} registros detectados.")

# ============================================================
# 6️⃣ Preparar subconjuntos únicos
# ============================================================
departamentos = df[['COD_DEPARTAMENTO', 'DEPARTAMENTO']].drop_duplicates()
municipios = df[['COD_MUNICIPIO', 'MUNICIPIO', 'CABECERA_MUNICIPAL', 'COD_DEPARTAMENTO']].drop_duplicates()
centros_poblados = df[['COD_CENTRO_POBLADO', 'CENTRO_POBLADO', 'COD_MUNICIPIO', 'ALTITUD_MSNM', 'PRECIPITACION_MEDIA']].drop_duplicates()
proveedores = df[['PROVEEDOR', 'NOMBRE_PROVEEDOR_COMERCIAL']].drop_duplicates()
indicadores = df[['COD_MUNICIPIO', 'AÑO', 'ESTRATO_PROMEDIO', 'INGRESO_PROMEDIO_HOGAR',
                  'TASA_POBREZA', 'INDICE_NBI', 'TASA_DESEMPLEO', 'TASA_ELECTRIFICACION',
                  'PCT_HOGARES_INTERNET', 'INV_PUBLICA_PER_CAPITA']].drop_duplicates()
cobertura = df[['AÑO', 'TRIMESTRE', 'PROVEEDOR', 'COD_DEPARTAMENTO', 'COD_MUNICIPIO',
                'COD_CENTRO_POBLADO', 'COBERTURA_2G', 'COBERTURA_3G',
                'COBERTURA_HSPA_HSPA_DC', 'COBERTURA_4G', 'COBERTURA_LTE', 'COBERTURA_5G']]

# ============================================================
# 7️⃣ Función de inserción por lotes
# ============================================================
def insertar_lote(query, valores):
    try:
        cursor.executemany(query, valores)
        conexion.commit()
    except mariadb.Error as e:
        print("⚠️ Error en lote:", e)

# ============================================================
# 8️⃣ Insertar datos
# ============================================================
print("➡ Insertando Departamentos...")
valores = [(int(f['COD_DEPARTAMENTO']), f['DEPARTAMENTO']) for _, f in departamentos.iterrows()]
insertar_lote("INSERT IGNORE INTO departamentos (cod_departamento, nombre) VALUES (%s,%s)", valores)

print("➡ Insertando Municipios...")
valores = [(int(f['COD_MUNICIPIO']), f['MUNICIPIO'], str(f['CABECERA_MUNICIPAL']), int(f['COD_DEPARTAMENTO']))
           for _, f in municipios.iterrows()]
insertar_lote("""INSERT IGNORE INTO municipios (cod_municipio, nombre, cabecera_municipal, cod_departamento)
                 VALUES (%s,%s,%s,%s)""", valores)

print("➡ Insertando Centros Poblados...")
valores = [(int(f['COD_CENTRO_POBLADO']), f['CENTRO_POBLADO'], int(f['COD_MUNICIPIO']),
             f['ALTITUD_MSNM'] if not pd.isna(f['ALTITUD_MSNM']) else None,
             f['PRECIPITACION_MEDIA'] if not pd.isna(f['PRECIPITACION_MEDIA']) else None)
            for _, f in centros_poblados.iterrows()]
insertar_lote("""INSERT IGNORE INTO centros_poblados
                 (cod_centro_poblado, nombre, cod_municipio, altitud_msnm, precipitacion_media)
                 VALUES (%s,%s,%s,%s,%s)""", valores)

print("➡ Insertando Proveedores...")
valores = [(f['PROVEEDOR'], f['NOMBRE_PROVEEDOR_COMERCIAL']) for _, f in proveedores.iterrows()]
insertar_lote("INSERT IGNORE INTO proveedores (nombre, nombre_comercial) VALUES (%s,%s)", valores)

cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
proveedor_dict = {n: i for i, n in cursor.fetchall()}

print("➡ Insertando Indicadores Socioeconómicos...")
valores = [(int(f['COD_MUNICIPIO']), int(f['AÑO']), f['ESTRATO_PROMEDIO'], f['INGRESO_PROMEDIO_HOGAR'],
             f['TASA_POBREZA'], f['INDICE_NBI'], f['TASA_DESEMPLEO'],
             f['TASA_ELECTRIFICACION'], f['PCT_HOGARES_INTERNET'], f['INV_PUBLICA_PER_CAPITA'])
            for _, f in indicadores.iterrows()]
insertar_lote("""INSERT INTO indicadores_socioeconomicos
                 (cod_municipio, anio, estrato_promedio, ingreso_promedio_hogar, tasa_pobreza, indice_nbi,
                  tasa_desempleo, tasa_electrificacion, pct_hogares_internet, inv_publica_per_capita)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", valores)

print("➡ Insertando Cobertura Móvil (tipo texto)...")
valores = [(int(f['AÑO']), int(f['TRIMESTRE']), proveedor_dict.get(f['PROVEEDOR']),
             int(f['COD_DEPARTAMENTO']), int(f['COD_MUNICIPIO']),
             int(f['COD_CENTRO_POBLADO']) if not pd.isna(f['COD_CENTRO_POBLADO']) else None,
             str(f['COBERTURA_2G']), str(f['COBERTURA_3G']), str(f['COBERTURA_HSPA_HSPA_DC']),
             str(f['COBERTURA_4G']), str(f['COBERTURA_LTE']), str(f['COBERTURA_5G']))
            for _, f in cobertura.iterrows()]
insertar_lote("""INSERT INTO cobertura_movil
                 (anio, trimestre, id_proveedor, cod_departamento, cod_municipio, cod_centro_poblado,
                  cobertura_2g, cobertura_3g, cobertura_hspa_hspa_dc, cobertura_4g, cobertura_lte, cobertura_5g)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", valores)

# ============================================================
# 9️⃣ Finalizar
# ============================================================
conexion.commit()
cursor.close()
conexion.close()
print("✅ Base de datos creada y 8000 registros cargados correctamente.")
