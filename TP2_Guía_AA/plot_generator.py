# Cadena de Gimnasio - Plot Generator Script
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openpyxl
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix

# Carga de datos
df = pd.read_excel("Mini_Proyecto_Clientes_Promociones.xlsx")

print(df.head())

# Preprocesamiento
df['Genero'] = df['Genero'].map({'F': 0, 'M': 1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Si': 1, 'No': 0})
df['Recompra'] = df['Recompra'].map({'Si': 1, 'No': 0})

# Gráfico de barras
plt.figure(figsize=(8, 6))
sns.barplot(x="Recompra", y="Monto_Promo", data=df, estimator='mean', errorbar=None)
plt.title("Promedio de Monto Promocional según Recompra")
plt.xlabel("Recompra (0: No, 1: Si)")
plt.ylabel("Monto Promocional Promedio")
plt.savefig('bar_plot.png')
plt.close()

# Modelado Predictivo
X = df.drop(['Cliente_ID', 'Recompra'], axis=1)
y = df['Recompra']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
modelo = DecisionTreeClassifier(random_state=42)
modelo.fit(X_train, y_train)

# Gráfico del árbol de decisión
plt.figure(figsize=(20, 10))
plot_tree(modelo,
          feature_names=X.columns,
          class_names=['No Recompra', 'Si Recompra'],
          filled=True,
          rounded=True,
          fontsize=10)
plt.title("Árbol de Decisión del Modelo Predictivo")
plt.savefig('decision_tree.png')
plt.close()

y_pred = modelo.predict(X_test)

# Matriz de confusión
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['No Recompra', 'Si Recompra'],
            yticklabels=['No Recompra', 'Si Recompra'])
plt.title('Matriz de Confusión')
plt.xlabel('Predicción')
plt.ylabel('Real')
plt.savefig('confusion_matrix.png')
plt.close()

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))