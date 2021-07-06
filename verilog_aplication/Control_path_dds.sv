module Control_path
  #(parameter DATA_WIDTH=32, parameter ADDR_WIDTH=8, parameter MAGNITUD_WIDTH=14, parameter ancho_detector=10, parameter ciclos=4, parameter FICHERO_INICIAL="freq_log.dat", parameter shunt=1000)
   (input clk125,
    input clk65,
    input areset_n,
    input start,
    input test,
    input logic signed [MAGNITUD_WIDTH-1:0] ADC_A,
    input logic signed [MAGNITUD_WIDTH-1:0] ADC_B,
    output logic fin,
    output logic fin2,
    output logic VALID_M,
    output logic [DATA_WIDTH-1:0] incrementado,
    output logic signed [MAGNITUD_WIDTH-1:0] DAC_S_registrado,
    output logic signed[31:0] MODULO,
    output logic signed[31:0] MODULOA,
    output logic signed[31:0] MODULOB,
    output logic [7:0] address_mem,
    output logic [7:0] address_mem2,
    output logic signed [31:0] PHASE
   );

  logic signed [MAGNITUD_WIDTH-1:0] DAC_A;
  //generacion
  logic detectado_cero_S;
  enum  logic [2:0] {G0, G1,G1B, G2,G3} state1;

  enum logic [2:0] {S0 , S1,  S3,S4} state2;

  //logic [7:0] address_mem;
  logic [2:0] contador_5_ciclos;

  //logic [31:0] phase_accumulator;
  logic ovalid;


  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      address_mem<=0;  //cambiado para verificacion hardware
      contador_5_ciclos<='0;
      state1<=G0;
      fin<=1'b0;
    end
    else
    case(state1)
      G0:
      begin
        fin<=1'b0;
        if (start)
          state1 <= G1;
      end
      G1:
        if (ovalid)
          state1<=G2;
      G1B:
        if (state2==S0)
          state1<=G2;
      G2:
      begin
        if (detectado_cero_S==1'b1)
          if ((contador_5_ciclos>ciclos)&&(address_mem!=199))
          begin
            state1 <= G1B;
            //address_mem<=address_mem+1;
            contador_5_ciclos<=0;
          end
          else
            //		if ((address_mem!=199)||((address_mem==199)&& (contador_5_ciclos<=ciclos)))
            contador_5_ciclos<=contador_5_ciclos+1;
        if ((address_mem==199))
        begin
          if (fin2==1'b1)
          begin
            state1<=G3;
            address_mem<=0;
            contador_5_ciclos<='0;
            fin<=1'b1;
          end
        end
        if ((contador_5_ciclos>ciclos)&&(detectado_cero_S==1'b1))
        begin
          address_mem<=address_mem+1;
        end
      end
      G3:
      begin
        fin<=1'b0;
        if (!start)
          state1 <= G0;
      end



    endcase

  end

  //recepcion

  logic [ancho_detector-1:0] shifterS;
  logic [ancho_detector-1:0] shifterA;
  logic [ancho_detector-1:0] shifterB;
  logic signed [MAGNITUD_WIDTH-1:0] ADC_A_registrado;
  logic signed [MAGNITUD_WIDTH-1:0] ADC_B_registrado;
  //logic signed [MAGNITUD_WIDTH-1:0] DAC_S_registrado;
  logic detectado_cero_A;
  logic detectado_cero_B;


  localparam [MAGNITUD_WIDTH-1:0] cero_magnitud='0;
  localparam tamanyo_shifter=1;
  logic [MAGNITUD_WIDTH-1:0] auxA;
  logic [MAGNITUD_WIDTH-1:0] auxB;
  logic [MAGNITUD_WIDTH-1:0] auxS;

  always_ff @(posedge clk125 or negedge areset_n)
    if (!areset_n)
      auxA<={{cero_magnitud}};
    else
      auxA<={ADC_A};

  assign ADC_A_registrado=auxA;

  always_ff @(posedge clk125 or negedge areset_n)
    if (!areset_n)
      auxB<={{cero_magnitud}};
    else
      auxB<={ADC_B};

  assign ADC_B_registrado=auxB;

  always_ff @(posedge clk125 or negedge areset_n)
    if (!areset_n)
      auxS<={{cero_magnitud}};
    else
      auxS<={DAC_A};

  assign DAC_S_registrado=auxS;




  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterA<='0;
    else
      shifterA<={ADC_A[MAGNITUD_WIDTH-1], shifterA[ancho_detector-1:1]};
  end

  assign detectado_cero_A= (~|shifterA[ancho_detector-2:0]) && (shifterA[(ancho_detector-1)]);



  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterB<='0;
    else
      shifterB<={ADC_B[MAGNITUD_WIDTH-1], shifterB[ancho_detector-1:1]};

  end
  assign detectado_cero_B= (~|shifterB[ancho_detector-2:0]) && (shifterB[(ancho_detector-1) ]);


  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterS<='0;
    else
      shifterS<={DAC_A[MAGNITUD_WIDTH-1], shifterS[ancho_detector-1:1]};

  end
  assign detectado_cero_S= (~|shifterS[ancho_detector-2:0]) && (shifterS[(ancho_detector-1)]);






  logic [2:0] contador_4_ciclosA, contador_4_ciclosB;
  logic [31:0] diferencia_pos, diferencia_neg;

  logic signed [MAGNITUD_WIDTH-1:0] MODULO_POSA, MODULO_NEGA;
  //logic signed [MAGNITUD_WIDTH-1:0] MODULOA, MODULOB;
  logic signed [MAGNITUD_WIDTH-1:0] MODULO_POSB, MODULO_NEGB;
  logic signed [MAGNITUD_WIDTH-1:0] PHASE_PRE;
  logic signed     [63:0]                      temporal;
  always_ff@(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      contador_4_ciclosA<='0;
      contador_4_ciclosB<='0;
      state2<=S0;
      fin2<=1'b0;
      MODULOA<='0;
      MODULOB<='0;
      //MODULO<='0;
      //PHASE<='0;
      MODULO_POSA<='0;
      MODULO_POSB<='0;
      MODULO_NEGA<='0;
      MODULO_NEGB<='0;
    end
    else
    case(state2)
      S0:
      begin
        fin2<=1'b0;
        diferencia_pos<='0;
        diferencia_neg<='0;
        contador_4_ciclosA<='0;
        contador_4_ciclosB<='0;
        if (state1==G1 || state1==G1B)
          state2 <= S1;
      end
      S1:
      begin
        if (detectado_cero_A==1'b1  )
        begin
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if (contador_4_ciclosA==ciclos && contador_4_ciclosB==ciclos)
          begin
            state2 <= S3;
            //diferencia_neg<=diferencia_neg+1;
          end
        end

        if ( detectado_cero_B==1'b1 )
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          if (contador_4_ciclosA==ciclos && contador_4_ciclosB==ciclos)
          begin
            state2 <= S4;
            // diferencia_pos<=diferencia_pos+1;
          end
        end
      end
      /*	S2A:
              begin
                  if (detectado_cero_B)
                      begin
      		    state2<=S3;
                          contador_4_ciclosB<=contador_B_ciclosA+1;
                          diferencia_pos<=diferencia_pos+1;
                      end	  
                  if (detectado_cero_A)
                      begin
      		    //state2<=S3;
                          contador_4_ciclosA<=contador_4_ciclosA+1;
                          //diferencia_pos<=diferencia_pos+1;
                      end	 
        
              end          
      	S2B: 	
              begin   
                  if (detectado_cero_A)
                      begin
      		    state2<=S4;
                          contador_4_ciclosA<=contador_4_ciclosA+1;
                          diferencia_neg<=diferencia_neg+1;
                      end	 
                  if (detectado_cero_B)
                      begin
      		  //  state2<=S4;
                          contador_4_ciclosB<=contador_4_ciclosB+1;
                         // diferencia_neg<=diferencia_neg+1;
                      end	 
              end                  
      */
      S3:     //positivo
      begin
        if (ADC_A_registrado>  MODULO_POSA)
          MODULO_POSA<=ADC_A_registrado;
        if (ADC_A_registrado<  MODULO_NEGA)
          MODULO_NEGA<=ADC_A_registrado;
        if (ADC_B_registrado>  MODULO_POSB)
          MODULO_POSB<=ADC_B_registrado;
        if (ADC_B_registrado<  MODULO_NEGB)
          MODULO_NEGB<=ADC_B_registrado;
        diferencia_pos<=diferencia_pos+1;
        if (detectado_cero_A)
        begin
          contador_4_ciclosA<=contador_4_ciclosA+1;
          diferencia_pos<='0;
          if ((contador_4_ciclosA == ciclos+1) && (contador_4_ciclosB == ciclos+2))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosB<='0;
          end
        end

        if (detectado_cero_B)
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          if ((contador_4_ciclosB == ciclos+1) && (contador_4_ciclosA == ciclos+2))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosB<='0;
          end

          if (contador_4_ciclosB == ciclos)
          begin
            temporal=(diferencia_pos*incrementado*360);
          end

        end
        if ((detectado_cero_B) && (detectado_cero_A))
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosB == ciclos+1) && (contador_4_ciclosA == ciclos+1))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosB<='0;
          end
        end

      end

      S4:     //negativo
      begin
        diferencia_neg <= diferencia_neg +1;
        if (ADC_A_registrado>  MODULO_POSA)
          MODULO_POSA<=ADC_A_registrado;
        if (ADC_A_registrado<  MODULO_NEGA)
          MODULO_NEGA<=ADC_A_registrado;
        if (ADC_B_registrado>  MODULO_POSB)
          MODULO_POSB<=ADC_B_registrado;
        if (ADC_B_registrado<  MODULO_NEGB)
          MODULO_NEGB<=ADC_B_registrado;
        if (detectado_cero_B)
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          diferencia_neg<='0;
          if ((contador_4_ciclosB == ciclos+1) && (contador_4_ciclosA == ciclos+2) )
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosA<='0;
          end
        end

        if (detectado_cero_A)
        begin
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosA==ciclos+1) && (contador_4_ciclosB==ciclos+2)) //esto obliga a dividir por 4 los desfases
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosA<='0;
          end
          if (contador_4_ciclosA == ciclos)
          begin
            temporal=-(diferencia_neg*incrementado*360);
          end

        end
        if ((detectado_cero_B) && (detectado_cero_A))
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosB == ciclos+1) && (contador_4_ciclosA == ciclos+1))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB<=(MODULO_POSB-MODULO_NEGB)>>>2;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal>>32);
            //contador_4_ciclosB<='0;
          end
        end
      end






    endcase

  end


  logic [31:0] cociente;
  logic findiv;


  Divisor_Alg2 #(.tamanyo(32))
               divisor0
               (
                 .CLK(clk125),
                 .RSTa(areset_n),
                 .Start(fin2),

                 .Num(MODULOA*shunt),
                 .Den(MODULOB),

                 .Coc(cociente),
                 .Res(),
                 .Done(findiv)

               );

  fifo_un_fichero #(.LENGTH(32), .SIZE(8))  DUV (.CLOCK(clk125),
                  .RESET_N(areset_n),
                  .DATA_IN(address_mem),
                  .READ(~findiv),
                  .WRITE(fin2),
                  .CLEAR_N(1'b1),
                  .F_FULL_N(),
                  .F_EMPTY_N(),
                  .USE_DW(),
                  .DATA_OUT(address_mem2));

  always_ff@(posedge clk125 or negedge areset_n)

    if(!areset_n)
      MODULO<='0;
    else
    begin
      VALID_M<=findiv;
      if (findiv)
      begin
        MODULO<=cociente-shunt;
        PHASE<=PHASE_PRE;
      end
    end

/*
  primera_prueba_nco sin1_source (
                       .clk       (clk125),       // clk.clk
                       .reset_n   (areset_n),   // rst.reset_n
                       .clken     (1'b1),     //  in.clken
                       .phi_inc_i (incrementado), //    .phi_inc_i
                       .fsin_o    (DAC_A),    // out.fsin_o
                       //.fcos_o    (cos_out),
                       .out_valid (ovalid)  //    .out_valid
                     );
*/                     

                    
  DDS_rafa sin2_source (
                       .clk       (clk125),       // clk.clk
                       .reset_n   (areset_n),   // rst.reset_n
                       .clken     (1'b1),     //  in.clken
                       .phi_inc_i (incrementado), //    .phi_inc_i
                       .fsin_o    (DAC_A),    // out.fsin_o
                       //.fcos_o    (cos_out),
                       .out_valid (ovalid)  //    .out_valid
                     );


  // Declare the ROM variable
  logic [DATA_WIDTH-1:0] rom[2**ADDR_WIDTH-1:0];

  // Initialize the ROM with $readmemb.  Put the memory contents
  // in the file single_port_rom_init.txt.  Without this file,
  // this design will not compile.
  // See Verilog LRM 1364-2001 Section 17.2.8 for details on the
  // format of this file.

  initial
  begin
    $readmemh(FICHERO_INICIAL, rom);
  end

  assign incrementado = test? 32'd34359738:rom[address_mem]; //puro combinacional


endmodule


