import sys
import redpitaya_scpi as scpi
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

rp_s = scpi.scpi(sys.argv[1])

wave_form = 'sine'
frecuencias = [1000000,5000000]
fm=125000000
numero_pulsos=10
ampl = 1






rp_s.tx_txt('SOUR1:BURS:STAT ON') # % Set burst mode to ON
rp_s.tx_txt('SOUR1:BURS:NCYC 20') # Set 10 pulses of sine wave
# rp_s.tx_txt('SOUR1:BURS:NOR 2') # Set 2 repeticiones


# there is an option to select coupling when using SIGNALlab 250-12
# rp_s.tx_txt('ACQ:SOUR1:COUP AC') # enables AC coupling on channel 1

# by default LOW level gain is selected
# rp_s.tx_txt('ACQ:SOUR1:GAIN LV') # user can switch gain using this command

# parametros de la adquisicion



# EMPEZAMOS CON LA ADQUISION


#Enable output
iteracion=1
super_buffer=[]
for freq in frecuencias:
    rp_s.tx_txt('GEN:RST')
    rp_s.tx_txt('ACQ:RST')

    rp_s.tx_txt('SOUR1:FUNC ' + str(wave_form).upper())
    rp_s.tx_txt('SOUR1:VOLT ' + str(ampl))


    rp_s.tx_txt('SOUR1:FREQ:FIX ' + str(freq))

    rp_s.tx_txt('ACQ:DEC 1')
    rp_s.tx_txt('ACQ:TRIG:LEV 125')
    rp_s.tx_txt('ACQ:TRIG:DLY 0')

    rp_s.tx_txt('ACQ:START')
    rp_s.tx_txt('ACQ:TRIG AWG_PE')
    rp_s.tx_txt('OUTPUT1:STATE ON')
# ESPERAMOS EL TRIGGER
    while 1:
        rp_s.tx_txt('ACQ:TRIG:STAT?')
        if rp_s.rx_txt() == 'TD':
            break
    rp_s.tx_txt('ACQ:TPOS?')
    veamos= rp_s.rx_txt()
    posicion_trigger=int(veamos)
    rp_s.tx_txt('ACQ:BUF:SIZE?')
    veamos2= rp_s.rx_txt()
    fantastico=fm*numero_pulsos/freq
    # LEEMOS Y REPRESENTAMOS
    rp_s.tx_txt('ACQ:SOUR1:DATA?')
    buff_string = rp_s.rx_txt()
    buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
    buff = list(map(float, buff_string))

    my_array = np.asarray(buff)
    super_buffer.append(buff)
    super_buffer_flat=sum(super_buffer, [])
    yf = fft(my_array)
    N=my_array.shape[0]
    T=1/fm
    idea=N//2
    xf = fftfreq(N, T)[:N//2]
    plot1=plt.figure(iteracion)
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    plt.xlabel('Frecuencia')
    iteracion=iteracion+1
    rp_s.tx_txt('OUTPUT1:STATE OFF')
    rp_s.tx_txt('ACQ:STOP')

plt.grid()
plot1=plt.figure(iteracion)

plt.plot(super_buffer_flat)
plt.ylabel('Voltage')

plt.show()
# view rawacquire_trigger_posedge.py

