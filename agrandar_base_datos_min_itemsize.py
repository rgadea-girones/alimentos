import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

import matplotlib.pyplot as plt
from MIOPATIA_db import DB_management as db 


from scipy.interpolate import interp1d

# Supongamos que este es tu array original
original_array = np.random.rand(10, 401, 8)

# Crea un array para almacenar el resultado
interpolated_array = np.empty((220, 3))

# Crea los índices de entrada y salida
x_in = np.geomspace(1, 401, 401)
x_out = np.geomspace(1, 401, 220)

filename= "COPIA_PANDAS/reflujo_rafa_20240517.hdf"
filename1= "COPIA_PANDAS/reflujo_rafa_20240517_mejor2.hdf"

df = pd.HDFStore(filename,'a',complib="zlib",complevel=4)
df1= pd.HDFStore(filename1,'a',complib="zlib",complevel=4)

pre_p_e  = df.get('data/pollos_estado')
pre_p_e2 = pre_p_e.copy()

datos = df.get('data/tabla')
datos2 = datos.copy()

# Modificar un valor específico
#pre_p_e.at[4, 'Estado'] = 2
#pre_p_e['Estado'] = pre_p_e['Estado'].astype('int32')

# Modificar una columna entera

max_str_len = 50
df1.put('data/pollos_estado', pre_p_e2, format='table', data_columns=True, min_itemsize={'Primero': max_str_len, 'Ultimo': max_str_len, 'Pollo': max_str_len, 'Medida': max_str_len, 'Fecha': max_str_len, 'Estado': max_str_len})
df1.put('data/tabla', datos2 , format='table', data_columns=True)

df.close
df1.close