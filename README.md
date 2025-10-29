# Minería de Datos - Trabajo Práctico Cuarto Cuatrimestre

## Descripción del Proyecto

Este repositorio contiene los trabajos prácticos realizados durante el curso de Minería de Datos en la Tecnicatura en Ciencia de Datos e Inteligencia Artificial. Los trabajos cubren diversos aspectos de la manipulación, análisis y gestión de datos utilizando Python y sus bibliotecas especializadas.

## Estructura del Proyecto

### Archivos Principales
- `MineriaDatos.ipynb` - Notebook principal con análisis de datos
- `productos.csv` - Datos de productos
- `comercio.sql`, `provincias.sql`, `storemd.sql` - Scripts SQL para base de datos
- `sql-for-data-science.pdf` - Guía de estudio SQL
- `TSCIA_MMD_Guia_de_estudio-1-4.pdf`, `TSCIA_MMD_Guia_de_estudio.pdf` - Guías de estudio
- `TSCIA_MMD_Python_CSV_Pandas.pdf` - Guía de Python, CSV y Pandas

### Carpeta CSVs/
Contiene datasets en formato CSV utilizados en los análisis:
- `clientes.csv` - Información de clientes
- `facturas_detalles.csv`, `facturas_encabezados.csv` - Datos de facturación
- `productos.csv` - Catálogo de productos
- `rubros.csv` - Clasificación por rubros
- `ventas.csv` - Datos de ventas
- Subcarpeta `CSV/` con datos simulados y generador de datos

### Carpeta python/
Scripts Python para manipulación de datos CSV:
- `analisis_pandas.py` - Análisis con Pandas
- `csv_agregarRegistros.py` - Agregar registros a CSV
- `csv_borrarRegistros.py` - Eliminar registros de CSV
- `csv_leerCSV.py` - Lectura de archivos CSV
- `csv_modificarRegistros.py` - Modificar registros CSV
- `funcionesCSV.py` - Funciones auxiliares para CSV
- `mainCSV.py` - Script principal para gestión CSV

## Trabajos Prácticos

### TP1: Manipulación CSV/JSON
**Ubicación:** `TP1_Manipulación_CSV_JSON_script/`

Sistema de gestión de archivos CSV y JSON desarrollado en Python con interfaz de línea de comandos. Incluye operaciones CRUD completas (Crear, Leer, Actualizar, Eliminar) para datos estructurados.

**Características principales:**
- Carga y gestión de múltiples archivos CSV/JSON
- Visualización tabular de datos con bordes y alineación automática
- Operaciones CRUD con validación de campos
- Manejo automático de IDs y selección de localidades
- Opciones flexibles de guardado (sobrescribir o crear nuevos archivos)
- Arquitectura modular con separación entre lógica de negocio e interfaz

**Archivos clave:**
- `mainCSV_v4.py` - Interfaz principal del menú
- `funcionesCSV_v3.py` - Módulo de funciones CRUD
- `app_streamlitV5.py` - Versión con interfaz Streamlit

### TP2: Guía de Análisis con IA - Cadena de Gimnasios
**Ubicación:** `TP2_Guía_AA/`

Análisis predictivo de datos de clientes de una cadena de gimnasios utilizando técnicas de minería de datos. Se desarrolla un modelo para predecir el comportamiento de recompra basado en características demográficas y promocionales.

**Objetivos:**
- Análisis exploratorio de datos (EDA)
- Desarrollo de modelo predictivo con árbol de decisión
- Evaluación del modelo con métricas de clasificación
- Visualización de resultados y matriz de confusión

**Tecnologías utilizadas:**
- Python con Pandas, Seaborn, Matplotlib
- Scikit-learn para modelado predictivo
- Jupyter Notebook para análisis interactivo

**Resultados:**
- Modelo de árbol de decisión para predicción de recompra
- Análisis del impacto de promociones en el comportamiento del cliente
- Visualizaciones: gráfico de barras, árbol de decisión, matriz de confusión

### TP3: Análisis de Datos con Pandas
**Ubicación:** `TP3_Pandas/`

Análisis exhaustivo de datos de ventas utilizando Pandas para extraer insights empresariales. Se analiza información de clientes, productos, facturas y tendencias temporales.

**Análisis realizados:**
- **Ranking de clientes:** Identificación de clientes más importantes por volumen de ventas
- **Análisis temporal:** Evolución mensual y semanal de ventas
- **Análisis de productos:** Productos más vendidos por cantidad y facturación
- **Matriz BCG:** Clasificación de productos por crecimiento e ingresos
- **Análisis por rubros:** Distribución de ventas por categorías

**Datasets utilizados:**
- `clientes.csv` - Información de clientes
- `productos.csv` - Catálogo de productos
- `rubros.csv` - Clasificación por rubros
- `facturas_encabezados_simulados.csv` - Encabezados de facturas
- `facturas_detalles_simulados.csv` - Detalles de facturas
- `ventas_simuladas.csv` - Datos consolidados de ventas

**Visualizaciones generadas:**
- Ranking de clientes por ventas totales
- Evolución mensual de ventas
- Ventas semanales de septiembre
- Distribución por rubros
- Ranking de productos por facturación
- Matriz BCG (Estrellas, Vacas Lecheras, Interrogantes, Perros)

### TP4: Gestor de Archivos CSV/JSON con Streamlit
**Ubicación:** `TP4/`

Aplicación web interactiva desarrollada con Streamlit para gestión completa de archivos CSV y JSON. Proporciona una interfaz intuitiva para manipulación de datos estructurados.

**Funcionalidades:**
- **Carga de archivos:** Soporte para archivos subidos y locales (CSV/JSON)
- **Visualización:** Presentación tabular con métricas de resumen
- **Gestión de registros:** Agregar, modificar y eliminar registros
- **Guardado flexible:** Sobrescribir archivo actual o crear nuevos
- **Interfaz responsive:** Diseño con sidebar y pestañas organizadas

**Características técnicas:**
- Gestión de estado con session_state de Streamlit
- Manejo de errores robusto
- Arquitectura modular con funciones separadas
- Interfaz de usuario intuitiva con navegación por pestañas

**Capturas de pantalla incluidas:**
- Pantalla de bienvenida
- Carga de archivos
- Visualización de datos
- Gestión de registros (agregar/modificar/borrar)
- Opciones de guardado

## Tecnologías Utilizadas

- **Python** - Lenguaje principal de programación
- **Pandas** - Manipulación y análisis de datos
- **Streamlit** - Desarrollo de aplicaciones web
- **Matplotlib/Seaborn** - Visualización de datos
- **Scikit-learn** - Modelado predictivo
- **Jupyter Notebook** - Análisis interactivo
- **SQL** - Gestión de bases de datos

## Información del Curso

- **Materia:** Modelizado de Minería de Datos
- **Docente:** Fernández, David
- **Alumno:** Oviedo, Lucas Nahuel
- **Carrera:** Tecnicatura en Ciencia de Datos e Inteligencia Artificial
- **Institución:** INSTITUTO SUPERIOR DE FORMACIÓN TÉCNICA N° 197
- **Año:** 2025
