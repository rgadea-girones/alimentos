
import pyvisa
import time
import sys
import json
import fit_library as fit
import numpy as np
import pandas as pd
import MIOPATIA_visa as mv
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from threading import Thread, Event, RLock

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMessageBox
from collections import OrderedDict
import ctypes

# PYINSTALLER : pyinstaller -D --specpath .\EXE miopatia.py

qtCreatorFile = "MIOPATIA.ui"


Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class DATA(object):
    """ DATA shared among different parts of the application.
        Reads information from JSON file.
        Writes JSON file with information if required
    """

    def __init__(self,read=True):

        self.filename = "miopatia.json"
        self.def_cfg=[]

        # Figure handlers
        self.fig1 = Figure()
        self.fig2 = Figure()
        self.fig3 = Figure()
        # Axes for plotting
        self.axes={'ax0':0,'ax1':0,'ax2':0,'ax3':0,'ax4':0}

        if (read==True):
            self.config_read()
        else:
            # These are the default values.
            self.def_cfg= {'f_inicial':{'value':10, 'limits':[10.0,100.0E6],'type':'float'},
                            'f_final' :{'value':10000000, 'limits':[10.0,100.0E6],'type':'float'},
                            'n_puntos':{'value':25, 'limits':[1,801],'type':'int'},
                            'ancho_banda':{'value':3, 'limits':[1,5],'type':'int'},
                            'vosc':{'value':0.5, 'limits':[0.0,1.0],'type':'float'},
                            'tipo_barrido':{'value':1, 'limits':[0,1],'type':'int'},
                            'DC_bias':{'value':0, 'limits':[0,1],'type':'int'},
                            'nivel_DC':{'value':0, 'limits':[-40.0,40.0],'type':'float'},
                            'avg':{'value':0, 'limits':[0,1],'type':'int'},
                            'n_medidas_punto':{'value':1, 'limits':[1,256],'type':'int'},
                            'load_mfile_name':"./medida.csv",
                            'save_mfile_name':"./medida.csv",
                            'load_cal_file_name':"./calibracion.cal",
                            'save_cal_file_name':"./calibracion_new.cal",
                            'load_h5file_name':"./espectros.hdf",
                            'def_path':"./",
                            'conf_cal':{'value':0, 'limits':[0,1],'type':'int'},
                            'c_load':{'value':500, 'limits':[0,1E6],'type':'float'},
                            'g_load':{'value':0.1, 'limits':[0,1E6],'type':'float'},
                            'pto_cal':{'value':1, 'limits':[0,1],'type':'int'},
                            'combox':['|Z|','F.Z','E\'r','E\'\'r','|Er|','F.Er'],
                            'combox_fit':['lm','trf','dogbox'],
                            'load_mfile_fit':"./medida.csv",
                            'origen_fit':{'value':0, 'limits':[0,1],'type':'int'},
                            # FIT PARAMETERS
                            'param_fit':{'names' :['n_func_fit','f_low_fit','f_high_fit',
                                                   'param_A1','param_B1','param_C1','param_D1',
                                                   'param_B2','param_C2','param_D2',
                                                   'param_B3','param_C3','param_D3'],
                                         'value' :[ 1,0,100E6,
                                                    0,0,0,0,
                                                    0,0,0,
                                                    0,0,0],
                                         'limits':[[1,3],[0,100E6],[0,100E6],
                                                   [-1E12,1E12],[-1E12,1E12],[-1E12,1E12],[-1E12,1E12],
                                                   [-1E12,1E12],[-1E12,1E12],[-1E12,1E12],
                                                   [-1E12,1E12],[-1E12,1E12],[-1E12,1E12]],
                                         'type'  :['int','float','float',
                                                   'float','float','float','float',
                                                   'float','float','float',
                                                   'float','float','float']},

                            #'n_func_fit': {'value':1, 'limits':[1,3],'type':'int'},
                            #'f_low_fit': {'value':0, 'limits':[0,100E6],'type':'float'},
                            #'f_high_fit': {'value':100E6, 'limits':[0,100E6],'type':'float'},
                            'VI_ADDRESS': 'GPIB0::17::INSTR',
                            'GPIB_timeout':12000
                            }
            self.config_write()


        # CONSTANTS
        self.E0              = 8.854e-12 # Vacuum permitivity
        self.Adj_center      = 100000    # Central Freq. for certain calibrations
        self.Adj_up_limit_a  = 1E-9      # Limite superior C (Faradios) del ajuste
                                         # de electrodos paralelos para electrodo TIPO A
        self.Adj_low_limit_a = 7E-10     # Limite inferior C (Faradios) del ajuste
                                         # de electrodos paralelos para electrodo TIPO A
        self.Adj_up_limit_b  = 2E-11     # Limite superior C (Faradios) del ajuste
                                         # de electrodos paralelos para electrodo TIPO B
        self.Adj_low_limit_b = 1.2E-11   # Limite inferior C (Faradios) del ajuste
                                         # de electrodos paralelos para electrodo TIPO B

        # Constantes para la calibración por carga
        self.Load_center     = 100000    # Frecuencia central 100KHz donde se realiza
                                         # la primera medida por carga.
        self.Load_ave        = 4         # Media de 4 medidas para el ajuste por carga
        self.Load_bw         = 5         # Bandwidth 5 (Mejor reolución - más lento) para el ajuste por carga.
        self.Load_up_limit_a = 5.05E-11  # 50.5 pF Limite superior del valor de la capacidad para la carga en el electrodo A
        self.Load_lo_limit_a = 4.95E-11  # 49.5 pF Limite inferior del valor de la capacidad para la carga en el electrodo A
        self.Load_up_limit_b = 5.05E-12  # 5.05 pF Limite superior del valor de la capacidad para la carga en el electrodo B
        self.Load_lo_limit_b = 4.95E-12  # 4.95 pF Limite inferior del valor de la capacidad para la carga en el electrodo B
        self.Load_up_limit_c = 1.55E-12  # 1.55 pF Limite superior del valor de la capacidad para la carga en el electrodo C
        self.Load_lo_limit_c = 1.45E-12  # 1.45 pF Limite inferior del valor de la capacidad para la carga en el electrodo C
        self.Load_up_limit_d = 1.55E-12  # 1.55 pF Limite superior del valor de la capacidad para la carga en el electrodo D
        self.Load_lo_limit_d = 1.45E-12  # 1.45 pF Limite inferior del valor de la capacidad para la carga en el electrodo D
        self.Load_g          = 0         # Valor de la admitancia de la carga

        # Constantes de calibración de abiertos - Caso calibración Carga-Open-Short
        self.Open_r          = 1E11      # Resistencia de 100GOhm. Valor esperado de resistencia en el abierto.
        self.Open_l          = 0         # Valor de la inductancia esperada en el abierto
        # Constantes de calibración de cortos - Caso calibración Carga-Open-Short
        self.Short_r         = 0         # Valor de la resitencia espreada del corto
        self.Short_l         = 0         # Valor de la inductancia esperada del corto.

        # Constantes de calibración de abiertos - Caso calibración Open-Short
        self.Open_c2         = 0         # Capacidad esperada para en el abierto.
        self.Open_g2         = 0         # Valor de la admitancia esperada en el abierto.
        # Constantes de calibración de cortos  - Caso calibración Open-Short
        self.Short_r2        = 0         # Valor de la resitencia espreada del corto
        self.Short_l2        = 0         # Valor de la inductancia esperada del corto.
        # Constantes de calibración de carga - Caso calibración Open-Short
        self.Load_r2         = 0         # Valor de la resitencia espreada del corto
        self.Load_l2         = 0         # Valor de la inductancia esperada del corto.

        self.Bw              = 3         # Valor del Bandwidth

        # Constantes para calibracion con platos
        self.D_elec_a        = 0.038     # Diametro del electrodo A - 38mm
        self.D_elec_b        = 0.005     # Diametro del electrodo B - 5 mm

        self.Nop             = 1         # ???
        self.Swe_type        = 'LIN'

        # Inicializacion de vectores de datos
        self.freq            = np.array([])
        self.Z_mod_data      = np.array([])
        self.Z_fase_data     = np.array([])
        self.Err_data        = np.array([])
        self.Eri_data        = np.array([])
        self.Er_mod_data     = np.array([])
        self.Er_fase_data    = np.array([])
        self.R_data          = np.array([])
        self.X_data          = np.array([])
        self.COM_OPEN_data_R = np.array([])
        self.COM_OPEN_data_X = np.array([])
        self.COM_SHORT_data_R = np.array([])
        self.COM_SHORT_data_X = np.array([])
        self.COM_LOAD_data_R = np.array([])
        self.COM_LOAD_data_X = np.array([])

        self.Co              = 1E-12   # Valor capacidad en abierto sensor de puntas
        self.stop_continue   = 0

        self.cal_points      = 100

        self.fit_params_glb = []

        self.fit_data_frame = []

        self.pollo_fitado = 0

    def config_write(self):
        writeName = self.filename
        try:
            with open(writeName,'w') as outfile:
                json.dump(self.def_cfg, outfile, indent=4, sort_keys=False)
        except IOError as e:
            print(e)

    def config_read(self):
        try:
            with open(self.filename,'r') as infile:
                self.def_cfg = json.load(infile)
        except IOError as e:
            print(e)


class BACK_END(object):
    """ Code associatted to controls, buttons, text boxes etc.
    """
    def __init__(self,parent_wdg,shared_data,visa):
        self.sd = shared_data
        self.pw = parent_wdg
        self.vi = visa
        self.flag = True

     # Controlled casting to avoid data intro errors. Read text or button_ID
    def value_control(self,objeto,limits=[0,1E12],type='int',qt_obj="QLineEdit"):
        try:
            if qt_obj == "QLineEdit":
                aux = eval(type)(objeto.text())
            elif qt_obj == "QButtonGroup":
                aux = eval(type)(objeto.checkedId())
            elif qt_obj == "QCheckBox":
                aux = eval(type)(objeto.isChecked())

            if ((aux >= limits[0]) and (aux <= limits[1])):
                return eval(type)(aux)
            else:
                if (aux > limits[1]):
                    objeto.setText(str(limits[1]))
                    return eval(type)(limits[1])
                else:
                    if (aux < limits[0]):
                        objeto.setText(str(limits[0]))
                        return eval(type)(limits[0])
        except ValueError:
            self.vi.append_plus("ERROR EN VALOR")
            objeto.setText(str(limits[0]))
            return limits[0]

    def save_config(self):
        self.sd.config_write()

    def redraw_measure(self):
        # self.vi.append_plus("CONTINUAR")
        if (len(self.sd.freq))>0:
            self.vi.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                     self.pw.comboBox_trazaB.currentIndex())
        else:
            self.vi.append_plus("NO HAY DATOS QUE MOSTRAR")
        self.pw.canvas1.draw()

    def medir(self):
        self.pw.MEDIR.setEnabled(False)
        app.processEvents()
        self.vi.append_plus("MEDIR")
        self.vi.config_measurement()
        self.vi.measure()
        self.vi.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                 self.pw.comboBox_trazaB.currentIndex())
        self.pw.canvas1.draw()
        self.pw.MEDIR.setEnabled(True)

    def load_m(self):
        self.vi.append_plus("CARGA MEDIDA")
        file = self.sd.def_cfg['load_mfile_name']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','Z_mod','Z_Fase', 'Err',
                                    'Eri','E_mod','E_fase','R','X'],
                            delim_whitespace=True)
        except:
            self.vi.append_plus("Fichero no encontrado\n")
        else:
            self.vi.append_plus(file)
            self.vi.show_data(self.pw.comboBox_trazaA.currentIndex(),
                              self.pw.comboBox_trazaB.currentIndex(),
                              data)
            self.pw.canvas2.draw()

    def load_m_fit(self):
        self.vi.append_plus("CARGA MEDIDA")
        file = self.sd.def_cfg['load_mfile_fit']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','Z_mod','Z_Fase', 'Err',
                                    'Eri','E_mod','E_fase','R','X'],
                            delim_whitespace=True)
        except:
            self.vi.append_plus("Fichero no encontrado\n")
        else:
            self.vi.append_plus(file)
            self.vi.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                                  self.pw.comboBox_fit_alg.currentText(),
                                  data)
            self.pw.canvas3.draw()

    def load_h5_fit(self):
        self.vi.append_fit("CARGA MEDIDA BASE DATOS H5")
        file = self.sd.def_cfg['load_h5file_name']
        try:
            hdf_db = pd.HDFStore(file,'r',complib="zlib",complevel=4)
            pollos = hdf_db.get('data/index/pollos')
            indice_medidas = hdf_db.get('data/index/medidas')
            tabla = hdf_db.get('data/tabla')
            #columns=['Freq','Z_mod','Z_Fase','Err','Eri','E_mod','E_fase','R','X']
        except:
            self.vi.append_fit("Fichero no encontrado\n")
        else:
            self.vi.append_fit(file)
            pollo_sel = pollos[int(self.pw.spinBox_pollo.value())]
            inicio_medida = indice_medidas['primero'][int(pollo_sel[self.pw.spinBox_medida.value()])]
            fin_medida    = indice_medidas['ultimo'][int(pollo_sel[self.pw.spinBox_medida.value()])]
            data = tabla[inicio_medida:fin_medida]
            self.sd.pollo_fitado = int(self.pw.spinBox_pollo.value())
            self.vi.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                                  self.pw.comboBox_fit_alg.currentText(),
                                  data)
            self.pw.canvas3.draw()
            hdf_db.close()


    def measure_fit(self):
        self.vi.append_fit("AJUSTE DE DATOS MEDIDOS")
        data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                     np.reshape(self.sd.Z_mod_data,(-1,1)),
                                     np.reshape(self.sd.Z_fase_data,(-1,1)),
                                     np.reshape(self.sd.Err_data,(-1,1)),
                                     np.reshape(self.sd.Eri_data,(-1,1)),
                                     np.reshape(self.sd.Er_mod_data,(-1,1)),
                                     np.reshape(self.sd.Er_fase_data,(-1,1)),
                                     np.reshape(self.sd.R_data,(-1,1)),
                                     np.reshape(self.sd.X_data,(-1,1))],
                                     axis=1)
        data_frame = pd.DataFrame(data_array,
                                  columns=['Freq','Z_mod','Z_Fase','Err','Eri',
                                           'E_mod','E_fase','R','X'])
        self.vi.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                              self.pw.comboBox_fit_alg.currentText(),
                              data_frame)
        self.pw.canvas3.draw()

    def save_fit(self):
        self.vi.append_fit("SALVA FIT BASE DATOS H5")
        file = self.sd.def_cfg['load_h5file_name']
        #try:
        hdf_db = pd.HDFStore(file,'a',complib="zlib",complevel=4)
        fit_data = hdf_db.get('data/fit')
        print(self.sd.pollo_fitado)
        fit_data.loc[self.sd.pollo_fitado]=self.sd.fit_data_frame.to_numpy()
        hdf_db.put('data/fit',fit_data)
        hdf_db.close()
        #except:
        #    self.vi.append_fit("Error en Base de Datos\n")
        #else:


    def save_m(self):
        def justify(input_str,n_char):
            string = input_str+''.join([' ']*(n_char-len(input_str)))
            return string.strip('"')

        self.vi.append_plus("SALVA MEDIDA")
        file_save = self.sd.def_cfg['save_mfile_name']
        try:
            data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                         np.reshape(self.sd.Z_mod_data,(-1,1)),
                                         np.reshape(self.sd.Z_fase_data,(-1,1)),
                                         np.reshape(self.sd.Err_data,(-1,1)),
                                         np.reshape(self.sd.Eri_data,(-1,1)),
                                         np.reshape(self.sd.Er_mod_data,(-1,1)),
                                         np.reshape(self.sd.Er_fase_data,(-1,1)),
                                         np.reshape(self.sd.R_data,(-1,1)),
                                         np.reshape(self.sd.X_data,(-1,1))],
                                         axis=1)
            data_frame = pd.DataFrame(data_array,
                                      columns=['Freq','Z_mod','Z_Fase','Err','Eri',
                                               'E_mod','E_fase','R','X'])
            data_frame.to_csv(file_save, sep=' ', index=False, float_format='%+13.6e',
                              # header=[justify('Freq',15).strip('"'), justify('Z_mod',15),
                              #         justify('Z_Fase',15), justify('Err',15),
                              #         justify('Eri',15), justify('E_mod',15),
                              #         justify('E_fase',15), justify('R',15),
                              #         justify('X',15)]
                              header=True)
        except:
            self.vi.append_plus("El fichero de datos no se ha podido salvar\n")
        else:
            self.vi.append_plus(file_save)


    def go_cal(self):
        self.vi.append_plus("CALIBRAR")
        self.vi.config_calibration()
        if (self.sd.def_cfg['conf_cal']['value'] == 0):
            # Calibración CARGA - ABIERTO - CORTO
            self.vi.cal_load_open_short()

        elif (self.sd.def_cfg['conf_cal']['value'] == 1):
            # Calibración ABIERTO - CORTO
            self.vi.cal_open_short()

    def load_cal(self):
        self.vi.append_plus("CARGAR CALIBRACIÓN")
        file = self.sd.def_cfg['load_cal_file_name']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','OPEN_R','OPEN_X','SHORT_R','SHORT_X',
                                     'LOAD_R','LOAD_X'],
                            delim_whitespace=True)
        except:
            self.vi.append_plus("Fichero no encontrado\n")
        else:
            self.vi.append_plus(file)
            self.sd.COM_OPEN_data_R = data['OPEN_R']
            self.sd.COM_OPEN_data_X = data['OPEN_X']
            self.sd.COM_SHORT_data_R = data['SHORT_R']
            self.sd.COM_SHORT_data_X = data['SHORT_X']
            self.sd.COM_LOAD_data_R = data['LOAD_R']
            self.sd.COM_LOAD_data_X = data['LOAD_X']

            self.vi.send_calibration()


    def save_cal(self):
        self.vi.append_plus("SALVAR CALIBRACIÓN")
        self.vi.get_calibration()

        file_save = self.sd.def_cfg['save_cal_file_name']
        try:
            print(len(self.sd.COM_OPEN_data_R))

            data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                         np.reshape(self.sd.COM_OPEN_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_OPEN_data_X,(-1,1)),
                                         np.reshape(self.sd.COM_SHORT_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_SHORT_data_X,(-1,1)),
                                         np.reshape(self.sd.COM_LOAD_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_LOAD_data_X,(-1,1))]
                                         ,axis=1)
            data_frame = pd.DataFrame(data_array,
                                      columns=['Freq','OPEN_R','OPEN_X','SHORT_R','SHORT_X',
                                               'LOAD_R','LOAD_X'])
            data_frame.to_csv(file_save, sep=' ', index=False, float_format='%+13.6e',header=True)
        except:
            self.vi.append_plus("El fichero de calibración no se ha podido salvar\n")
        else:
            self.vi.append_plus(file_save)


    def default_data(self):

        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                if self.pw.mirror[i]['qt'] == 'QLineEdit':
                    eval("self.pw."+j).setText(str(self.sd.def_cfg[i]['value']))
                elif self.pw.mirror[i]['qt'] == 'QButtonGroup':
                    eval("self.pw."+j).button(self.sd.def_cfg[i]['value']).setChecked(True)
                elif self.pw.mirror[i]['qt'] == 'QCheckBox':
                    eval("self.pw."+j).setChecked(self.sd.def_cfg[i]['value'])

        for i in self.pw.paths.keys():
            aux = self.pw.paths[i]
            eval("self.pw." + aux).setText(str(self.sd.def_cfg[i]))

        for i in self.pw.others.keys():
            aux = self.pw.others[i]['array']
            if self.pw.others[i]['qt'] == 'QLineEdit':
                eval("self.pw." + aux).setText(str(self.sd.def_cfg[i]['value']))
            elif self.pw.others[i]['qt'] == 'QButtonGroup':
                eval("self.pw." + aux).button(self.sd.def_cfg[i]['value']).setChecked(True)
            elif self.pw.others[i]['qt'] == 'QCheckBox':
                eval("self.pw." + aux).setChecked(self.sd.def_cfg[i]['value'])

        for i in self.pw.fit_param.keys():
            if i[0:6] == 'lparam':
                pass
            elif i[0:5] == 'param':
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                eval("self.pw." + self.pw.fit_param[i]['array'] + "_L").setText(str(self.sd.def_cfg['param_fit']['limits'][pos][0]))
                eval("self.pw." + self.pw.fit_param[i]['array'] + "_H").setText(str(self.sd.def_cfg['param_fit']['limits'][pos][1]))
                eval("self.pw." + self.pw.fit_param[i]['array']).setText(str(self.sd.def_cfg['param_fit']['value'][pos]))
            else:
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                eval("self.pw." + self.pw.fit_param[i]['array']).setText(str(self.sd.def_cfg['param_fit']['value'][pos]))


        # Default fit magnitude ABS(EPSILON)
        self.pw.comboBox_mag_fit.setCurrentIndex(4)

        self.store_data()
        self.store_fit()

    def store_fit(self):

        # Add fit parameters to params
        for i in self.pw.fit_param.keys():
            if i[0:6] == 'lparam':
                pass
            else:
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                aux = self.pw.fit_param[i]['array']
                new_data = self.value_control(eval("self.pw."+ aux ), self.sd.def_cfg['param_fit']['limits'][pos],
                                            type = self.sd.def_cfg['param_fit']['type'][pos],
                                            qt_obj = self.pw.fit_param[i]['qt'])
                self.sd.def_cfg['param_fit']['value'][pos] = new_data

        # Add boundary array to params
        for i in self.pw.fit_param.keys():
            if i[0:5] == 'param':
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                aux = self.pw.fit_param[i]['array']
                new_data_L = self.value_control(eval("self.pw."+ aux +"_L" ), [-1E12,1E12],
                                              type = self.sd.def_cfg['param_fit']['type'][pos],
                                              qt_obj = self.pw.fit_param[i]['qt'])
                new_data_H = self.value_control(eval("self.pw."+ aux +"_H" ), [-1E12,1E12],
                                              type = self.sd.def_cfg['param_fit']['type'][pos],
                                              qt_obj = self.pw.fit_param[i]['qt'])
                self.sd.def_cfg['param_fit']['limits'][pos] = [new_data_L, new_data_H]



    def store_data(self):
        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                new_data = self.value_control(eval("self.pw."+j), self.sd.def_cfg[i]['limits'],
                                              type = self.sd.def_cfg[i]['type'],
                                              qt_obj = self.pw.mirror[i]['qt'])
                def_data = self.sd.def_cfg[i]['value']
                if def_data != new_data:
                    self.sd.def_cfg[i]['value'] = new_data
                    break

        for i in self.pw.paths.keys():
            new_data = eval("self.pw."+self.pw.paths[i]).text()
            self.sd.def_cfg[i] = new_data

        for i in self.pw.others.keys():
            aux = self.pw.others[i]['array']
            new_data = self.value_control(eval("self.pw." + aux), self.sd.def_cfg[i]['limits'],
                                          type = self.sd.def_cfg[i]['type'],
                                          qt_obj = self.pw.others[i]['qt'])
            self.sd.def_cfg[i]['value'] = new_data

        # UPDATE
        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                if self.pw.mirror[i]['qt'] == 'QLineEdit':
                    eval("self.pw."+j).setText(str(self.sd.def_cfg[i]['value']))
                elif self.pw.mirror[i]['qt'] == 'QButtonGroup':
                    eval("self.pw."+j).button(self.sd.def_cfg[i]['value']).setChecked(True)
                elif self.pw.mirror[i]['qt'] == 'QCheckBox':
                    eval("self.pw."+j).setChecked(self.sd.def_cfg[i]['value'])



        print(self.sd.def_cfg)



class BROWSERS(object):
    """ File Browsers for config files, input and output files etc.
    """
    def __init__(self,parent_wdg,shared_data):
        self.sd = shared_data
        self.pw = parent_wdg

    def load_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path.setText(self.sd.def_cfg['load_mfile_name'])


    def save_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.pw,
                                        'Salvar fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.save_path.setText(self.sd.def_cfg['save_mfile_name'])


    def load_calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Fichero de calibración',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.cal)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_cal_file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_2.setText(self.sd.def_cfg['load_cal_file_name'])


    def save_calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.pw,
                                        'Fichero de calibración',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.cal)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_cal_file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.save_path_2.setText(self.sd.def_cfg['save_cal_file_name'])

    def load_fit_data_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero de medidas',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_fit'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_3.setText(self.sd.def_cfg['load_mfile_fit'])

    def load_h5file_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.hdf)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_h5file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_4.setText(self.sd.def_cfg['load_h5file_name'])
        with pd.HDFStore(self.sd.def_cfg['load_h5file_name'],'r',complib="zlib",complevel=4) as hdf_db:
            pollos = hdf_db.get('data/index/pollos').to_numpy(dtype=float)
        size = np.shape(pollos)
        n_medidas = size[0]
        n_pollos  = size[1]
        self.pw.spinBox_medida.setMaximum(n_medidas-1)
        self.pw.spinBox_pollo.setMaximum(n_pollos-1)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self,data):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./pollo.jpeg'))
        self.show()
        # Shared data
        self.sd = data
        # Classes Instantiation
        self.brw = BROWSERS(self,data)
        # VISA start
        self.vi  = mv.VISA(self.sd,[self.textBrowser,self.textBrowser_2],self.textBrowser_3)
        self.be  = BACK_END(self,data,self.vi)


        ######### Combos Initialization and RadiButton Groups creation #########
        # Button groups creation
        def Rbutton_group(button_array):
            bg_config_cal = QtWidgets.QButtonGroup()
            radioButton = button_array
            j=0
            for i in radioButton:
                bg_config_cal.addButton(i)
                bg_config_cal.setId(i,j)
                j+=1
            return bg_config_cal

        self.comboBox_trazaA.addItems(self.sd.def_cfg['combox'])
        self.comboBox_trazaB.addItems(self.sd.def_cfg['combox'])
        self.comboBox_mag_fit.addItems(self.sd.def_cfg['combox'])
        self.comboBox_fit_alg.addItems(self.sd.def_cfg['combox_fit'])
        self.bg_xaxis      = Rbutton_group([self.radioButton_lineal, self.radioButton_log])
        self.bg_xaxis_2    = Rbutton_group([self.radioButton_lineal_2, self.radioButton_log_2])
        self.bg_DC         = Rbutton_group([self.radioButton_DC_ON, self.radioButton_DC_OFF])
        self.bg_DC_2       = Rbutton_group([self.radioButton_DC_ON_2, self.radioButton_DC_OFF_2])
        self.bg_config_cal = Rbutton_group([self.radioButton_config_cal_1, self.radioButton_config_cal_2])
        self.bg_pto_cal    = Rbutton_group([self.radioButton_pto_cal_medidor, self.radioButton_pto_cal_usuario])


        ############## Widget to internal variables assignment #################
        # Data Mirroring through GUI
        self.mirror =  {'f_inicial':   {'array':['f_inicial', 'f_inicial_2'],'qt':'QLineEdit'},
                        'f_final':     {'array':['f_final',   'f_final_2'],  'qt':'QLineEdit'},
                        'n_puntos':    {'array':['n_puntos',  'n_puntos_2'],  'qt':'QLineEdit'},
                        'ancho_banda': {'array':['ancho_banda', 'ancho_banda_2'],  'qt':'QLineEdit'},
                        'vosc':        {'array':['vosc',        'vosc_2'],   'qt':'QLineEdit'},
                        'tipo_barrido':{'array':['bg_xaxis', 'bg_xaxis_2'],  'qt':'QButtonGroup'},
                        'DC_bias':     {'array':['bg_DC',    'bg_DC_2'],     'qt':'QButtonGroup'},
                        'nivel_DC':    {'array':['nivel_DC', 'nivel_DC_2'],  'qt':'QLineEdit'},
                        'avg':         {'array':['avg',      'avg_2'],  'qt':'QCheckBox'},
                        'n_medidas_punto':{'array':['n_medidas_punto', 'n_medidas_punto_2'],  'qt':'QLineEdit'}}
        # Paths
        self.paths = {'load_mfile_name':'load_path',
                      'save_mfile_name':'save_path',
                      'load_cal_file_name':'load_path_2',
                      'save_cal_file_name':'save_path_2'}
        # Other controls
        self.others = {'conf_cal':{'array':'bg_config_cal', 'qt':'QButtonGroup'},
                       'c_load':{'array':'c_load', 'qt':'QLineEdit'},
                       'g_load':{'array':'g_load', 'qt':'QLineEdit'},
                       'pto_cal':{'array':'bg_pto_cal', 'qt':'QButtonGroup'}
                       }
        #Fit Parameters
        self.fit_param = OrderedDict(
                         [
                         ('n_func_fit',{'array':'n_func', 'qt':'QLineEdit'}),
                         ('f_low_fit' ,{'array':'f_low', 'qt':'QLineEdit'}),
                         ('f_high_fit',{'array':'f_high', 'qt':'QLineEdit'}),
                         ('param_A1',{'array':'param_A1', 'qt':'QLineEdit'}),
                         ('param_B1',{'array':'param_B1', 'qt':'QLineEdit'}),
                         ('param_C1',{'array':'param_C1', 'qt':'QLineEdit'}),
                         ('param_D1',{'array':'param_D1', 'qt':'QLineEdit'}),
                         ('param_B2',{'array':'param_B2', 'qt':'QLineEdit'}),
                         ('param_C2',{'array':'param_C2', 'qt':'QLineEdit'}),
                         ('param_D2',{'array':'param_D2', 'qt':'QLineEdit'}),
                         ('param_B3',{'array':'param_B3', 'qt':'QLineEdit'}),
                         ('param_C3',{'array':'param_C3', 'qt':'QLineEdit'}),
                         ('param_D3',{'array':'param_D3', 'qt':'QLineEdit'}),
                         ('lparam_A1_H',{'array':'param_A1_H', 'qt':'QLineEdit'}),
                         ('lparam_B1_H',{'array':'param_B1_H', 'qt':'QLineEdit'}),
                         ('lparam_C1_H',{'array':'param_C1_H', 'qt':'QLineEdit'}),
                         ('lparam_D1_H',{'array':'param_D1_H', 'qt':'QLineEdit'}),
                         ('lparam_B2_H',{'array':'param_B2_H', 'qt':'QLineEdit'}),
                         ('lparam_C2_H',{'array':'param_C2_H', 'qt':'QLineEdit'}),
                         ('lparam_D2_H',{'array':'param_D2_H', 'qt':'QLineEdit'}),
                         ('lparam_B3_H',{'array':'param_B3_H', 'qt':'QLineEdit'}),
                         ('lparam_C3_H',{'array':'param_C3_H', 'qt':'QLineEdit'}),
                         ('lparam_D3_H',{'array':'param_D3_H', 'qt':'QLineEdit'}),
                          ('lparam_A1_L',{'array':'param_A1_L', 'qt':'QLineEdit'}),
                          ('lparam_B1_L',{'array':'param_B1_L', 'qt':'QLineEdit'}),
                          ('lparam_C1_L',{'array':'param_C1_L', 'qt':'QLineEdit'}),
                          ('lparam_D1_L',{'array':'param_D1_L', 'qt':'QLineEdit'}),
                          ('lparam_B2_L',{'array':'param_B2_L', 'qt':'QLineEdit'}),
                          ('lparam_C2_L',{'array':'param_C2_L', 'qt':'QLineEdit'}),
                          ('lparam_D2_L',{'array':'param_D2_L', 'qt':'QLineEdit'}),
                          ('lparam_B3_L',{'array':'param_B3_L', 'qt':'QLineEdit'}),
                          ('lparam_C3_L',{'array':'param_C3_L', 'qt':'QLineEdit'}),
                          ('lparam_D3_L',{'array':'param_D3_L', 'qt':'QLineEdit'})
                         ]
                         )

        ########### Controls Defaults ############
        self.be.default_data()


        ############# Function to Widget assignment

        # Clicked Calls
        clicked  = [{'wdg':self.toolButton_load,   'func':self.brw.load_mfile_browser},
                    {'wdg':self.toolButton_load_4,   'func':self.brw.load_h5file_browser},
                    {'wdg':self.toolButton_save,   'func':self.brw.save_mfile_browser},
                    {'wdg':self.toolButton_load_2, 'func':self.brw.load_calibration_file_browser},
                    {'wdg':self.toolButton_save_2, 'func':self.brw.save_calibration_file_browser},
                    {'wdg':self.REDRAW_MEASURE,    'func':self.be.redraw_measure},
                    {'wdg':self.MEDIR,             'func':self.be.medir},
                    {'wdg':self.LOAD_M,            'func':self.be.load_m},
                    {'wdg':self.SAVE_M,            'func':self.be.save_m},
                    {'wdg':self.GO_CAL,            'func':self.be.go_cal},
                    {'wdg':self.LOAD_CAL,          'func':self.be.load_cal},
                    {'wdg':self.SAVE_CAL,          'func':self.be.save_cal},
                    {'wdg':self.SAVE_cfg,          'func':self.be.save_config},
                    {'wdg':self.LOAD_fit_data,     'func':self.be.load_m_fit},
                    {'wdg':self.toolButton_load_3, 'func':self.brw.load_fit_data_browser},
                    {'wdg':self.AJUSTA,            'func':self.be.measure_fit},
                    {'wdg':self.LOAD_fit_data_2,   'func':self.be.load_h5_fit},
                    {'wdg':self.SAVE_fit,          'func':self.be.save_fit}]

        # Fit calls
        for i in self.fit_param.keys():
            eval("self." + self.fit_param[i]['array'] +".editingFinished").connect(self.be.store_fit)
        for i in clicked:
            i['wdg'].clicked.connect(i['func'])

        # Mirrored calls
        for i in self.mirror.keys():
            if self.mirror[i]['qt'] == 'QLineEdit':
                event = 'editingFinished'
            elif self.mirror[i]['qt'] == 'QButtonGroup':
                event = 'buttonClicked'
            elif self.mirror[i]['qt'] == 'QCheckBox':
                event = 'stateChanged'

            for j in self.mirror[i]['array']:
                eval("self." + j + "." + event).connect(self.be.store_data)
        # Other widgets calls
        for i in self.others.keys():
            if self.others[i]['qt'] == 'QLineEdit':
                event = 'editingFinished'
            elif self.others[i]['qt'] == 'QButtonGroup':
                event = 'buttonClicked'
            elif self.others[i]['qt'] == 'QCheckBox':
                event = 'stateChanged'
            eval("self." + self.others[i]['array'] + "." + event).connect(self.be.store_data)
        # Path edit calls
        for i in self.paths.keys():
            eval("self." + self.paths[i] + "." + 'editingFinished').connect(self.be.store_data)


    # Close Window event treatment
    def closeEvent(self, event):
        quit_msg = "¿Seguro que quiere salir del programa?"
        reply = QMessageBox.question(self, 'Cuidado!',
                         quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # MatplotLib Widgets
    def addmpl_1(self, fig):
        # Matplotlib constructor
        self.canvas1 = FigureCanvas(fig)
        self.mpl_1.addWidget(self.canvas1)
        self.canvas1.show()
        self.toolbar = NavigationToolbar(self.canvas1, self.frame_2,
                                         coordinates=True)
        self.mpl_1.addWidget(self.toolbar)
        self.sd.axes['ax0'] = fig.add_subplot(111)
        self.sd.axes['ax1'] = self.sd.axes['ax0'].twinx()
        self.sd.axes['ax0'].tick_params(axis="x", labelsize=8)
        self.sd.axes['ax0'].tick_params(axis="y", labelsize=8)
        self.sd.axes['ax1'].tick_params(axis="x", labelsize=8)
        self.sd.axes['ax1'].tick_params(axis="y", labelsize=8)
        # self.sd.axes['ax2'] = self.sd.axes['ax1'].twinx()


    def addmpl_2(self, fig):
        # Matplotlib constructor
        self.canvas2 = FigureCanvas(fig)
        self.mpl_2.addWidget(self.canvas2)
        self.canvas2.draw()
        self.toolbar = NavigationToolbar(self.canvas2, self.frame_3,
                                         coordinates=True)
        self.mpl_2.addWidget(self.toolbar)
        self.sd.axes['ax2'] = fig.add_subplot(111)
        self.sd.axes['ax3'] = self.sd.axes['ax2'].twinx()
        self.sd.axes['ax2'].tick_params(axis="x", labelsize=8)
        self.sd.axes['ax2'].tick_params(axis="y", labelsize=8)
        self.sd.axes['ax3'].tick_params(axis="x", labelsize=8)
        self.sd.axes['ax3'].tick_params(axis="y", labelsize=8)


    def addmpl_3(self, fig):
        # Matplotlib constructor
        self.canvas3 = FigureCanvas(fig)
        self.mpl_3.addWidget(self.canvas3)
        self.canvas3.draw()
        self.toolbar = NavigationToolbar(self.canvas3, self.frame_5,
                                         coordinates=True)
        self.mpl_3.addWidget(self.toolbar)
        self.sd.axes['ax4'] = fig.add_subplot(111)
        self.sd.axes['ax4'].tick_params(axis="x", labelsize=8)
        self.sd.axes['ax4'].tick_params(axis="y", labelsize=8)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    myappid = 'UPV.visa.4294A.1' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setWindowIcon(QtGui.QIcon('pollo.jpg'))

    data = DATA(read=True)
    window = MyApp(data)
    window.setWindowIcon(QtGui.QIcon('pollo.jpg'))
    window.addmpl_1(data.fig1)
    window.addmpl_2(data.fig2)
    window.addmpl_3(data.fig3)
    window.show()
    sys.exit(app.exec_())
