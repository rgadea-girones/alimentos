import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM,Bidirectional
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing import sequence
import datetime
import scipy.io as sio
# import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import sys
import os
# Obtener la ruta del directorio actual
current_dir = os.getcwd()

# Construir la ruta relativa al directorio que quieres agregar
relative_dir = os.path.join(current_dir, 'mis_pkgs/')

# Agregar la ruta relativa al sys.path
sys.path.insert(0, relative_dir)

from MIOPATIA_db import DB_management as db 

#lectura de los datos
filename = "hdf_28_06_atunes_agilent_clasificados.hdf"
with pd.HDFStore(filename,complib="zlib",complevel=4) as hdf_db:
    pre_p_e1  = hdf_db.get('data/pollos_estado')
    # p_e =pre_p_e1.drop_duplicates(subset = ['Pollo', 'Medida'],  keep = 'last').reset_index(drop = True)
    t    = hdf_db.get('data/tabla')
    X_train=np.zeros((pre_p_e1.shape[0],401,8))
    y_train=np.zeros((pre_p_e1.shape[0],2))
    x=0
    for index, row in pre_p_e1.iterrows():   # El primer registro no se toma en cuenta porque es basura
        Primero = int(row['Primero'])
        Ultimo  = int(row['Ultimo'])
        estado  = int(row['Estado'])
        print(Primero)
        print(Ultimo)
        print(estado)
        if estado == 0 or estado== 1:
            target = (1,0)
        else:
            target = (0,1)
        pepito=np.array(t.iloc[Primero:Ultimo+1])
        # #print(pepito.shape)
        X_train[x]=pepito[:,3:11]
        #print(X_train[x][0:4,:])       
        y_train[x]=target
        x=x+1
print(X_train.shape)
print(y_train.shape)


#filtrado de las dos primeras muestras
X_train_filtrado = X_train[2:][:,:]
y_train_filtrado = y_train[2:]
print(X_train_filtrado.shape)
print(y_train_filtrado.shape)
print(X_train_filtrado[0][:,:])


#normalizacion de los datos
scaler = MinMaxScaler(feature_range=(0, 1))
data_2d = X_train_filtrado.reshape(-1, X_train_filtrado.shape[-1])
normalized_data_2d = scaler.fit_transform(data_2d)
X_train_Normalizado=normalized_data_2d.reshape(X_train_filtrado.shape)
y_train_Normalizado=y_train_filtrado # los valores ya estaban normalizados
print(X_train_Normalizado[0])

savedict={'X_train_Normalizado':X_train_Normalizado,'y_train_Normalizado':y_train_Normalizado}

sio.savemat('Train_Normalizado.mat',savedict)


#creacion  de la red y entrenamiento
model = Sequential()
model.add(Bidirectional(LSTM(50, return_sequences=True),input_shape=(401, 8)))
model.add(Bidirectional(LSTM(50, return_sequences=True)))
model.add(Bidirectional(LSTM(50, return_sequences=True)))
model.add(Bidirectional(LSTM(50, return_sequences=False)))
model.add(Dense(50, activation='sigmoid'))
model.add(Dense(2, activation='sigmoid'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(X_train_Normalizado, y_train_Normalizado, epochs=3, batch_size=20)


# Final evaluation of the model
scores = model.evaluate(X_train_Normalizado, y_train_Normalizado, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))


#obtención d ela matriz de confusion
y_pred = model.predict(X_train_Normalizado)
y_pred2=np.argmax(y_pred,axis=1)
cm=confusion_matrix(np.argmax(y_train_Normalizado, axis=1), y_pred2)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.show()


#salvado de la red 
model.save('saved_model/my_model3')