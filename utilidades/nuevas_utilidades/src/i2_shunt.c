#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <complex.h>
#include <sys/param.h>



#define M_PI 3.14159265358979323846

#include <fcntl.h>
#include <linux/ioctl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <errno.h>
#include <stdint.h>

#define I2C_SLAVE_FORCE 		   0x0706
#define EXPANDER_ADDR            	   0x20

// switching shunt resistors
int main (int argc, char *argv[]) {

    if (argc==1) {
		//usage();
		return 0;
	}

    /** Argument check */
    if (argc<2) {
        fprintf(stderr, "Too few arguments!\n\n");
        //usage();
        return -1;
    }
    int k = strtod(argv[1], NULL);
    if ( (k < 0) || (k > 5) ) {
        fprintf(stderr, "Invalid shunt index value!\n\n");
        //usage();
        return -1;
    }    

    int  dat;
    int  fd; 
    int  status;
    char str [1+2*11];

    // parse input arguments
    //int k=3;
    //printf("k es %d \n",k);
    dat = (1<<k);

    // Open the device.
    fd = open("/dev/i2c-0", O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Cannot open the I2C device\n");
        return 1;
    }

    // set slave address
    status = ioctl(fd, I2C_SLAVE_FORCE, EXPANDER_ADDR);
    if (status < 0) {
        fprintf(stderr, "Unable to set the I2C address\n");
        return -1;
    }

    // Write to expander
    str [0] = 0; // set address to 0
    str [1+0x00] = 0x00; // IODIRA - set all to output
    str [1+0x01] = 0x00; // IODIRB - set all to output
    str [1+0x02] = 0x00; // IPOLA
    str [1+0x03] = 0x00; // IPOLB
    str [1+0x04] = 0x00; // GPINTENA
    str [1+0x05] = 0x00; // GPINTENB
    str [1+0x06] = 0x00; // DEFVALA
    str [1+0x07] = 0x00; // DEFVALB
    str [1+0x08] = 0x00; // INTCONA
    str [1+0x09] = 0x00; // INTCONB
    str [1+0x0A] = 0x00; // IOCON
    str [1+0x0B] = 0x00; // IOCON
    str [1+0x0C] = 0x00; // GPPUA
    str [1+0x0D] = 0x00; // GPPUB
    str [1+0x0E] = 0x00; // INTFA
    str [1+0x0F] = 0x00; // INTFB
    str [1+0x10] = 0x00; // INTCAPA
    str [1+0x11] = 0x00; // INTCAPB
    str [1+0x12] = (dat >> 0) & 0xff; // GPIOA
    str [1+0x13] = (dat >> 8) & 0xff; // GPIOB
    str [1+0x14] = (dat >> 0) & 0xff; // OLATA
    str [1+0x15] = (dat >> 8) & 0xff; // OLATB
    status = write(fd, str, 1+2*11);

    if (!status) fprintf(stderr, "Error I2C write\n");
    
    close(fd);
    return 0;
}