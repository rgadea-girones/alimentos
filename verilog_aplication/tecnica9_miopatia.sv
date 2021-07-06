// ============================================================================
// Copyright (c) 2013 by Terasic Technologies Inc.
// ============================================================================
//
// Permission:
//
//   Terasic grants permission to use and modify this code for use
//   in synthesis for all Terasic Development Boards and Altera Development 
//   Kits made by Terasic.  Other use of this code, including the selling 
//   ,duplication, or modification of any portion is strictly prohibited.
//
// Disclaimer:
//
//   This VHDL/Verilog or C/C++ source code is intended as a design reference
//   which illustrates how these types of functions can be implemented.
//   It is the user's responsibility to verify their design for
//   consistency and functionality through the use of formal
//   verification methods.  Terasic provides no warranty regarding the use 
//   or functionality of this code.
//
// ============================================================================
//           
//  Terasic Technologies Inc
//  9F., No.176, Sec.2, Gongdao 5th Rd, East Dist, Hsinchu City, 30070. Taiwan
//  
//  
//                     web: http://www.terasic.com/  
//                     email: support@terasic.com
//
// ============================================================================
//Date:  Thu Jul 11 11:26:45 2013
// ============================================================================

//`define ENABLE_HPS
//`define ENABLE_USB

module tecnica9_miopatia(

      ///////// ADC /////////
      inout              ADC_CS_N,
      output             ADC_DIN,
      input              ADC_DOUT,
      output             ADC_SCLK,

      ///////// AUD /////////
      input              AUD_ADCDAT,
      inout              AUD_ADCLRCK,
      inout              AUD_BCLK,
      output             AUD_DACDAT,
      inout              AUD_DACLRCK,
      output             AUD_XCK,

      ///////// CLOCK2 /////////
      input              CLOCK2_50,

      ///////// CLOCK3 /////////
      input              CLOCK3_50,

      ///////// CLOCK4 /////////
      input              CLOCK4_50,

      ///////// CLOCK /////////
      input              CLOCK_50,

      ///////// DRAM /////////
      output      [12:0] DRAM_ADDR,
      output      [1:0]  DRAM_BA,
      output             DRAM_CAS_N,
      output             DRAM_CKE,
      output             DRAM_CLK,
      output             DRAM_CS_N,
      inout       [15:0] DRAM_DQ,
      output             DRAM_LDQM,
      output             DRAM_RAS_N,
      output             DRAM_UDQM,
      output             DRAM_WE_N,

      ///////// FAN /////////
      output             FAN_CTRL,

      ///////// FPGA /////////
      output             FPGA_I2C_SCLK,
      inout              FPGA_I2C_SDAT,

      ///////// GPIO /////////
     // inout     [35:0]   GPIO_0,
		
		///////// HEX0 /////////
      output      [6:0]  HEX0,

      ///////// HEX1 /////////
      output      [6:0]  HEX1,

      ///////// HEX2 /////////
      output      [6:0]  HEX2,

      ///////// HEX3 /////////
      output      [6:0]  HEX3,

      ///////// HEX4 /////////
      output      [6:0]  HEX4,

      ///////// HEX5 /////////
      output      [6:0]  HEX5,

`ifdef ENABLE_HPS
      ///////// HPS /////////
      input              HPS_CONV_USB_N,
      output      [14:0] HPS_DDR3_ADDR,
      output      [2:0]  HPS_DDR3_BA,
      output             HPS_DDR3_CAS_N,
      output             HPS_DDR3_CKE,
      output             HPS_DDR3_CK_N,
      output             HPS_DDR3_CK_P,
      output             HPS_DDR3_CS_N,
      output      [3:0]  HPS_DDR3_DM,
      inout       [31:0] HPS_DDR3_DQ,
      inout       [3:0]  HPS_DDR3_DQS_N,
      inout       [3:0]  HPS_DDR3_DQS_P,
      output             HPS_DDR3_ODT,
      output             HPS_DDR3_RAS_N,
      output             HPS_DDR3_RESET_N,
      input              HPS_DDR3_RZQ,
      output             HPS_DDR3_WE_N,
      output             HPS_ENET_GTX_CLK,
      inout              HPS_ENET_INT_N,
      output             HPS_ENET_MDC,
      inout              HPS_ENET_MDIO,
      input              HPS_ENET_RX_CLK,
      input       [3:0]  HPS_ENET_RX_DATA,
      input              HPS_ENET_RX_DV,
      output      [3:0]  HPS_ENET_TX_DATA,
      output             HPS_ENET_TX_EN,
      inout       [3:0]  HPS_FLASH_DATA,
      output             HPS_FLASH_DCLK,
      output             HPS_FLASH_NCSO,
      inout              HPS_GSENSOR_INT,
      inout              HPS_I2C1_SCLK,
      inout              HPS_I2C1_SDAT,
      inout              HPS_I2C2_SCLK,
      inout              HPS_I2C2_SDAT,
      inout              HPS_I2C_CONTROL,
      inout              HPS_KEY,
      inout              HPS_LED,
      inout              HPS_LTC_GPIO,
      output             HPS_SD_CLK,
      inout              HPS_SD_CMD,
      inout       [3:0]  HPS_SD_DATA,
      output             HPS_SPIM_CLK,
      input              HPS_SPIM_MISO,
      output             HPS_SPIM_MOSI,
      inout              HPS_SPIM_SS,
      input              HPS_UART_RX,
      output             HPS_UART_TX,
      input              HPS_USB_CLKOUT,
      inout       [7:0]  HPS_USB_DATA,
      input              HPS_USB_DIR,
      input              HPS_USB_NXT,
      output             HPS_USB_STP,
`endif /*ENABLE_HPS*/

      ///////// IRDA /////////
      input              IRDA_RXD,
      output             IRDA_TXD,

      ///////// KEY /////////
      input       [3:0]  KEY,

      ///////// LEDR /////////
      output      [9:0]  LEDR,

      ///////// PS2 /////////
      inout              PS2_CLK,
      inout              PS2_CLK2,
      inout              PS2_DAT,
      inout              PS2_DAT2,

      ///////// SW /////////
      input       [9:0]  SW,

      ///////// TD /////////
      input              TD_CLK27,
      input      [7:0]   TD_DATA,
      input              TD_HS,
      output             TD_RESET_N,
      input              TD_VS,

`ifdef ENABLE_USB
      ///////// USB /////////
      input              USB_B2_CLK,
      inout       [7:0]  USB_B2_DATA,
      output             USB_EMPTY,
      output             USB_FULL,
      input              USB_OE_N,
      input              USB_RD_N,
      input              USB_RESET_N,
      inout              USB_SCL,
      inout              USB_SDA,
      input              USB_WR_N,
`endif /*ENABLE_USB*/

      ///////// VGA /////////
      output      [7:0]  VGA_B,
      output             VGA_BLANK_N,
      output             VGA_CLK,
      output      [7:0]  VGA_G,
      output             VGA_HS,
      output      [7:0]  VGA_R,
      output             VGA_SYNC_N,
      output             VGA_VS,

	//////////// GPIO_0_1, GPIO_0_1 connect to ADA - High Speed ADC/DAC //////////
	output		          		ADC_CLK_A,
	output		          		ADC_CLK_B,
	input 		    [13:0]		ADC_DA,
	input 		    [13:0]		ADC_DB,
	output		          		ADC_OEB_A,
	output		          		ADC_OEB_B,
	input 		          		ADC_OTR_A,
	input 		          		ADC_OTR_B,
	output		          		DAC_CLK_A,
	output		          		DAC_CLK_B,
	output	logic	    [13:0]		DAC_DA,
	output		    [13:0]		DAC_DB,
	output		          		DAC_MODE,
	output		          		DAC_WRT_A,
	output		          		DAC_WRT_B,
	input 		          		OSC_SMA_ADC4,
	output		          		POWER_ON,
	input 		          		SMA_DAC4

);


//=======================================================
//  REG/WIRE declarations
//=======================================================

//=======================================================
//  REG/WIRE declarations
//=======================================================
assign  DAC_WRT_B = ~CLK_125;      //Input write signal for PORT B
assign  DAC_WRT_A = ~CLK_125;      //Input write signal for PORT A

assign  DAC_MODE = 1; 		       //Mode Select. 1 = dual port, 0 = interleaved.

assign  DAC_CLK_B = ~CLK_125; 	    //PLL Clock to DAC_B
assign  DAC_CLK_A = ~CLK_125; 	    //PLL Clock to DAC_A
 
assign  ADC_CLK_B = ~CLK_65;  	    //PLL Clock to ADC_B
assign  ADC_CLK_A = ~CLK_65;  	    //PLL Clock to ADC_A


assign  ADC_OEB_A = 0; 		  	    //ADC_OEA
assign  ADC_OEB_B = 0; 			    //ADC_OEB

/////////////////////////////////////


wire    [13:0]	sin_out;



wire    [31:0]	fase;
wire    [31:0]	modulo, moduloA, moduloB;
wire    [7:0]  direccion;
wire    wren;
wire    [21:0] temp1,temp2;



assign  phasinc1 = 32'd34359738;
assign  phasinc2 = phasinc1<<1;



assign  POWER_ON  = 1;            //Disable OSC_SMA

reg		 [13:0]		r_ADC_DA/*synthesis noprune*/;
reg	signed	 [13:0]		r_ADC_DB/*synthesis noprune*/;
reg		 [13:0]		r_DAC_DA/*synthesis noprune*/;

reg       [13:0]     ADC_DA_reg, ADC_DA_reg2;
reg       [13:0]     ADC_DB_reg, ADC_DB_reg2;
//reg		 [13:0]		r_DAC_DB/*synthesis noprune*/;

/*
assign temp1=(ADC_DA-13'd6702)*8'b01011011;
assign temp2=(ADC_DB-13'd6702)*8'b01011011;

always @ (posedge CLK_65) r_ADC_DA <= 2*temp1[18:6]-13'd4096;
always @ (posedge CLK_65) r_ADC_DB <= 2*temp2[18:6]-13'd4096;





*/


//sincronizadores

always_ff @(posedge CLK_125 )
	begin
			ADC_DA_reg<=ADC_DA;
			ADC_DA_reg2<=ADC_DA_reg;
			ADC_DB_reg<=ADC_DB;
			ADC_DB_reg2<=ADC_DB_reg;
			
	end

localparam DESFASE1=20, DESFASE2=30;

localparam [13:0] cero_magnitud='0;

logic [(DESFASE2 -1):0][13:0] auxB;

logic  signed[13:0] LOOP_B_DESFASADO;

always_ff @(posedge CLK_125 or negedge KEY[0])
	if (!KEY[0])
			  auxB<={(DESFASE2){cero_magnitud}};
	else
			auxB<={r_DAC_DA,auxB[DESFASE2-1:1]};

	assign LOOP_B_DESFASADO=auxB[0];

assign temp1=(ADC_DA_reg2-13'd6690)*8'b10101110;
assign temp2=(ADC_DB_reg2-13'd6690)*8'b10101110;

always @ (posedge CLK_125) r_ADC_DA <= temp1[18:6]-13'd4096;
always @ (posedge CLK_125) r_ADC_DB <= SW[1]?({LOOP_B_DESFASADO[13],LOOP_B_DESFASADO[13:1]}): temp2[18:6]-13'd4096;


always @ (posedge CLK_125) r_DAC_DA <= {sin_out[13],sin_out[13:1]};

always @ (posedge CLK_125) DAC_DA <= {sin_out[13],sin_out[13:1]}+13'd4096;







nios_system_tec9_miopatia u0(
		.reset_n(KEY[0]),                                  //               clk_50_clk_in_reset.reset_n
		.clk_50(CLOCK_50),    
        .clk_125mhz_clk              (CLK_125),       
        .clk_65mhz_clk               (CLK_65), 
		//                     clk_50_clk_in.clk
		.pll_outclk1_clk(DRAM_CLK),                             //                         pll_sdram.clk

		.zs_addr_from_the_sdram(DRAM_ADDR),                   //                        sdram_wire.addr
		.zs_ba_from_the_sdram(DRAM_BA),                     //                                  .ba
		.zs_cas_n_from_the_sdram(DRAM_CAS_N),                  //                                  .cas_n
		.zs_cke_from_the_sdram(DRAM_CKE),                    //                                  .cke
		.zs_cs_n_from_the_sdram(DRAM_CS_N),                   //                                  .cs_n
		.zs_dq_to_and_from_the_sdram(DRAM_DQ),              //                                  .dq
		.zs_dqm_from_the_sdram({DRAM_UDQM,DRAM_LDQM}),                    //                                  .dqm
		.zs_ras_n_from_the_sdram(DRAM_RAS_N),                  //                                  .ras_n
		.zs_we_n_from_the_sdram(DRAM_WE_N)  ,                 //                                  .we_n
        .in_port_to_the_sw           ()   ,
        .in_port_to_the_key          (),          // key_external_connection.export
        .out_port_from_the_led       () 		
		
		
	);

	
Control_path
#(.DATA_WIDTH(32), .ADDR_WIDTH(8), .MAGNITUD_WIDTH(14), .ancho_detector(30),.ciclos(1), .FICHERO_INICIAL("freq_log.dat"))

Ucontrol
(.clk125(CLK_125),
.clk65(CLK_65),
//.test(SW[0]),
.areset_n(KEY[0]),
.start(~KEY[3]),
.ADC_A(r_ADC_DA),
.ADC_B(r_ADC_DB),
.address_mem(direccion),
.fin(),
.fin2(wren),
.DAC_S_registrado(sin_out),
.MODULO(modulo),
.PHASE(fase),
.MODULOA(moduloA),
.MODULOB(moduloB)
);


fases_mem M1(
	.address(direccion),
	.clock(CLK_125),
	.data(fase),
	.wren(wren),
	.q());
	
modulo_mem M2(
	.address(direccion),
	.clock(CLK_125),
	.data(modulo),
	.wren(wren),
	.q());
	

moduloA_mem M3(
	.address(direccion),
	.clock(CLK_125),
	.data(moduloA),
	.wren(wren),
	.q());
moduloB_mem M4(
	.address(direccion),
	.clock(CLK_125),
	.data(moduloB),
	.wren(wren),
	.q());	


endmodule
