import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_excel("C:/Users/47-01/Downloads/Mini_Proyecto_Clientes_Promociones.xlsx")

print(df.head())

df['Genero'] = df['Genero'].map({'F':0,'M':1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Si':1, 'No':0})
df['Recompra'] = df['Recompra'].map({'Si':1, 'No':0})

#Visualizacion de relaciones clave:
sns.bloxplot(x="Recompra", y="Monto_Promo", data=df)
plt.title("Recompra segun el Monto Promocional")
plt.show()

#Modelado Predictivo
X = df.drop(['Cliente_ID','Recompra'], axis=1)

y = df['Recompra']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

modelo = DecisionTreeClassifier(random_state=42)
modelo.fit(X_train, y_train)

y_pred = modelo.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

