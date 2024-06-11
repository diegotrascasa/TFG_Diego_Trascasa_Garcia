import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Leer los datos
train_df = pd.read_csv('mitbih_train.csv', header=None)  # Cargar el conjunto de entrenamiento
test_df = pd.read_csv('mitbih_test.csv', header=None)    # Cargar el conjunto de prueba

# Convertir la última columna a entero
train_df[187] = train_df[187].astype(int)  # Asegurarse de que las etiquetas sean enteros

# Remuestrear las clases minoritarias para balancear el conjunto de datos
df_1 = train_df[train_df[187] == 1]  # Filtrar clase 1
df_2 = train_df[train_df[187] == 2]  # Filtrar clase 2
df_3 = train_df[train_df[187] == 3]  # Filtrar clase 3
df_4 = train_df[train_df[187] == 4]  # Filtrar clase 4
df_0 = train_df[train_df[187] == 0].sample(n=20000, random_state=42)  # Filtrar clase 0 con muestra

# Aumentar las clases minoritarias mediante remuestreo con reemplazo
df_1_upsample = resample(df_1, replace=True, n_samples=20000, random_state=123)
df_2_upsample = resample(df_2, replace=True, n_samples=20000, random_state=124)
df_3_upsample = resample(df_3, replace=True, n_samples=20000, random_state=125)
df_4_upsample = resample(df_4, replace=True, n_samples=20000, random_state=126)

# Combinar los datasets remuestreados para formar un conjunto de entrenamiento balanceado
balanced_train_df = pd.concat([df_0, df_1_upsample, df_2_upsample, df_3_upsample, df_4_upsample])

# Dividir los datos en características (X) y etiquetas (y)
X_train = balanced_train_df.iloc[:, :-1]  # Características del conjunto de entrenamiento
y_train = balanced_train_df.iloc[:, -1]   # Etiquetas del conjunto de entrenamiento
X_test = test_df.iloc[:, :-1]             # Características del conjunto de prueba
y_test = test_df.iloc[:, -1]              # Etiquetas del conjunto de prueba

# Inicializar y entrenar el clasificador Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
y_pred = model.predict(X_test)

# Generar y mostrar la matriz de confusión
cm = confusion_matrix(y_test, y_pred)
labels = ['Normal Beats', 'Supraventricular Ectopy Beats', 'Ventricular Ectopy Beats', 'Fusion Beats', 'Unclassifiable Beats']

plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted')  # Etiqueta del eje x: Predicciones
plt.ylabel('Actual')     # Etiqueta del eje y: Valores reales
plt.title('Confusion Matrix')  # Título del gráfico
plt.show()

# Imprimir el informe de clasificación
report = classification_report(y_test, y_pred, target_names=labels)
print(report)

# Guardar el modelo entrenado en un archivo para su posterior uso
joblib.dump(model, 'ecg_model.pkl')
