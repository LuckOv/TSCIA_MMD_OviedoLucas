import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

df = pd.read_excel("C:/Users/47-01/Downloads/Mini_Proyecto_Clientes_Promociones.xlsx")

print("Columnas en el dataset:")
print(df.columns.tolist())
print("\nPrimeras filas del dataset:")
print(df.head())
print("\nInformación del dataset:")
print(df.info())
print("\nDistribución de la variable objetivo:")
print(df['Recompra'].value_counts())

# Preprocesamiento
df['Genero'] = df['Genero'].map({'F':0,'M':1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Si':1, 'No':0})
df['Recompra'] = df['Recompra'].map({'Si':1, 'No':0})

# Verificar valores nulos
print("\nValores nulos por columna:")
print(df.isnull().sum())

# Gráfico de barras
plt.figure(figsize=(8, 6))
sns.barplot(x="Recompra", y="Monto_Promo", data=df, estimator='mean', errorbar=None)
plt.title("Promedio de Monto Promocional según Recompra")
plt.xlabel("Recompra (0: No, 1: Si)")
plt.ylabel("Monto Promocional Promedio")
plt.show()

# Preparación de datos
X = df.drop(['Cliente_ID','Recompra'], axis=1)
y = df['Recompra']

# Identificar automáticamente las columnas numéricas (excluyendo las ya convertidas)
numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nColumnas numéricas identificadas: {numeric_cols}")

# Balanceo de clases (si es necesario)
print(f"\nDistribución original de clases: {y.value_counts().to_dict()}")

# Si hay desbalance significativo, aplicar balanceo
if len(y.value_counts()) > 1 and y.value_counts().min() / y.value_counts().max() < 0.5:
    print("Aplicando balanceo de clases...")
    # Unir X e y para el balanceo
    df_balanced = pd.concat([X, y], axis=1)
    
    # Separar clases
    df_majority = df_balanced[df_balanced.Recompra == 0]
    df_minority = df_balanced[df_balanced.Recompra == 1]
    
    # Balancear por oversampling de la clase minoritaria
    df_minority_upsampled = resample(df_minority, 
                                     replace=True, 
                                     n_samples=len(df_majority), 
                                     random_state=42)
    
    # Combinar las clases balanceadas
    df_balanced = pd.concat([df_majority, df_minority_upsampled])
    
    # Separar nuevamente X e y
    X = df_balanced.drop('Recompra', axis=1)
    y = df_balanced['Recompra']
    print(f"Distribución después del balanceo: {y.value_counts().to_dict()}")

# Escalar características numéricas si existen
if numeric_cols:
    scaler = StandardScaler()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    print("Características numéricas escaladas.")
else:
    print("No hay características numéricas para escalar.")

# División de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# MEJORA 1: Optimización de hiperparámetros con GridSearchCV
print("\nOptimizando hiperparámetros...")
param_grid = {
    'max_depth': [3, 5, 7, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'criterion': ['gini', 'entropy']
}

grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42), 
                          param_grid, 
                          cv=5, 
                          scoring='accuracy',
                          n_jobs=-1)
grid_search.fit(X_train, y_train)

print(f"Mejores parámetros: {grid_search.best_params_}")
print(f"Mejor score en validación: {grid_search.best_score_:.4f}")

# MEJORA 2: Usar el modelo optimizado
best_model = grid_search.best_estimator_

# MEJORA 3: Probar con Random Forest (generalmente mejor que un solo árbol)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluación de modelos
models = {
    'Árbol de Decisión Optimizado': best_model,
    'Random Forest': rf_model
}

for name, model in models.items():
    y_pred = model.predict(X_test)
    
    print(f"\n=== {name} ===")
    print(f"Exactitud: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precisión: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
    
    # Matriz de confusión
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, 
                annot=True, 
                fmt='d', 
                cmap='Blues',
                xticklabels=['No Recompra', 'Si Recompra'],
                yticklabels=['No Recompra', 'Si Recompra'])
    plt.title(f'Matriz de Confusión - {name}')
    plt.xlabel('Predicción')
    plt.ylabel('Real')
    plt.show()

# Gráfico del árbol de decisión optimizado (solo si no es demasiado grande)
if grid_search.best_params_['max_depth'] is not None and grid_search.best_params_['max_depth'] <= 10:
    plt.figure(figsize=(20, 10))
    plot_tree(best_model, 
              feature_names=X.columns,
              class_names=['No Recompra', 'Si Recompra'],
              filled=True,
              rounded=True,
              fontsize=10)
    plt.title("Árbol de Decisión Optimizado")
    plt.show()
else:
    print("El árbol es demasiado grande para visualizar de manera clara.")

# Importancia de características (para Random Forest)
plt.figure(figsize=(10, 6))
importances = rf_model.feature_importances_
feature_names = X.columns
indices = np.argsort(importances)[::-1]

plt.barh(range(len(importances)), importances[indices])
plt.yticks(range(len(importances)), [feature_names[i] for i in indices])
plt.xlabel('Importancia')
plt.title('Importancia de Características - Random Forest')
plt.gca().invert_yaxis()
plt.show()

# Reporte detallado del mejor modelo
print("\n=== REPORTE DETALLADO DEL MEJOR MODELO ===")
y_pred_best = best_model.predict(X_test)
print(classification_report(y_test, y_pred_best))