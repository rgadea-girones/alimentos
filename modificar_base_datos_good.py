import pandas as pd

filename= "COPIA_PANDAS\\reflujo_rafa_20240517.hdf"
df = pd.HDFStore(filename,'a',complib="zlib",complevel=4)
# Crear un DataFrame de ejemplo
pre_p_e  = df.get('data/pollos_estado')

# Modificar un valor específico
#pre_p_e.at[4, 'Estado'] = 2
#pre_p_e['Estado'] = pre_p_e['Estado'].astype('int32')

# Modificar una columna entera
df.put('data/pollos_estado', pre_p_e, format='table', data_columns=True)
df.close