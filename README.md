MIOPATIA

Instrucciones:
1) Acordarse de que el spi server esté funcionando en la redpitaya. Se puede hacer a través del aaplicación web->development->scpi server->run o manualmente con el comando

systemctl start redpitaya_scpi &

2) Para que funcione la aplicación es necesario que tu redpitaya tenga instalado en 
/opt/redpitaya/bin

la aplicación i2c_shunt , necesaria para modificar la resistencia de shunt.

Dicha aplicación, así como su fichero fuente (por si quisiera recompilarse) se encuentra en la carpeta de utilidades
