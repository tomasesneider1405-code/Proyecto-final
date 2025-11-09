# Proyecto-final
proyecto final bootcam

# 🛰️ Proyecto Final – Brecha Digital en Colombia (2017–2024)

Este proyecto construye y analiza una base de datos completa sobre la **cobertura móvil en Colombia**, integrando información sobre **tecnologías móviles (2G–5G)**, **proveedores**, y **condiciones socioeconómicas municipales**.  

El objetivo es **medir la brecha digital** entre departamentos y municipios del país mediante consultas SQL y scripts en Python.

---

## 📂 Estructura del Proyecto

📁 COBER20251108/
│
├── crear_y_cargar_cobertura_colombia_final.py # Script principal en Python
├── cobertura_colombia_2017_2024_limpio_V2.csv # Fuente de datos (≈8000 registros)
└── consultas_sql/ # Consultas SQL avanzadas

---

## ⚙️ Tecnologías Utilizadas
- **MySQL / MariaDB** → creación de base de datos y consultas analíticas  
- **Python 3.x** → carga automatizada y normalización de datos  
- **Pandas** → manipulación y limpieza del CSV  
- **MySQL Connector / MariaDB** → conexión y carga directa a la base de datos  

---

## 🧠 Descripción del Script Principal

### 📜 Archivo: `crear_y_cargar_cobertura_colombia_final.py`

**Funciones principales:**
1. 🔌 **Conecta** automáticamente a un servidor MySQL local.
2. 🗃️ **Crea** la base de datos `cobertura_colombia` y todas sus tablas normalizadas:
   - `departamentos`
   - `municipios`
   - `centros_poblados`
   - `proveedores`
   - `indicadores_socioeconomicos`
   - `cobertura_movil`
3. 📄 **Carga** el archivo `cobertura_colombia_2017_2024_limpio_V2.csv`.
4. 🔁 **Inserta** los registros en lotes (más de 8.000 filas) utilizando claves foráneas y relaciones correctas.
5. ✅ **Finaliza** con confirmación y cierre seguro de la conexión.

**Fragmento del código:**
```python
conexion = mariadb.connect(host="127.0.0.1", user="root", password="")
cursor = conexion.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS cobertura_colombia;")
cursor.execute("USE cobertura_colombia;")

