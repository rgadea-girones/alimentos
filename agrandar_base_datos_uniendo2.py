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

filename= "COPIA_PANDAS\lomosP1_20240430_clasificado_experto_filtrado.hdf"
filename1= "COPIA_PANDAS\lomosP2_20240430_clasificado_experto_filtrado.hdf"
filename2= "COPIA_PANDAS\hdf_lomosP1P2_trainval_filtrado_def_good.hdf"
filename3= "COPIA_PANDAS\hdf_lomosP1P2_test_filtrado_def_good.hdf"
df = pd.HDFStore(filename,'a',complib="zlib",complevel=4)
df1= pd.HDFStore(filename1,'a',complib="zlib",complevel=4)
df_trainval=pd.HDFStore(filename2,'a',complib="zlib",complevel=4)
df_test=pd.HDFStore(filename3,'a',complib="zlib",complevel=4)

# Crear un DataFrame de ejemplo
pre_p_e  = df.get('data/pollos_estado')
pre_p_e1 = df1.get('data/pollos_estado')    
pre_p_e2 = pd.DataFrame(columns=pre_p_e.columns)
pre_p_e3 = pd.DataFrame(columns=pre_p_e.columns)




datos = df.get('data/tabla')
datos1= df1.get('data/tabla')
datos2 = pd.DataFrame(columns=datos.columns)
datos3 = pd.DataFrame(columns=datos.columns)

# Modificar un valor específico
#pre_p_e.at[4, 'Estado'] = 2
#pre_p_e['Estado'] = pre_p_e['Estado'].astype('int32')

# Modificar una columna entera

max_str_len = 50
df_trainval.put('data/pollos_estado', pre_p_e2, format='table', data_columns=True, min_itemsize={'Primero': max_str_len, 'Ultimo': max_str_len, 'Pollo': max_str_len, 'Medida': max_str_len, 'Fecha': max_str_len, 'Estado': max_str_len})
df_trainval.put('data/tabla', datos2 , format='table', data_columns=True)

df_test.put('data/pollos_estado', pre_p_e3, format='table', data_columns=True, min_itemsize={'Primero': max_str_len, 'Ultimo': max_str_len, 'Pollo': max_str_len, 'Medida': max_str_len, 'Fecha': max_str_len, 'Estado': max_str_len})
df_test.put('data/tabla', datos3 , format='table', data_columns=True)

n_freq=220

#recorrer el dataframe y agregar datos

for index, row in pre_p_e.iterrows():

    Primero_ori = int(row['Primero'])
    Ultimo_ori  = int(row['Ultimo'])
    Pollo=row['Pollo']
    pollo=int(Pollo)
    Medida=row['Medida']
    medida=int(Medida)
    fecha_hora=row['Fecha'] 
    estado  = row['Estado']
    data_aux=np.array(datos.iloc[Primero_ori:Ultimo_ori+1])
    Z=data_aux[:,3].reshape(-1,1)
    freq=data_aux[:,2].reshape(-1,1)
    fase=data_aux[:,4].reshape(-1,1)
    #vuelvo a calcular el resto de 6 parametros con los datos fitados
    Co              = 1E-12   # Valor capacidad en abierto sensor de puntas
    R_data = Z*np.cos(fase*np.pi/180)
    X_data = Z*np.sin(fase*np.pi/180)
    complex_aux         = R_data + X_data*1j
    admitance_aux       = 1./complex_aux
    G_data              = np.real(admitance_aux)
    Cp_data             = np.imag(admitance_aux)/(2*np.pi*freq)
    Err_data    = (Cp_data/Co).reshape(-1,1)
    Eri_data    = G_data/(Co*(2*np.pi*freq)).reshape(-1,1)
    E_data   = Err_data + -1*Eri_data*1j
    Er_mod_data  = np.abs(E_data).reshape(-1,1)
    Er_fase_data = np.angle(E_data).reshape(-1,1)

    if int(estado)<5:
        if pollo<26:
            Primero = len(datos2)
            Ultimo  = Primero + Ultimo_ori - Primero_ori
            datos_auxiliares= np.concatenate([freq,Z,fase,Err_data,Eri_data,Er_mod_data,Er_fase_data,R_data,X_data],axis=1 )
            datos_aux = np.concatenate([np.ones((n_freq,1),dtype=int)*(pollo),
                                                    np.ones((n_freq,1),dtype=int)*(medida),
                                                    datos_auxiliares],axis=1)
            data_aux_df = pd.DataFrame(datos_aux,columns=['Pollo','Medida','Freq','Z_mod',
                                                        'Z_Fase','Err','Eri','E_mod','E_fase','R','X'])
            pollito=pollo        
            pollo_aux = np.array([pollito,medida,fecha_hora,estado,Primero,Ultimo]).reshape(1,-1)
            pollo_aux_df = pd.DataFrame(pollo_aux, columns=['Pollo','Medida','Fecha','Estado','Primero','Ultimo'])        
            df_trainval.append('data/tabla', data_aux_df)
            df_trainval.append('data/pollos_estado',pollo_aux_df)
            datos2 = df_trainval.get('data/tabla')
        else:
            Primero = len(datos3)
            Ultimo  = Primero + Ultimo_ori - Primero_ori
            datos_auxiliares= np.concatenate([freq,Z,fase,Err_data,Eri_data,Er_mod_data,Er_fase_data,R_data,X_data],axis=1 )
            datos_aux = np.concatenate([np.ones((n_freq,1),dtype=int)*(pollo),
                                                    np.ones((n_freq,1),dtype=int)*(medida),
                                                    datos_auxiliares],axis=1)
            data_aux_df = pd.DataFrame(datos_aux,columns=['Pollo','Medida','Freq','Z_mod',
                                                        'Z_Fase','Err','Eri','E_mod','E_fase','R','X'])
            pollito=pollo-25
            pollo_aux = np.array([pollito,medida,fecha_hora,estado,Primero,Ultimo]).reshape(1,-1)
            pollo_aux_df = pd.DataFrame(pollo_aux, columns=['Pollo','Medida','Fecha','Estado','Primero','Ultimo'])        
            df_test.append('data/tabla', data_aux_df)
            df_test.append('data/pollos_estado',pollo_aux_df)
            datos3 = df_test.get('data/tabla')
for index, row in pre_p_e1.iterrows():

    Primero_ori = int(row['Primero'])
    Ultimo_ori  = int(row['Ultimo'])
    Pollo=row['Pollo']
    pollo=int(Pollo)
    Medida=row['Medida']
    medida=int(Medida)
    fecha_hora=row['Fecha'] 
    estado  = row['Estado']
    data_aux=np.array(datos1.iloc[Primero_ori:Ultimo_ori+1])
    Z=data_aux[:,3].reshape(-1,1)
    freq=data_aux[:,2].reshape(-1,1)
    fase=data_aux[:,4].reshape(-1,1)
    #vuelvo a calcular el resto de 6 parametros con los datos fitados
    Co              = 1E-12   # Valor capacidad en abierto sensor de puntas
    R_data = Z*np.cos(fase*np.pi/180)
    X_data = Z*np.sin(fase*np.pi/180)
    complex_aux         = R_data + X_data*1j
    admitance_aux       = 1./complex_aux
    G_data              = np.real(admitance_aux)
    Cp_data             = np.imag(admitance_aux)/(2*np.pi*freq)
    Err_data    = (Cp_data/Co).reshape(-1,1)
    Eri_data    = G_data/(Co*(2*np.pi*freq)).reshape(-1,1)
    E_data   = Err_data + -1*Eri_data*1j
    Er_mod_data  = np.abs(E_data).reshape(-1,1)
    Er_fase_data = np.angle(E_data).reshape(-1,1)

    if int(estado)<5:
        if pollo<76 and pollo!=0:
            Primero = len(datos2)
            Ultimo  = Primero + Ultimo_ori - Primero_ori
            datos_auxiliares= np.concatenate([freq,Z,fase,Err_data,Eri_data,Er_mod_data,Er_fase_data,R_data,X_data],axis=1 )
            datos_aux = np.concatenate([np.ones((n_freq,1),dtype=int)*(pollo),
                                                    np.ones((n_freq,1),dtype=int)*(medida),
                                                    datos_auxiliares],axis=1)
            data_aux_df = pd.DataFrame(datos_aux,columns=['Pollo','Medida','Freq','Z_mod',
                                                        'Z_Fase','Err','Eri','E_mod','E_fase','R','X'])
            pollito=pollo-25
            pollo_aux = np.array([pollito,medida,fecha_hora,estado,Primero,Ultimo]).reshape(1,-1)
            pollo_aux_df = pd.DataFrame(pollo_aux, columns=['Pollo','Medida','Fecha','Estado','Primero','Ultimo'])        
            df_trainval.append('data/tabla', data_aux_df)
            df_trainval.append('data/pollos_estado',pollo_aux_df)
            datos2 = df_trainval.get('data/tabla')
        elif pollo!=0:
            Primero = len(datos3)
            Ultimo  = Primero + Ultimo_ori - Primero_ori
            datos_auxiliares= np.concatenate([freq,Z,fase,Err_data,Eri_data,Er_mod_data,Er_fase_data,R_data,X_data],axis=1 )
            datos_aux = np.concatenate([np.ones((n_freq,1),dtype=int)*(pollo),
                                                    np.ones((n_freq,1),dtype=int)*(medida),
                                                    datos_auxiliares],axis=1)
            data_aux_df = pd.DataFrame(datos_aux,columns=['Pollo','Medida','Freq','Z_mod',
                                                        'Z_Fase','Err','Eri','E_mod','E_fase','R','X'])
            pollito=pollo-50
            pollo_aux = np.array([pollito,medida,fecha_hora,estado,Primero,Ultimo]).reshape(1,-1)
            pollo_aux_df = pd.DataFrame(pollo_aux, columns=['Pollo','Medida','Fecha','Estado','Primero','Ultimo'])        
            df_test.append('data/tabla', data_aux_df)
            df_test.append('data/pollos_estado',pollo_aux_df)
            datos3 = df_test.get('data/tabla')
        else:
            Primero = len(datos3)
            Ultimo  = Primero + Ultimo_ori - Primero_ori
            datos_auxiliares= np.concatenate([freq,Z,fase,Err_data,Eri_data,Er_mod_data,Er_fase_data,R_data,X_data],axis=1 )
            datos_aux = np.concatenate([np.ones((n_freq,1),dtype=int)*(pollo),
                                                    np.ones((n_freq,1),dtype=int)*(medida),
                                                    datos_auxiliares],axis=1)
            data_aux_df = pd.DataFrame(datos_aux,columns=['Pollo','Medida','Freq','Z_mod',
                                                        'Z_Fase','Err','Eri','E_mod','E_fase','R','X'])
            pollito=50
            pollo_aux = np.array([pollito,medida,fecha_hora,estado,Primero,Ultimo]).reshape(1,-1)
            pollo_aux_df = pd.DataFrame(pollo_aux, columns=['Pollo','Medida','Fecha','Estado','Primero','Ultimo'])        
            df_test.append('data/tabla', data_aux_df)
            df_test.append('data/pollos_estado',pollo_aux_df)
            datos3 = df_test.get('data/tabla')

# Convertir la columna 'Pollo' a números
pre_p_e2  = df_trainval.get('data/pollos_estado')
pre_p_e3 = df_test.get('data/pollos_estado')  
pollo_numeros = pd.to_numeric(pre_p_e2['Pollo'], errors='coerce')

# Obtener el valor máximo
max_pollo = pollo_numeros.max()

print("pollos en train",max_pollo)

# Convertir la columna 'Pollo' a números
pollo_numeros2 = pd.to_numeric(pre_p_e3['Pollo'], errors='coerce')

# Obtener el valor máximo
max_pollo2 = pollo_numeros2.max()

print("pollos en test",max_pollo2)
# Cerrar el archivo original
df.close
df1.close
df_trainval.close
df_test.close
