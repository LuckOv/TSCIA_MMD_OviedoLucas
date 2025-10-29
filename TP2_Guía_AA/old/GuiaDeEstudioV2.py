import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_excel("C:/Users/47-01/Downloads/Mini_Proyecto_Clientes_Promociones.xlsx")

print(df.head())

df['Genero'] = df['Genero'].map({'F':0,'M':1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Si':1, 'No':0})
df['Recompra'] = df['Recompra'].map({'Si':1, 'No':0})

# Gráfico de barras corregido
plt.figure(figsize=(8, 6))
sns.barplot(x="Recompra", y="Monto_Promo", data=df, estimator='mean', errorbar=None)
plt.title("Promedio de Monto Promocional según Recompra")
plt.xlabel("Recompra (0: No, 1: Si)")
plt.ylabel("Monto Promocional Promedio")
plt.show()

# Modelado Predictivo
X = df.drop(['Cliente_ID','Recompra'], axis=1)
y = df['Recompra']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

modelo = DecisionTreeClassifier(criterion='gini', random_state=42)
modelo.fit(X_train, y_train)

y_pred = modelo.predict(X_test)

# Gráfico del árbol de decisión
plt.figure(figsize=(20, 10))
plot_tree(modelo, 
          feature_names=X.columns,
          class_names=['No Recompra', 'Si Recompra'],
          filled=True,
          rounded=True,
          fontsize=10)
plt.title("Árbol de Decisión del Modelo Predictivo")
plt.show()

y_pred = modelo.predict(X_test)

#Matriz de confusión como heatmap

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
plt.show()

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))