import pyvisa
import time
import sys
import json
import numpy as np
import pandas as pd
import MIOPATIA_visa as mv
from PyQt5 import QtCore, QtWidgets, uic
from threading import Thread, Event, RLock

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMessageBox

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
        # Axes for plotting
        self.axes={'ax0':0,'ax1':0,'ax2':0,'ax3':0}

        if (read==True):
            self.config_read()
        else:
            # These are the default values.
            self.def_cfg= {'f_inicial':10,
                            'f_final':10000000,
                            'n_puntos':10,
                            'ancho_banda':2,
                            'vosc':0.5,
                            'tipo_barrido':0,
                            'DC_bias':0,
                            'nivel_DC':0,
                            'avg':0,
                            'n_medidas_punto':0,
                            'load_mfile_name':"./medida.csv",
                            'save_mfile_name':"./medida.csv",
                            'cal_file_name':"./calibracion.cal",
                            'def_path':"./",
                            'conf_cal':0,
                            'c_load':500,
                            'g_load':0.1,
                            'pto_cal':0,
                            'combox':['|Z|','F.Z','E\'r','E\'\'r','|Er|','F.Er'],
                            'VI_ADDRESS': 'GPIB0::17::INSTR'
                            }
        self.config_write()

        # FLAGS
        self.measuring = False

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

        self.Co              = 1E-12   # Valor capacidad en abierto sensor de puntas


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

     # Controlled casting to avoid data intro errors
    def float_v(self,objeto,limits=[0,1E12]):
        try:
            aux = float(objeto.text())
            print(aux)
            if ((aux >= limits[0]) and (aux <= limits[1])):
                return float(aux)
            else:
                if (aux > limits[1]):
                    objeto.setText(str(limits[1]))
                    return float(limits[1])
                else:
                    if (aux < limits[0]):
                        objeto.setText(str(limits[0]))
                        return float(limits[0])
        except ValueError:
            self.pw.textBrowser.append("ERROR EN VALOR")
            objeto.setText(str(limits[0]))
            return limits[0]

    def int_v(self,objeto,limits=[0,1E12]):
        try:
            aux = int(objeto.text())
            if ((aux >= limits[0]) and (aux <= limits[1])):
                return int(aux)
            else:
                if (aux > limits[1]):
                    objeto.setText(str(limits[1]))
                    return int(limits[1])
                else:
                    if (aux < limits[0]):
                        objeto.setText(str(limits[0]))
                        return int(limits[0])
        except ValueError:
            self.pw.textBrowser.append("ERROR EN VALOR")
            objeto.setText(str(limits[0]))
            return limits[0]

    def save_config(self):
        self.sd.config_write()

    def continuar(self):
        # self.pw.textBrowser.append("CONTINUAR")
        if (len(self.sd.freq))>0:
            self.vi.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                     self.pw.comboBox_trazaB.currentIndex())
        else:
            self.pw.textBrowser.append("NO HAY DATOS QUE MOSTRAR")
        self.pw.canvas1.draw()

    def medir(self):
        self.pw.MEDIR.setEnabled(False)
        app.processEvents()
        self.pw.textBrowser.append("MEDIR")
        self.vi.config_measurement()
        self.vi.measure()
        self.vi.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                 self.pw.comboBox_trazaB.currentIndex())
        self.pw.canvas1.draw()
        self.pw.MEDIR.setEnabled(True)

    def load_m(self):
        self.pw.textBrowser.append("CARGA MEDIDA")
        file = self.sd.def_cfg['load_mfile_name']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','Z_mod','Z_Fase', 'Err',
                                    'Eri','E_mod','E_fase','R','X'],
                            delim_whitespace=True)
        except:
            self.pw.textBrowser.append("Fichero no encontrado\n")
        else:
            self.pw.textBrowser.append(file)
            self.vi.show_data(self.pw.comboBox_trazaA.currentIndex(),
                              self.pw.comboBox_trazaB.currentIndex(),
                              data)
            self.pw.canvas2.draw()


    def save_m(self):
        def justify(input_str,n_char):
            string = input_str+''.join([' ']*(n_char-len(input_str)))
            return string.strip('"')

        self.pw.textBrowser.append("SALVA MEDIDA")
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
            self.pw.textBrowser.append("El fichero de datos no se ha podido salvar\n")
        else:
            self.pw.textBrowser.append(file_save)


    def go_cal(self):
        self.pw.textBrowser.append("CALIBRAR")

    def load_cal(self):
        self.pw.textBrowser.append("CARGAR CALIBRACIÓN")

    def save_cal(self):
        self.pw.textBrowser.append("SALVAR CALIBRACIÓN")

    def store_data(self):
        self.sd.def_cfg['f_inicial']=self.int_v(self.pw.f_inicial,[40,110E6])
        self.sd.def_cfg['f_final']=self.int_v(self.pw.f_final,[40,110E6])
        self.sd.def_cfg['n_puntos']=self.int_v(self.pw.n_puntos,[1,801])
        self.sd.def_cfg['ancho_banda']=self.int_v(self.pw.ancho_banda,[1,5])
        self.sd.def_cfg['vosc']=self.float_v(self.pw.vosc,[0.0,1.0])
        self.sd.def_cfg['nivel_DC']=self.float_v(self.pw.nivel_DC,[-40.0,40.0])
        self.sd.def_cfg['n_medidas_punto']=self.int_v(self.pw.n_medidas_punto,[1,256])
        self.sd.def_cfg['load_mfile_name']=self.pw.load_path.text()
        self.sd.def_cfg['save_mfile_name']=self.pw.save_path.text()
        self.sd.def_cfg['save_mfile_name']=self.pw.save_path.text()
        self.sd.def_cfg['c_load']=self.float_v(self.pw.c_load)
        self.sd.def_cfg['g_load']=self.float_v(self.pw.g_load)
        self.sd.def_cfg['cal_file_name']=self.pw.load_path_2.text()

        print(self.sd.def_cfg)

    # Button groups send id when clicked, then a function per button group is created
    def bt_xaxis(self,id):
        self.sd.def_cfg['tipo_barrido']=id
    def bt_DC(self,id):
        self.sd.def_cfg['DC_bias']=id
    def bt_avg(self,id):
        self.sd.def_cfg['avg']=id
    def bt_config_cal(self,id):
        self.sd.def_cfg['conf_cal']=id
    def bt_pto_cal(self,id):
        self.sd.def_cfg['pto_cal']=id


class BROWSERS(object):
    """ File Browsers for config files, input and output files etc.
    """
    def __init__(self,parent_wdg,shared_data):
        self.sd = shared_data
        self.parent_wdg = parent_wdg

    def load_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.parent_wdg,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.parent_wdg.load_path.setText(self.sd.def_cfg['load_mfile_name'])


    def save_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.parent_wdg,
                                        'Salvar fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.parent_wdg.save_path.setText(self.sd.def_cfg['save_mfile_name'])


    def calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.parent_wdg,
                                        'Fichero de calibración',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.cal)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['cal_file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.parent_wdg.load_path_2.setText(self.sd.def_cfg['cal_file_name'])



class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self,data):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Shared data
        self.data = data

        # Classes Instantiation
        self.browsers = BROWSERS(self,data)
        # VISA start
        self.v_s = mv.VISA(self.data,self.textBrowser)
        self.backend  = BACK_END(self,data,self.v_s)



        # Controls Defaults
        self.f_inicial.setText(str(self.data.def_cfg['f_inicial']))
        self.f_final.setText(str(self.data.def_cfg['f_final']))
        self.n_puntos.setText(str(self.data.def_cfg['n_puntos']))
        self.vosc.setText(str(self.data.def_cfg['vosc']))
        self.ancho_banda.setText(str(self.data.def_cfg['ancho_banda']))
        self.nivel_DC.setText(str(self.data.def_cfg['nivel_DC']))
        self.n_medidas_punto.setText(str(self.data.def_cfg['n_medidas_punto']))
        self.load_path.setText(str(self.data.def_cfg['load_mfile_name']))
        self.save_path.setText(str(self.data.def_cfg['save_mfile_name']))
        self.load_path_2.setText(str(self.data.def_cfg['cal_file_name']))
        self.c_load.setText(str(self.data.def_cfg['c_load']))
        self.g_load.setText(str(self.data.def_cfg['g_load']))

        self.comboBox_trazaA.addItems(self.data.def_cfg['combox'])
        self.comboBox_trazaB.addItems(self.data.def_cfg['combox'])

        # Radio Buttons groups creation
        self.bg_xaxis = QtWidgets.QButtonGroup()
        self.radioButton_xaxis=[self.radioButton_lineal, self.radioButton_log]
        j=0
        for i in self.radioButton_xaxis:
            self.bg_xaxis.addButton(i)
            self.bg_xaxis.setId(i,j)
            j+=1
        j=0
        self.bg_DC = QtWidgets.QButtonGroup()
        self.radioButton_DC   =[self.radioButton_DC_ON, self.radioButton_DC_OFF]
        for i in self.radioButton_DC:
            self.bg_DC.addButton(i)
            self.bg_DC.setId(i,j)
            j+=1
        j=0
        self.bg_avg = QtWidgets.QButtonGroup()
        self.radioButton_avg  =[self.radioButton_avg_SI, self.radioButton_avg_NO]
        for i in self.radioButton_avg:
            self.bg_avg.addButton(i)
            self.bg_avg.setId(i,j)
            j+=1
        j=0
        self.bg_config_cal = QtWidgets.QButtonGroup()
        self.radioButton_config_cal=[self.radioButton_config_cal_1,
                                self.radioButton_config_cal_2]
        for i in self.radioButton_config_cal:
            self.bg_config_cal.addButton(i)
            self.bg_config_cal.setId(i,j)
            j+=1
        j=0
        self.bg_pto_cal = QtWidgets.QButtonGroup()
        self.radioButton_pto_cal=[self.radioButton_pto_cal_medidor,
                             self.radioButton_pto_cal_usuario]
        for i in self.radioButton_pto_cal:
            self.bg_pto_cal.addButton(i)
            self.bg_pto_cal.setId(i,j)
            j+=1

        # Radio Buttons
        self.radioButton_xaxis[self.data.def_cfg['tipo_barrido']].setChecked(True)
        self.radioButton_DC[self.data.def_cfg['DC_bias']].setChecked(True)
        self.radioButton_avg[self.data.def_cfg['avg']].setChecked(True)
        self.radioButton_config_cal[self.data.def_cfg['conf_cal']].setChecked(True)
        self.radioButton_pto_cal[self.data.def_cfg['pto_cal']].setChecked(True)

        # Clicked Calls
        self.toolButton_load.clicked.connect(self.browsers.load_mfile_browser)
        self.toolButton_save.clicked.connect(self.browsers.save_mfile_browser)
        self.toolButton_load_2.clicked.connect(self.browsers.calibration_file_browser)
        self.CONTINUAR.clicked.connect(self.backend.continuar)
        self.MEDIR.clicked.connect(self.backend.medir)
        self.LOAD_M.clicked.connect(self.backend.load_m)
        self.SAVE_M.clicked.connect(self.backend.save_m)
        self.GO_CAL.clicked.connect(self.backend.go_cal)
        self.LOAD_CAL.clicked.connect(self.backend.load_cal)
        self.SAVE_CAL.clicked.connect(self.backend.save_cal)
        self.SAVE_cfg.clicked.connect(self.backend.save_config)

        # Controls Signals
        self.f_inicial.editingFinished.connect(self.backend.store_data)
        self.f_final.editingFinished.connect(self.backend.store_data)
        self.n_puntos.editingFinished.connect(self.backend.store_data)
        self.ancho_banda.editingFinished.connect(self.backend.store_data)
        self.vosc.editingFinished.connect(self.backend.store_data)
        self.nivel_DC.editingFinished.connect(self.backend.store_data)
        self.n_medidas_punto.editingFinished.connect(self.backend.store_data)
        self.load_path.textChanged.connect(self.backend.store_data)
        self.save_path.textChanged.connect(self.backend.store_data)
        self.load_path_2.textChanged.connect(self.backend.store_data)
        self.c_load.editingFinished.connect(self.backend.store_data)
        self.g_load.editingFinished.connect(self.backend.store_data)
        self.bg_xaxis.buttonClicked[int].connect(self.backend.bt_xaxis)
        self.bg_DC.buttonClicked[int].connect(self.backend.bt_DC)
        self.bg_avg.buttonClicked[int].connect(self.backend.bt_avg)
        self.bg_config_cal.buttonClicked[int].connect(self.backend.bt_config_cal)
        self.bg_pto_cal.buttonClicked[int].connect(self.backend.bt_pto_cal)


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
        self.data.axes['ax0'] = fig.add_subplot(111)
        self.data.axes['ax1'] = self.data.axes['ax0'].twinx()
        self.data.axes['ax0'].tick_params(axis="x", labelsize=8)
        self.data.axes['ax0'].tick_params(axis="y", labelsize=8)
        self.data.axes['ax1'].tick_params(axis="x", labelsize=8)
        self.data.axes['ax1'].tick_params(axis="y", labelsize=8)
        # self.data.axes['ax2'] = self.data.axes['ax1'].twinx()


    def addmpl_2(self, fig):
        # Matplotlib constructor
        self.canvas2 = FigureCanvas(fig)
        self.mpl_2.addWidget(self.canvas2)
        self.canvas2.draw()
        self.toolbar = NavigationToolbar(self.canvas2, self.frame_3,
                                         coordinates=True)
        self.mpl_2.addWidget(self.toolbar)
        self.data.axes['ax2'] = fig.add_subplot(111)
        self.data.axes['ax3'] = self.data.axes['ax2'].twinx()
        self.data.axes['ax2'].tick_params(axis="x", labelsize=8)
        self.data.axes['ax2'].tick_params(axis="y", labelsize=8)
        self.data.axes['ax3'].tick_params(axis="x", labelsize=8)
        self.data.axes['ax3'].tick_params(axis="y", labelsize=8)




if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    data = DATA(read=True)
    window = MyApp(data)
    window.addmpl_1(data.fig1)
    window.addmpl_2(data.fig2)
    window.show()
    sys.exit(app.exec_())
