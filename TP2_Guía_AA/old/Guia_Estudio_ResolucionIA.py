import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

print("=" * 60)
print("INICIANDO CARGA DE DATOS")
print("=" * 60)

# 1. VERIFICAR Y CARGAR EL DATAFRAME
ruta_archivo = "C:/Users/47-01/Downloads/Mini_Proyecto_Clientes_Promociones.xlsx"

# Verificar si el archivo existe
if not os.path.exists(ruta_archivo):
    print(f"ERROR: El archivo no existe en la ruta: {ruta_archivo}")
    print("Buscando archivos Excel en la carpeta Downloads...")
    
    downloads_path = "C:/Users/47-01/Downloads/"
    if os.path.exists(downloads_path):
        archivos_excel = [f for f in os.listdir(downloads_path) if f.endswith(('.xlsx', '.xls'))]
        if archivos_excel:
            print("Archivos Excel encontrados:")
            for archivo in archivos_excel:
                print(f"   - {archivo}")
            # Usar el primer archivo Excel encontrado
            ruta_archivo = os.path.join(downloads_path, archivos_excel[0])
            print(f"Usando archivo: {ruta_archivo}")
        else:
            print("No se encontraron archivos Excel en Downloads")
            exit()
    else:
        print("No se puede acceder a la carpeta Downloads")
        exit()

# Cargar el archivo con manejo de errores
try:
    df = pd.read_excel(ruta_archivo)
    print(f"ARCHIVO CARGADO EXITOSAMENTE")
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print(f"Nombre del archivo: {os.path.basename(ruta_archivo)}")
    
except Exception as e:
    print(f"ERROR AL LEER EL ARCHIVO: {e}")
    print("Posibles soluciones:")
    print("   1. Verifica que el archivo no esté abierto en Excel")
    print("   2. Instala openpyxl: pip install openpyxl")
    print("   3. Verifica que el archivo no esté corrupto")
    exit()

# 2. MOSTRAR INFORMACIÓN DEL DATAFRAME
print("\n" + "=" * 60)
print("INFORMACIÓN DEL DATASET")
print("=" * 60)

print("PRIMERAS 5 FILAS:")
print(df.head())

print("\n NOMBRES DE COLUMNAS:")
print(df.columns.tolist())

print("\n INFORMACIÓN GENERAL:")
print(df.info())

print("\n VALORES NULOS POR COLUMNA:")
print(df.isnull().sum())

print("\n DISTRIBUCIÓN DE DATOS:")
print(df.describe())

# 3. VERIFICAR SI EXISTEN LAS COLUMNAS NECESARIAS
columnas_requeridas = ['Cliente_ID', 'Recompra']
columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]

if columnas_faltantes:
    print(f"\n COLUMNAS FALTANTES: {columnas_faltantes}")
    print("COLUMNAS DISPONIBLES:")
    for col in df.columns:
        print(f"   - {col}")
    exit()
else:
    print(f"\n TODAS LAS COLUMNAS REQUERIDAS ESTÁN PRESENTES")

# 4. PROCESAMIENTO DE DATOS (solo si df se cargó correctamente)
print("\n" + "=" * 60)
print("PROCESAMIENTO DE DATOS")
print("=" * 60)

# Verificar y mapear columnas categóricas
if 'Genero' in df.columns:
    print(" Valores únicos en Género:", df['Genero'].unique())
    df['Genero'] = df['Genero'].map({'F': 0, 'M': 1, 'Femenino': 0, 'Masculino': 1})
    
if 'Recibio_Promo' in df.columns or 'Recibió_Promo' in df.columns:
    col_name = 'Recibio_Promo' if 'Recibio_Promo' in df.columns else 'Recibió_Promo'
    print(f" Valores únicos en {col_name}:", df[col_name].unique())
    df[col_name] = df[col_name].map({'Si': 1, 'No': 0, 'Sí': 1})
    
if 'Recompra' in df.columns:
    print(" Valores únicos en Recompra:", df['Recompra'].unique())
    df['Recompra'] = df['Recompra'].map({'Si': 1, 'No': 0, 'Sí': 1})

# 5. MODELADO PREDICTIVO (solo si todo está bien)
print("\n" + "=" * 60)
print("MODELADO PREDICTIVO")
print("=" * 60)

# Preparar variables
X = df.drop(['Cliente_ID', 'Recompra'], axis=1)
y = df['Recompra']

print(f" X shape: {X.shape}")
print(f" y shape: {y.shape}")

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Entrenar modelo
modelo = DecisionTreeClassifier(random_state=42)
modelo.fit(X_train, y_train)

# Predecir y evaluar
y_pred = modelo.predict(X_test)

print("\n MATRIZ DE CONFUSIÓN:")
print(confusion_matrix(y_test, y_pred))

print("\n REPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred))

print("=" * 60)
print("PROCESO COMPLETADO EXITOSAMENTE")
print("=" * 60)