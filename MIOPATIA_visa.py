import json
import pyvisa as visa
import time
#import socket as sk
#from threading import Thread, Event
import os
import numpy as np

BYE_MSG={'command':"BYE",'arg1':"",'arg2':""}


class VISA():
    def __init__(self,shared_data,txt_browser):
        self.uc = shared_data
        self.tb = txt_browser

        # Visa initializationg
        self.rm = visa.ResourceManager()
        self.lor = self.rm.list_resources()
        self.tb.append("Lista de dispositivos encontrados:")
        self.tb.append(str(self.lor))
        try:
            self.inst = self.rm.open_resource(self.uc.def_cfg['VI_ADDRESS'])
            self.tb.append("Conectados al equipo:")
            self.tb.append(str(self.inst.query("*IDN?")))

        except:
            self.tb.append("No encuentro el medidor 4294A")

        else:
            # Basic parameters
            self.inst.timeout = 120000
            # Self-test operation takes a long time [self.inst.query("*TST?")]
            self.inst.read_termination  = '\n'
            self.inst.write_termination = '\n'
            # Avoids reading/sending carriage return inside messages

            self.inst.write('HOLD')

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
        # Calibración MEDIDOR/USUARIO
        # COMMON PARAMETERS
        # Configure calibration/measurement process
        self.inst.write('CALP %s' % self.switch({0:'FIXED', 1:'USER'},self.uc.def_cfg['conf_cal']))
        #fprintf(handles.GPIBobj,'PAVER OFF'); % Desactivo el promediado. Añadido por mi.

        # Average of measurement points
        self.inst.write('PAVERFACT %s' % str(self.uc.def_cfg['n_medidas_punto']))
        # Activate average or not
        self.inst.write('PAVER %s' % self.switch({0:'ON', 1:'OFF'},self.uc.def_cfg['avg']))
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
                        self.tb.append("Módulo de BIAS demasiado elevado. Redúzcala o Desactívela")
                        self.tb.append("ERROR %s" % str(error_code))
                    else:
                        self.tb.append("Reconsidere usar la tensión de BIAS")
                        self.tb.append("ERROR %s" % str(error_code))
                else:
                    self.tb.append("Reconsidere usar la tensión de BIAS")
                    self.tb.append("ERROR %s" % str(error_code))
            else:
                self.tb.append("Reconsidere usar la tensión de BIAS")
                self.tb.append("ERROR %s" % str(error_code))

        # No BIAS voltage
        else:
            self.inst.write('DCRNG M1') # Default range
            self.inst.write('DCO OFF')


    def measure(self):
        self.tb.append("Midiendo Z=R+iX")

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

        self.tb.append(self.inst.query('*OPC?'))

        # self.inst.enable_event(event_type, event_mech)
        #
        # #self.tb.append(self.inst.query('*OPC?'))
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
