import sys
import redpitaya_scpi as scpi
import numpy as np
from time import perf_counter as pc
from time import sleep
from scipy.fft import fft, fftfreq, fftshift
import matplotlib.pyplot as plt
from plumbum import SshMachine
from plumbum.machines.paramiko_machine import ParamikoMachine


t0=pc()
rp_s = scpi.scpi(sys.argv[1])

# superparametros
wave_form = 'sine'
frecuencia_min = 1
frecuencia_max=6
puntos_decada=10


numero_valores=(frecuencia_max-frecuencia_min)*puntos_decada
#frecuencias =np.geomspace(frecuencia_min,frecuencia_max,numero_valores)
frecuencias_TOTAL =np.logspace(frecuencia_min,frecuencia_max,256,base=10)

frecuencias=frecuencias_TOTAL[frecuencias_TOTAL>40]

fm=125000000
numero_pulsos=10
ciclos=5
ampl = 1

amplreference=np.linspace(10,1,numero_valores)
ampl2=1/amplreference
phases=np.linspace(180,0,numero_valores)
#decimation=np.logspace(numero_valores-1, 0, num=numero_valores, base=2.0)
#decimation=30*[1024]+30*[64]+40*[1]
decimation=1*puntos_decada*[8192]+2*puntos_decada*[1024]+1*puntos_decada*[64]+2*puntos_decada*[1]




# rp_s.tx_txt('SOUR1:BURS:NOR 2') # Set 2 repeticiones


# there is an option to select coupling when using SIGNALlab 250-12
# rp_s.tx_txt('ACQ:SOUR1:COUP AC') # enables AC coupling on channel 1

# by default LOW level gain is selected
# rp_s.tx_txt('ACQ:SOUR1:GAIN LV') # user can switch gain using this command

# configuramos la FPGA
rp_s.tx_txt('RP:FPGABITREAM_DSD 0.94')

#configuramos el shunt
R_shunt_k=3
veamos = ParamikoMachine('158.42.32.24', user = "root", password="root")
veamos.env["LD_LIBRARY_PATH"]="/opt/redpitaya/lib"
veamos.cwd.chdir("/opt/redpitaya/bin")
comando="./i2c_shunt " + str(R_shunt_k)
# print (comando)
r_back = veamos[comando]
r_back()

# si vemos que se bloquea descomentar
rp_s.tx_txt('SOUR1:VOLT 1')
rp_s.tx_txt('SOUR1:VOLT:OFFS 0.00') # esto lo utilizo para cambiar el offset de canal b
rp_s.tx_txt('SOUR2:VOLT:OFFS 0.02') # esto lo utilizo para cambiar el offset de canal b
rp_s.tx_txt('SOUR1:BURS:NCYC 1')  # solo funciona si led3 esta activado, numero de ciclos por frecuencia
rp_s.tx_txt('SOUR1:BURS:NOR 225') # solo funciona si led3 esta activado, numero de frecuencias
rp_s.tx_txt('SOUR1:BURS:INT:PER 30') # solo funciona si led3 esta activado, ancho detector

rp_s.tx_txt('DIG:PIN LED'+str(1)+','+str(0))  # 1->state2  0->state1
rp_s.tx_txt('DIG:PIN LED'+str(2)+','+str(0))  # desbloqueo finalizacion state1, tambien genera inicio
rp_s.tx_txt('DIG:PIN LED'+str(3)+','+str(1))  #activacion del led3


t1=pc()
rp_s.tx_txt('CHIRP ON')

# rp_s.tx_txt('RP:FPGABITREAM_DSD 0.94')
while 1 :
#    rp_s.tx_txt('FIN:RAF:STAT? 1')
    rp_s.tx_txt('DIG:PIN? DIO'+str(7)+'_N')
    state = rp_s.rx_txt()
    if state == '1':
        break
#    # print(rp_s.rx_txt())
# rp_s.tx_txt('DIG:PIN? DIO'+str(7)+'_N')
# state = rp_s.rx_txt()
print(state)
# EMPEZAMOS CON LA ADQUISION

rp_s.tx_txt('CHIRP OFF')
rp_s.tx_txt('ACQ:RESULT1:DATA?')
t3=pc()

buff_string = rp_s.rx_txt()
buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
buff = list(map(float, buff_string))
t4=pc()
my_array = np.asarray(buff)
# super_buffer.append(buff)
# super_buffer_flat=sum(super_buffer, [])

t5=pc()
print('t5-t1:',t5-t1)
#Enable output
iteracion=1

Z=my_array[0:225]
PHASE=my_array[256: 256+225]*frecuencias*360/125e6
plotZ=plt.figure(2*iteracion+1)
plt.semilogx(frecuencias, Z,'o')
#plt.semilogx(frecuencias,amplreference,'o')
plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
plt.ylabel('Z')

plotPHASE=plt.figure(2*iteracion+2)
plt.semilogx(frecuencias,PHASE, 'o')
#plt.semilogx(frecuencias,phases,'o')
plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
plt.ylabel('PHASE')



plt.show()
# view rawacquire_trigger_posedge.py

