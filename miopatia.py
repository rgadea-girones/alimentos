import pyvisa
import time
import sys
import json
import numpy as np
import pandas as pd
import MIOPATIA_visa as MP_visa
from PyQt5 import QtCore, QtWidgets, uic
from threading import Thread, Event, RLock

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

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
        self.axes={'ax1':0,'ax2':0}

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
                            'VI_ADDRESS': 'USB0::1510::8752::9030149::0::INSTR'
                            }
        self.config_write()

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
    def __init__(self,parent_wdg,shared_data):
        self.sd = shared_data
        self.pw = parent_wdg

     # Controlled casting to avoid data intro errors
    def float_v(self,number):
        try:
            return float(number)
        except ValueError:
            return 0.0

    def int_v(self,number):
        try:
            return int(number)
        except ValueError:
            return 0

    def continuar(self):
        print("CONTINUAR")

    def medir(self):
        print("MEDIR")

    def load_m(self):
        print("CARGA MEDIDA")
        data = pd.read_csv("pechuga_con_piel.csv",header=0,
                           names=['Freq','Z_mod','Z_Fase', 'Err','Eri','E_mod','E_fase','R','X'],
                           delim_whitespace=True)
        x_axis = np.array(data['Freq'])
        self.sd.axes['ax1'].semilogx(x_axis,data['Z_mod'])
        self.sd.axes['ax1'].grid(True)
        self.pw.canvas1.draw()


    def save_m(self):
        print("SALVA MEDIDA")

    def go_cal(self):
        print("CALIBRAR")

    def load_cal(self):
        print("CARGAR CALIBRACIÓN")

    def save_cal(self):
        print("SALVAR CALIBRACIÓN")

    def store_data(self):
        self.sd.def_cfg['f_inicial']=self.int_v(self.pw.f_inicial.text())
        self.sd.def_cfg['f_final']=self.int_v(self.pw.f_final.text())
        self.sd.def_cfg['n_puntos']=self.int_v(self.pw.n_puntos.text())
        self.sd.def_cfg['ancho_banda']=self.float_v(self.pw.ancho_banda.text())
        self.sd.def_cfg['vosc']=self.float_v(self.pw.vosc.text())
        self.sd.def_cfg['nivel_DC']=self.float_v(self.pw.nivel_DC.text())
        self.sd.def_cfg['n_medidas_punto']=self.float_v(self.pw.n_medidas_punto.text())
        self.sd.def_cfg['load_mfile_name']=self.pw.load_path.text()
        self.sd.def_cfg['save_mfile_name']=self.pw.save_path.text()
        self.sd.def_cfg['save_mfile_name']=self.pw.save_path.text()
        self.sd.def_cfg['c_load']=self.float_v(self.pw.c_load.text())
        self.sd.def_cfg['g_load']=self.float_v(self.pw.g_load.text())
        self.sd.def_cfg['cal_file_name']=self.pw.load_path_2.text()

        print(self.sd.def_cfg)

    # Button groups send id when clicked, then a function per button group is created
    def bt_xaxis(self,id):
        self.sd.def_cfg['tipo_barrido']=id
        print(id)
    def bt_DC(self,id):
        self.sd.def_cfg['DC_bias']=id
        print(id)
    def bt_avg(self,id):
        self.sd.def_cfg['avg']=id
        print(id)
    def bt_config_cal(self,id):
        self.sd.def_cfg['conf_cal']=id
        print(id)
    def bt_pto_cal(self,id):
        self.sd.def_cfg['pto_cal']=id
        print(id)


class BROWSERS(object):
    """ File Browsers for config files, input and output files etc.
    """
    def __init__(self,parent_wdg,shared_data):
        self.sd = shared_data
        self.parent_wdg = parent_wdg

    def load_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.parent_wdg,
                                        'Open measurement file',
                                        self.sd.def_cfg['def_path'],
                                        "Measurement files (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.parent_wdg.load_path.setText(self.sd.def_cfg['load_mfile_name'])


    def save_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.parent_wdg,
                                        'Save measurement file',
                                        self.sd.def_cfg['def_path'],
                                        "Measurement files (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.parent_wdg.save_path.setText(self.sd.def_cfg['save_mfile_name'])


    def calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.parent_wdg,
                                        'Calibration file',
                                        self.sd.def_cfg['def_path'],
                                        "Calibration files (*.cal)")
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
        self.backend  = BACK_END(self,data)

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

        # Controls Calls
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


    # MatplotLib Widgets
    def addmpl_1(self, fig):
        # Matplotlib constructor
        self.canvas1 = FigureCanvas(fig)
        self.mpl_1.addWidget(self.canvas1)
        self.canvas1.show()
        self.toolbar = NavigationToolbar(self.canvas1, self.frame_2,
                                         coordinates=True)
        self.mpl_1.addWidget(self.toolbar)
        self.data.axes['ax1'] = fig.add_subplot(111)
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


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    data = DATA(read=False)
    window = MyApp(data)
    window.addmpl_1(data.fig1)
    window.addmpl_2(data.fig2)
    window.show()
    sys.exit(app.exec_())
