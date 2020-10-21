import json
import pyvisa as visa
import time
#import socket as sk
#from threading import Thread, Event
import os
import numpy as np
from PyQt5.QtWidgets import QMessageBox


BYE_MSG={'command':"BYE",'arg1':"",'arg2':""}


class VISA():
    def __init__(self,shared_data,txt_browser):
        self.uc = shared_data
        self.tb = txt_browser

        # Visa initializationg
        self.rm = visa.ResourceManager()
        self.lor = self.rm.list_resources()
        self.append_plus("Lista de dispositivos encontrados:")
        self.append_plus(str(self.lor))
        try:
            self.inst = self.rm.open_resource(self.uc.def_cfg['VI_ADDRESS'])
            self.append_plus("Conectados al equipo:")
            self.append_plus(str(self.inst.query("*IDN?")))

        except:
            self.append_plus("No encuentro el medidor 4294A")

        else:
            # Basic parameters
            self.inst.timeout = 120000
            # Self-test operation takes a long time [self.inst.query("*TST?")]
            self.inst.read_termination  = '\n'
            self.inst.write_termination = '\n'
            # Avoids reading/sending carriage return inside messages

            self.inst.write('HOLD')

    def append_plus(self,message):
        for text_browser in self.tb:
            text_browser.append(message)

    def switch(self,switcher,input):
        #Switch case function
         arg = switcher.get(input, "Error in Switch Operation")
         return arg

    def float_v(self,number):
        # Limit float precision
        try:
            return float("{0:.2f}".format(float(number)))
        except ValueError:
            return 0.0


    def config_measurement(self):

        #fprintf(handles.GPIBobj,'PAVER OFF'); % Desactivo el promediado. Añadido por mi.

        # Average of measurement points
        self.inst.write('PAVERFACT %s' % str(self.uc.def_cfg['n_medidas_punto']))
        # Activate average or not
        self.inst.write('PAVER %s' % self.switch({0:'OFF', 1:'ON'},self.uc.def_cfg['avg']))
        # Frequency sweep starting at ...
        self.inst.write('STAR %s' % str(self.uc.def_cfg['f_inicial']))
        # Frequency sweep stopping at ...
        self.inst.write('STOP %s' % str(self.uc.def_cfg['f_final']))
        # Tipo de barrido
        self.inst.write('SWPT %s' % self.switch({0:'LIN', 1:'LOG'},self.uc.def_cfg['tipo_barrido']))
        # Number of points
        self.inst.write('POIN %s' % str(self.uc.def_cfg['n_puntos']))
        # Bandwidth - resolución de la medida.
        self.inst.write('BWFACT %s' % str(self.uc.def_cfg['ancho_banda']))
        # Configura la tensión de salida del oscilador
        self.inst.write('POWMOD VOLT;POWE %s' % str(self.uc.def_cfg['vosc']))


        # DC_bias active
        if (self.uc.def_cfg['DC_bias']==0):
            # Tensión de polarización.
            self.inst.write('DCV %s' % str(self.uc.def_cfg['nivel_DC']))
            # Modo de BIAS
            self.inst.write('DCMOD CVOLT')
            # Rango de tensión de bias.
            self.inst.write('DCRNG M1')
            # Borrar errores
            self.inst.write('*CLS')
            # Activo la tensión de bias.
            self.inst.write('DCO ON')
            # Solicito el último error que se ha producido
            error = self.inst.query('OUTPERRO?')
            error_code = int(error[0:error.find(',')])
            if (error_code==0):
                flag_dcrange = 1
            elif (error_code==137):
                self.inst.write('DCRNG M10')
                self.inst.write('*CLS')
                self.inst.write('DCO ON')
                error = self.inst.query('OUTPERRO?')
                error_code = int(error[0:error.find(',')])
                if (error_code==0):
                    flag_dcrange = 10
                elif (error_code==137):
                    self.inst.write('DCRNG M100')
                    self.inst.write('*CLS')
                    self.inst.write('DCO ON')
                    error = self.inst.query('OUTPERRO?')
                    error_code = int(error[0:error.find(',')])
                    if (error_code==0):
                        flag_dcrange = 100
                    elif (error_code==137):
                        # ERROR: BIAS Voltage too high
                        self.append_plus("Módulo de BIAS demasiado elevado. Redúzcala o Desactívela")
                        self.append_plus("ERROR %s" % str(error_code))
                    else:
                        self.append_plus("Reconsidere usar la tensión de BIAS")
                        self.append_plus("ERROR %s" % str(error_code))
                else:
                    self.append_plus("Reconsidere usar la tensión de BIAS")
                    self.append_plus("ERROR %s" % str(error_code))
            else:
                self.append_plus("Reconsidere usar la tensión de BIAS")
                self.append_plus("ERROR %s" % str(error_code))

        # No BIAS voltage
        else:
            self.inst.write('DCRNG M1') # Default range
            self.inst.write('DCO OFF')


    def measure(self):
        self.append_plus("Midiendo Z=R+iX")

        # Service Request instead of using pulling
        event_type = visa.constants.EventType.service_request
        # Mechanism by which we want to be notified
        event_mech = visa.constants.EventMechanism.queue

        self.inst.write('TRGS INT')          # Internal Trigger Source
        self.inst.write('ESNB 1')            # Event_Status_Register[0]=1 // Enables Sweep Completion bit
        self.inst.write('*SRE 4')            # Service Request Enable = 1
        self.inst.write('*CLS')              # Clears Error queue


        self.inst.write('MEAS IRIM')         # Medida de R y X
        self.inst.write('HIDI OFF')          # Muestras la traza inactiva
        self.inst.write('SING')              # Iniciar un barrido único.

        self.append_plus("ACK Instrumento = %s" % self.inst.query('*OPC?'))

        # self.inst.enable_event(event_type, event_mech)
        #
        # #self.append_plus(self.inst.query('*OPC?'))
        # # Wait for the event to occur
        # response = self.inst.wait_on_event(event_type, 10000)
        #
        # #if (response.event.event_type == event_type):
        #     # response.timed_out = False
        # self.inst.disable_event(event_type, event_mech)
        # response.timed_out = False

        # Recover Measured Data
        self.inst.write('TRAC A')           # Selecciona traza A
        self.inst.write('AUTO')             # Autoescala
        aux_R = np.fromstring(self.inst.query('OUTPDTRC?'), dtype=float, sep=',')

        self.inst.write('TRAC B')           # Selecciona traza A
        self.inst.write('AUTO')             # Autoescala
        aux_X = np.fromstring(self.inst.query('OUTPDTRC?'), dtype=float, sep=',')

        self.uc.R_data = aux_R[0::2]
        self.uc.X_data = aux_X[0::2]

        # Compute Err, Eri, Er_mod, Er_fase_data
        # First create frequency array based on actual gui conditions
        # The freq array will not be changed until next data acquisition even if GUI changes
        if (self.uc.def_cfg['tipo_barrido']==0):
            self.uc.freq = np.linspace(self.uc.def_cfg['f_inicial'],
                                       self.uc.def_cfg['f_final'],
                                       self.uc.def_cfg['n_puntos'])
        elif(self.uc.def_cfg['tipo_barrido']==1):
            self.uc.freq = np.logspace(np.log10(self.uc.def_cfg['f_inicial']),
                                       np.log10(self.uc.def_cfg['f_final']),
                                       self.uc.def_cfg['n_puntos'])

        complex_aux         = self.uc.R_data + self.uc.X_data*1j
        self.uc.Z_mod_data  = np.abs(complex_aux)
        self.uc.Z_fase_data = np.angle(complex_aux)

        admitance_aux       = 1./complex_aux
        G_data              = np.real(admitance_aux)
        Cp_data             = np.imag(admitance_aux)/(2*np.pi*self.uc.freq)
        self.uc.Err_data    = Cp_data/self.uc.Co
        self.uc.Eri_data    = G_data/(self.uc.Co*(2*np.pi*self.uc.freq));
        E_data              = self.uc.Err_data + -1*self.uc.Eri_data*1j;

        self.uc.Er_mod_data  = np.abs(E_data);
        self.uc.Er_fase_data = np.angle(E_data);

        # Deactivate BIAS for security reasons
        self.inst.write('DCO OFF')
        self.inst.write('DCRNG M1')

        print("MEDIDA REALIZADA")


    def show_measurement(self,comboBox_trazaA,comboBox_trazaB):
        self.uc.axes['ax0'].cla()
        self.uc.axes['ax1'].cla()

        traza_A = self.switch({ 0:self.uc.Z_mod_data,
                                1:self.uc.Z_fase_data,
                                2:self.uc.Err_data,
                                3:self.uc.Eri_data,
                                4:self.uc.Er_mod_data,
                                5:self.uc.Er_fase_data}, comboBox_trazaA)

        traza_B = self.switch({ 0:self.uc.Z_mod_data,
                                1:self.uc.Z_fase_data,
                                2:self.uc.Err_data,
                                3:self.uc.Eri_data,
                                4:self.uc.Er_mod_data,
                                5:self.uc.Er_fase_data}, comboBox_trazaB)

        if (self.uc.def_cfg['tipo_barrido']==0):
            self.uc.axes['ax0'].plot(self.uc.freq, traza_A, color='red')
            self.uc.axes['ax0'].tick_params(axis='y', colors='red')
            self.uc.axes['ax1'].plot(self.uc.freq, traza_B, color='blue')
            self.uc.axes['ax1'].grid(True)
            self.uc.axes['ax1'].tick_params(axis='y',colors='blue')

        elif(self.uc.def_cfg['tipo_barrido']==1):
            self.uc.axes['ax0'].semilogx(self.uc.freq, traza_A, color='red')
            self.uc.axes['ax0'].tick_params(axis='y',colors='red')
            self.uc.axes['ax1'].semilogx(self.uc.freq, traza_B, color='blue')
            self.uc.axes['ax1'].grid(True)
            self.uc.axes['ax1'].tick_params(axis='y', colors='blue')

        self.uc.fig1.tight_layout()


    def show_data(self, comboBox_trazaA, comboBox_trazaB, data):

        self.uc.axes['ax2'].cla()
        self.uc.axes['ax3'].cla()

        traza_A = self.switch({ 0:data['Z_mod'],
                                1:data['Z_Fase'],
                                2:data['Err'],
                                3:data['Eri'],
                                4:data['E_mod'],
                                5:data['E_fase']},
                                comboBox_trazaA)

        traza_B = self.switch({ 0:data['Z_mod'],
                                1:data['Z_Fase'],
                                2:data['Err'],
                                3:data['Eri'],
                                4:data['E_mod'],
                                5:data['E_fase']},
                                comboBox_trazaB)

        if (self.uc.def_cfg['tipo_barrido']==0):
            self.uc.axes['ax2'].plot(data['Freq'], traza_A, color='red')
            self.uc.axes['ax2'].tick_params(axis='y', colors='red')
            self.uc.axes['ax3'].plot(data['Freq'], traza_B, color='blue')
            self.uc.axes['ax3'].grid(True)
            self.uc.axes['ax3'].tick_params(axis='y',colors='blue')

        elif(self.uc.def_cfg['tipo_barrido']==1):
            self.uc.axes['ax2'].semilogx(data['Freq'], traza_A, color='red')
            self.uc.axes['ax2'].tick_params(axis='y',colors='red')
            self.uc.axes['ax3'].semilogx(data['Freq'], traza_B, color='blue')
            self.uc.axes['ax3'].grid(True)
            self.uc.axes['ax3'].tick_params(axis='y', colors='blue')

        self.uc.fig2.tight_layout()


    def config_calibration(self):
        # Configuración de los valores para la calibración en abierto, corto y carga
        # Calibración MEDIDOR/USUARIO
        # COMMON PARAMETERS
        # Configure calibration/measurement process
        self.inst.write('CALP %s' % self.switch({0:'FIXED', 1:'USER'},self.uc.def_cfg['conf_cal']))
        # Average of measurement points
        self.inst.write('PAVERFACT %s' % str(self.uc.def_cfg['n_medidas_punto']))
        # Activate average or not
        self.inst.write('PAVER %s' % self.switch({0:'OFF', 1:'ON'},self.uc.def_cfg['avg']))
        # Frequency sweep starting at ...
        self.inst.write('STAR %s' % str(self.uc.def_cfg['f_inicial']))
        # Frequency sweep stopping at ...
        self.inst.write('STOP %s' % str(self.uc.def_cfg['f_final']))
        # Tipo de barrido
        self.inst.write('SWPT %s' % self.switch({0:'LIN', 1:'LOG'},self.uc.def_cfg['tipo_barrido']))
        # Number of points
        self.inst.write('POIN %s' % str(self.uc.def_cfg['n_puntos']))
        # Bandwidth - resolución de la medida.
        self.inst.write('BWFACT %s' % str(self.uc.def_cfg['ancho_banda']))
        # Configura la tensión de salida del oscilador
        self.inst.write('POWMOD VOLT;POWE %s' % str(self.uc.def_cfg['vosc']))

        # Desativo bias
        self.inst.write('DCO OFF')
        # Fijo rango de tensión de bias
        self.inst.write('DCRNG M1')

        # % ************** IMPORTANTE ***********************************
        # % * Los valores de la calibración en abierto serán usados para la
        # % * calibración en carga y los valores de la caligración en carga serán
        # % * usados para la calibración en abierto.
        # % ***************************************************************

        # Conductancia esparada en la calibración en abierto
        self.inst.write('DCOMOPENG %s' % str(self.uc.def_cfg['g_load']))
        # Capacidad esparada en la calibración en abierto (fF)
        self.inst.write('DCOMOPENC %s' % str(self.uc.def_cfg['c_load']))

        # Resistencia esperada calibración corto
        self.inst.write('DCOMSHORR %s' % str(self.uc.Short_r))
        # Inductancia esperada calibración corto
        self.inst.write('DCOMSHORL %s' % str(self.uc.Short_l))
        # Resistencia esperada calibración en carga
        self.inst.write('DCOMLOADR %s' % str(self.uc.Open_r))
        # Inductancia esperada calibración en carga
        self.inst.write('DCOMLOADL %s' % str(self.uc.Open_l))


    def cal_load_open_short(self):
        # Proceos de la calibración en carga, para ello como se indica se
        # realiza una calibración en abierto con la configuración realizada con
        # los comandos anteriores.

        ############## CARGA
        self.message_box("Calibración con CARGA",
                         "Introduzca la carga indicada y pulsa ACEPTAR")
        self.append_plus("Realizando calibración por carga")

        error_code = self.AdapterCorrection('Compen_Open')
        if error_code==0:
            self.append_plus("Calibración por CARGA realizada correctamente")
        else:
            self.append_plus("Error %s en calibración por carga" % error_code)

        ############## ABIERTO
        self.message_box("Calibración en ABIERTO",
                         "Configure el sensor para calibración en ABIERTO y pulsa ACEPTAR")
        self.append_plus("Realizando calibración en ABIERTO")

        error_code = self.AdapterCorrection('Compen_Load')
        if error_code==0:
            self.append_plus("Calibración en ABIERTO realizada correctamente")
        else:
            self.append_plus("Error %s en calibración en ABIERTO" % error_code)

        ############## CORTO
        self.message_box("Calibración en CORTO",
                         "Configure el sensor para calibración en CORTO y pulsa ACEPTAR")
        self.append_plus("Realizando calibración en CORTO")

        error_code = self.AdapterCorrection('Compen_Short')
        if error_code==0:
            self.append_plus("Calibración en CORTO realizada correctamente")
        else:
            self.append_plus("Error %s en calibración en CORTO" % error_code)

    def cal_open_short(self):
        # Proceos de la calibración en carga, para ello como se indica se
        # realiza una calibración en abierto con la configuración realizada con
        # los comandos anteriores.

        ############## ABIERTO
        self.message_box("Calibración en ABIERTO",
                         "Configure el sensor para calibración en ABIERTO y pulsa ACEPTAR")
        self.append_plus("Realizando calibración en ABIERTO")

        error_code = self.AdapterCorrection('Compen_Open')
        if error_code==0:
            self.append_plus("Calibración en ABIERTO realizada correctamente")
        else:
            self.append_plus("Error %s en calibración en ABIERTO" % error_code)

        ############## CORTO
        self.message_box("Calibración en CORTO",
                         "Configure el sensor para calibración en CORTO y pulsa ACEPTAR")
        self.append_plus("Realizando calibración en CORTO")

        error_code = self.AdapterCorrection('Compen_Short')
        if error_code==0:
            self.append_plus("Calibración en CORTO realizada correctamente")
        else:
            self.append_plus("Error %s en calibración en CORTO" % error_code)



    def message_box(self,title,text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        # msg.setInformativeText(text)
        msg.setWindowTitle(title)
        #msg.setDetailedText("")
        retval = msg.exec_()


    def AdapterCorrection(self, type):
        # Activo el bit 8 del instrument event status register
        # Que se activará cuando se finalice una calibración o compensación
        self.inst.write('ESNB 256')
        # Activo el bit 2 del Status Byte Register, el denomindo bit Instrument
        # Event Status Register Summary. Este indica que se active la linea SRQ
        # del bus GPIB cuando se produzca el evento programando en el Instrument
        # Event Status Register
        self.inst.write('*SRE 4')
        # Clear de los registros
        self.inst.write('*CLS')
        # Se aplica la compensación según el tipo de calibración
        self.inst.write(self.switch({'Adapter_Phase':'ECALP',
                                   'Compen_Open':'COMA',
                                   'Compen_Short':'COMB',
                                   'Compen_Load':'COMC'}
                                   ,type))
        # Espera hasta que se produce un SRQ en el instrumento indicado con GPIBobj
        # En este caso la linea SRQ se activa cuando se ha finalizado la
        # compensación (timeout 120seg)
        self.inst.wait_for_srq(120000)

        # Pregunto poe el último error
        error = self.inst.query('OUTPERRO?')
        error_code = int(error[0:error.find(',')])

        if error_code == 0:
            self.append_plus("Calibración %s correcta" % type)
        else:
            self.append_plus("Error en Calibración %s" % type)

        return error_code
