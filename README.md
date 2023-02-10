MIOPATIA

Instrucciones:

0) Supongamos que me he bajado la imagen de redpitaya y he arrancado mi placa con dicha imagen que he escrito en mi sdcard

1) Es importante conectarse adecuadamente. Las instrucciones se pueden ver en
        https://redpitaya.readthedocs.io/en/latest/quickStart/connect/connect.html
        
        Es importante al terminar esta conectividad que podamos conectarnos via ssh (para poder hacer el punto 2 es necesario poder transferir ficheros) con la placa y que sepamos la IP de la placa en la LAN que tenemos. 

2) Hay que hacer los siguientes cambios:

        a) Cambiar el servidor scpi-server
        
        Mirar en utilidades/super_nuevas_utilidades y copiar el fichero scpi-server allí existente en

        /opt/redpitaya/bin


        b) Cambiar la librería asociada de la api.

        Mirar en utilidades/super_nuevas_utilidades y copiar los ficheros librp.so e librp.a en

        /opt/redpitaya/lib

        c) Añadir un fichero de configuración de FPGA a los existentes por defecto

        Mirar en utilidades/super_nuevas_utilidades y copiar el fichero fpga_DSD_0.94.bit en

        /opt/redpitaya/fpga

        d) (opcional) Sustituir el fichero de configuración de FPGA que viene por defecto en la imagen original.

        Mirar en utilidades/super_nuevas_utilidades y copiar el fichero fpga_0.94.bit en

        /opt/redpitaya/fpga

3) Acordarse de que el spi server esté funcionando en la redpitaya. Se puede hacer a través del aplicación web->development->scpi server->run o manualmente con el comando

systemctl start redpitaya_scpi &

4) Supongamos que ya tengo bien conectada la placa, cambiados los ficheros y lanzado el spi_server. Es el momento de lanzar la aplicación python remota (en nuestro PC) que se conectará con la placa.

     a) Necesito saber la IP porque es el único argumento que necesita la aplicación python denominada miopatia.py para ser lanzada
     
     b) Si todo ha sido correcto se abrirá el entorno para el manejo de la placa
