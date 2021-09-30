MIOPATIA

Instrucciones:

0) Supongamos que me he bajado la imagen de redpitaya y he arrancado mi placa con dicha imagen que he escrito en mi sdcard

1) Hay que hacer los siguientes cambios:

        a) Cambiar el servidor scpi-server
        
        Mirar en utilidades y copiar el fichero scpi-server allí existente en

        /opt/redpitaya/bin


        b) Cambiar la librería asociada de la api.

        Mirar en utilidades y copiar los ficheros librp.so e librp.a en

        /opt/redpitaya/lib

        c) Añadir un fichero de configuración de FPGA a los existentes por defecto

        Mirar en utilidades y copiar el fichero fpga_DSD_0.94.bit en

        /opt/redpitaya/fpga

2) Acordarse de que el spi server esté funcionando en la redpitaya. Se puede hacer a través del aaplicación web->development->scpi server->run o manualmente con el comando

systemctl start redpitaya_scpi &

3) Para que funcione la aplicación es necesario que tu redpitaya tenga instalado en 
/opt/redpitaya/bin

la aplicación i2c_shunt , necesaria para modificar la resistencia de shunt.

Dicha aplicación, así como su fichero fuente (por si quisiera recompilarse) se encuentra en la carpeta de utilidades
