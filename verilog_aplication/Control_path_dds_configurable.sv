module Control_path_rafa
  #(parameter DATA_WIDTH=32, parameter ADDR_WIDTH=8, parameter MAGNITUD_WIDTH=14, parameter pancho_detector=10, parameter pciclos=4, parameter FICHERO_INICIAL="freq_log.dat", parameter shunt=1000)
   (input clk125,
    input clk65,
    input areset_n,
    input start,
    input test1,
    input test2,
    input test3,
    input [2:0] salto,
    input [7:0] numero_rep,
    input [2:0] num_ciclos,
    input [7:0] numero_anchura,
    input logic signed [MAGNITUD_WIDTH-1:0] ADC_A,
    input logic signed [MAGNITUD_WIDTH-1:0] ADC_B,
    output logic fin,
    output logic fin2,
    output logic VALID_M,
    output logic VALID_P,
    
    output logic [DATA_WIDTH-1:0] incrementado,
    output logic signed [MAGNITUD_WIDTH-1:0] DAC_S_registrado,
    output logic signed[31:0] MODULO,
    output logic signed[31:0] MODULOA,
    output logic signed[31:0] MODULOB,
    output logic [7:0] address_mem,
    output logic [7:0] address_mem2,
    output logic [7:0] address_mem3,    

    output logic [2:0] estado_pasos_cero,
    output logic signed [31:0] PHASE,
    output logic signed [31:0] PHASEA,
    output logic signed [31:0] PHASEB
   );
parameter G0=3'b000, G1=3'b001, G1B=3'b100, G2=3'b010, G3=3'b011;
parameter S0=3'b000, S1=3'b001, S4=3'b100,  S3=3'b011;
parameter D0=2'b00, D1=2'b01, D2=2'b10;
  logic signed [MAGNITUD_WIDTH-1:0] DAC_A;
  logic signed [MAGNITUD_WIDTH-1:0] DAC_A_cos;
  //generacion
  logic detectado_cero_S, detectado_cero_Snormal,detectado_cero_Stest;
  logic detectado_cero_A, detectado_cero_Anormal,detectado_cero_Atest;
  logic detectado_cero_B, detectado_cero_Bnormal,detectado_cero_Btest;
  
  // enum  logic [2:0] {G0, G1,G1B, G2,G3} state1;

  // enum logic [2:0] {S0 , S1,  S3,S4} state2;
  
  logic [2:0] state1;

  logic [2:0] state2;

  //logic [7:0] address_mem;
  logic [2:0] contador_5_ciclos;
  logic [2:0] ciclos;
  logic [7:0] repeticiones;
  logic [7:0] ancho_detector;
  logic [7:0] paso;
  logic [7:0] anchura_variable;
  
  
  assign anchura_variable=address_mem<100?numero_anchura:30;
  
  assign ciclos=test3?num_ciclos:pciclos;
  assign repeticiones=test3?numero_rep:225; //numero de puntos que tenemos
  assign ancho_detector=test3?anchura_variable:pancho_detector;
  // assign ancho_detector=pancho_detector;
  //assign paso=test3?{{5{1'b0}},salto}:8'b00000001;
  // assign paso=1;
  assign paso=8'b00000001;
  assign detectado_cero_S=detectado_cero_Stest;
  assign detectado_cero_A=detectado_cero_Atest;
  assign detectado_cero_B=detectado_cero_Btest;
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
        if ((state2==S0) ) //|| (test2==1'b1))
          state1<=G2;
      G2:
      begin
        if (detectado_cero_S==1'b1)
          if ((contador_5_ciclos>ciclos)&&(address_mem<repeticiones))
          begin
            state1 <= G1B;
            //address_mem<=address_mem+1;
            contador_5_ciclos<=0;
          end
          else
            //		if ((address_mem!=199)||((address_mem==199)&& (contador_5_ciclos<=ciclos)))
            contador_5_ciclos<=contador_5_ciclos+1;
        if ((address_mem>=repeticiones))
        begin
          if ((fin2==1'b1)||(test2==1'b1))
          
          begin
            state1<=G3;
           // if (!test2)
           //     address_mem<='0;           
            contador_5_ciclos<='0;
            fin<=1'b1;
          end
        end
        if ((contador_5_ciclos>ciclos)&&(detectado_cero_S==1'b1))
        begin
            if (address_mem>=repeticiones)
                address_mem<=repeticiones;
            else
                address_mem<=address_mem+paso;
        end
      end
      G3:
      begin
        fin<=1'b1;
        if (!start)
        begin
          state1 <= G0;
          address_mem<='0;
         end   
      end



    endcase

  end

  //recepcion
/*
  logic [ancho_detector-1:0] shifterS;
  logic [ancho_detector-1:0] shifterA;
  logic [ancho_detector-1:0] shifterB;
  */
  
  logic signed [31:0] ADC_A_registrado;
  logic signed [31:0] ADC_B_registrado;
  //logic signed [MAGNITUD_WIDTH-1:0] DAC_S_registrado;



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

  assign ADC_A_registrado={{18{auxA[13]}},auxA};

  always_ff @(posedge clk125 or negedge areset_n)
    if (!areset_n)
      auxB<={{cero_magnitud}};
    else
      auxB<={ADC_B};

  assign ADC_B_registrado={{18{auxB[13]}},auxB};

  always_ff @(posedge clk125 or negedge areset_n)
    if (!areset_n)
      auxS<={{cero_magnitud}};
    else
      auxS<={DAC_A};

  assign DAC_S_registrado=auxS;


/*

  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterA<='0;
    else
      shifterA<={auxA[MAGNITUD_WIDTH-1], shifterA[ancho_detector-1:1]};
  end

  assign detectado_cero_Anormal= (~|shifterA[ancho_detector-2:0]) && (shifterA[(ancho_detector-1)]);
 */
  logic [1:0]  detect_a, detect_b, detect_s;
  logic [7:0] counta;
  
   always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      detect_a<=D0;
      counta<='0;
      detectado_cero_Atest<=1'b0;
      end
    else
      case (detect_a)
        D0: if (auxA[MAGNITUD_WIDTH-1]==1'b0)
        begin
                detect_a<=D1;
                detectado_cero_Atest<=1'b0;
                counta<=counta+1;
        end
        else 
        begin
                detect_a<=D0;
                detectado_cero_Atest<=1'b0;
                counta<='0;
        end
        D1: if (auxA[MAGNITUD_WIDTH-1]==1'b0 )
                    if(counta<ancho_detector) 
                        begin
                        detect_a<=D1;
                        counta<=counta+1;
                        detectado_cero_Atest<=1'b0;
                        end
                        else
                        begin
                        detect_a<=D2;
                        detectado_cero_Atest<=1'b0;
                        counta<='0;
                        end  
              else
                     begin
                        detect_a<=D0;
                        counta<='0;
                        detectado_cero_Atest<=1'b0;
                      end    
         D2: if (auxA[MAGNITUD_WIDTH-1]==1'b1)
            begin
                    detect_a<=D0;
                    detectado_cero_Atest<=1'b1;
                    counta<='0;
            end
            else 
            begin
                    detect_a<=D2;
                    detectado_cero_Atest<=1'b0;
                    counta<='0;
            end                     
           default: begin
                    detect_a<=D0;
                    counta<='0;
                    detectado_cero_Atest<=1'b0;
                    end           
         endcase
   end
         
             
  


/*
  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterB<='0;
    else
      shifterB<={auxB[MAGNITUD_WIDTH-1], shifterB[ancho_detector-1:1]};

  end
  assign detectado_cero_Bnormal= (~|shifterB[ancho_detector-2:0]) && (shifterB[(ancho_detector-1) ]);
  
*/  
 // enum logic [1:0] {D0 , D1}  detect_b;
  logic [7:0] countb;
  
   always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      detect_b<=D0;
      countb<='0;
      detectado_cero_Btest<=1'b0;
      end
    else
      case (detect_b)
        D0: if (auxB[MAGNITUD_WIDTH-1]==1'b0)
        begin
                detect_b<=D1;
                detectado_cero_Btest<=1'b0;
                countb<=countb+1;
        end
        else 
        begin
                detect_b<=D0;
                detectado_cero_Btest<=1'b0;
                countb<='0;
        end
        D1: if (auxB[MAGNITUD_WIDTH-1]==1'b0 )
                    if(countb<ancho_detector) 
                        begin
                        detect_b<=D1;
                        countb<=countb+1;
                        detectado_cero_Btest<=1'b0;
                        end
                     else
                        begin
                        detect_b<=D2;
                        detectado_cero_Btest<=1'b0;
                        countb<='0;
                        end  
              else
                     begin
                        detect_b<=D0;
                        countb<='0;
                        detectado_cero_Btest<=1'b0;
                      end   
         D2: if (auxB[MAGNITUD_WIDTH-1]==1'b1)
            begin
                    detect_b<=D0;
                    detectado_cero_Btest<=1'b1;
                    countb<='0;
            end
            else 
            begin
                    detect_b<=D2;
                    detectado_cero_Btest<=1'b0;
                    countb<='0;
            end 
           default: begin
                    detect_b<=D0;
                    countb<='0;
                    detectado_cero_Btest<=1'b0;
                    end                                     
         endcase
   end                       
         
/*
  always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
      shifterS<='0;
    else
      shifterS<={auxS[MAGNITUD_WIDTH-1], shifterS[ancho_detector-1:1]};

  end
  assign detectado_cero_Snormal= (~|shifterS[ancho_detector-2:0]) && (shifterS[(ancho_detector-1)]);

*/

  logic [7:0] counts;
  
   always_ff @(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      detect_s<=D0;
      counts<='0;
      detectado_cero_Stest<=1'b0;
      end
    else
      case (detect_s)
        D0: if (auxS[MAGNITUD_WIDTH-1]==1'b0)
        begin
                detect_s<=D1;
                detectado_cero_Stest<=1'b0;
                counts<=counts+1;
        end
        else 
        begin
                detect_s<=D0;
                detectado_cero_Stest<=1'b0;
                counts<='0;
        end
        D1: if (auxS[MAGNITUD_WIDTH-1]==1'b0 )
                    if(counts<ancho_detector) 
                        begin
                        detect_s<=D1;
                        counts<=counts+1;
                        detectado_cero_Stest<=1'b0;
                        end
                        else
                        begin
                        detect_s<=D2;
                        detectado_cero_Stest<=1'b0;
                        counts<='0;
                        end  
              else
                     begin
                        detect_s<=D0;
                        counts<='0;
                        detectado_cero_Stest<=1'b0;
                      end    
         D2: if (auxS[MAGNITUD_WIDTH-1]==1'b1)
            begin
                    detect_s<=D0;
                    detectado_cero_Stest<=1'b1;
                    counts<='0;
            end
            else 
            begin
                    detect_s<=D2;
                    detectado_cero_Stest<=1'b0;
                    counts<='0;
            end   
           default: begin
                    detect_s<=D0;
                    counts<='0;
                    detectado_cero_Stest<=1'b0;
                    end                                   
        endcase
   end


  logic [2:0] contador_4_ciclosA, contador_4_ciclosB;
  logic signed [31:0] diferencia_pos, diferencia_neg;

  logic signed [31:0] MODULO_POSA, MODULO_NEGA;
  logic signed [31:0] MODULO_POSB, MODULO_NEGB;
  
  logic signed [31:0] MODULOA_pre, MODULOB_pre;
  logic signed [31:0] PHASE_PRE;
  logic signed     [31:0]                      temporal;
  
  //empezamos cosas nuevas
  
  logic signed [31:0] A_proyeccion_0;
  logic signed [31:0] A_proyeccion_1;
  logic signed [31:0] B_proyeccion_0;
  logic signed [31:0] B_proyeccion_1;
  
  logic signed [31:0] A_proyeccion_0_def;
  logic signed [31:0] A_proyeccion_1_def;
  logic signed [31:0] B_proyeccion_0_def;
  logic signed [31:0] B_proyeccion_1_def; 
  
  always_ff@(posedge clk125 or negedge areset_n)
  begin
    if(!areset_n)
    begin
      contador_4_ciclosA<='0;
      contador_4_ciclosB<='0;
      state2<=S0;
      fin2<=1'b0;
      MODULOA_pre<='0;
      MODULOB_pre<='0;
      //MODULO<='0;
      //PHASE<='0;
      MODULO_POSA<='0;
      MODULO_POSB<='0;
      MODULO_NEGA<='0;
      MODULO_NEGB<='0;
      A_proyeccion_0<='0;
      A_proyeccion_1<='0;
      B_proyeccion_0<='0;
      B_proyeccion_1<='0;
                  
    end
    else
    case(state2)
      S0:
      begin
        fin2<=1'b0;
        diferencia_pos<='0;
        diferencia_neg<='0;
        MODULO_POSA<='0;
        MODULO_POSB<='0;
        MODULO_NEGA<='0;
        MODULO_NEGB<='0;
        A_proyeccion_0<='0;
        A_proyeccion_1<='0;
        B_proyeccion_0<='0;
        B_proyeccion_1<='0;        
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
        
        A_proyeccion_0<=ADC_A_registrado*DAC_A+ A_proyeccion_0;
        A_proyeccion_1<=ADC_A_registrado*DAC_A_cos+A_proyeccion_1;
        B_proyeccion_0<=ADC_B_registrado*DAC_A+B_proyeccion_0; 
        B_proyeccion_1<=ADC_B_registrado*DAC_A_cos+B_proyeccion_1;               
        
        
        if (detectado_cero_A)
        begin
          contador_4_ciclosA<=contador_4_ciclosA+1;
          diferencia_pos<='0;
          if ((contador_4_ciclosA == ciclos+2) && (contador_4_ciclosB == ciclos+3))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
            //contador_4_ciclosB<='0;
          end
        end

        if (detectado_cero_B)
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          if ((contador_4_ciclosB == ciclos+2) && (contador_4_ciclosA == ciclos+3))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;            
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
            //contador_4_ciclosB<='0;
          end

          if (contador_4_ciclosB == ciclos)
          begin
            //temporal=(diferencia_pos*incrementado*360);
            temporal=diferencia_pos;
          end

        end
        if ((detectado_cero_B) && (detectado_cero_A))
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosB == ciclos+2) && (contador_4_ciclosA == ciclos+2))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;            
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
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
        A_proyeccion_0<=ADC_A_registrado*DAC_A+ A_proyeccion_0;
        A_proyeccion_1<=ADC_A_registrado*DAC_A_cos+A_proyeccion_1;
        B_proyeccion_0<=ADC_B_registrado*DAC_A+B_proyeccion_0; 
        B_proyeccion_1<=ADC_B_registrado*DAC_A_cos+B_proyeccion_1;            
        if (detectado_cero_B)
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          diferencia_neg<='0;
          if ((contador_4_ciclosB == ciclos+2) && (contador_4_ciclosA == ciclos+3) )
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;            
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
            //contador_4_ciclosA<='0;
          end
        end

        if (detectado_cero_A)
        begin
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosA==ciclos+2) && (contador_4_ciclosB==ciclos+3)) //esto obliga a dividir por 4 los desfases
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;            
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
            //contador_4_ciclosA<='0;
          end
          if (contador_4_ciclosA == ciclos)
          begin
           // temporal=-(diferencia_neg*incrementado*360);
            temporal=-diferencia_neg;
          end

        end
        if ((detectado_cero_B) && (detectado_cero_A))
        begin
          contador_4_ciclosB<=contador_4_ciclosB+1;
          contador_4_ciclosA<=contador_4_ciclosA+1;
          if ((contador_4_ciclosB == ciclos+2) && (contador_4_ciclosA == ciclos+2))
          begin
            state2<=S0;
            fin2<=1'b1;
            MODULOA_pre<=(MODULO_POSA-MODULO_NEGA)>>>2;
            MODULOB_pre<=(MODULO_POSB-MODULO_NEGB)>>>2;
            
            A_proyeccion_0_def<=A_proyeccion_0;
            A_proyeccion_1_def<=A_proyeccion_1;
            B_proyeccion_0_def<=B_proyeccion_0;
            B_proyeccion_1_def<=B_proyeccion_1;            
            //MODULO<=(((MODULO_POSA-MODULO_NEGA)/(MODULO_POSB-MODULO_NEGB))- 1)*1000;
            PHASE_PRE<=(temporal);
            //contador_4_ciclosB<='0;
          end
        end
      end






    endcase

  end


  logic [31:0] cociente;
  logic findiv;
  logic finarctan;
  logic [31:0] fasea;
  logic [31:0] faseb;
  
  logic pulso_fases, pulso_fases_reg,pulsito;


  Divisor_Alg2 #(.tamanyo(32))
               divisor_m
               (
                 .CLK(clk125),
                 .RSTa(areset_n),
                 .Start(fin2),

                 .Num(MODULOA_pre*shunt),
                 .Den(MODULOB_pre),

                 .Coc(cociente),
                 .Res(),
                 .Done(findiv)

               );
 /*              
  Divisor_Alg2 #(.tamanyo(32))
               divisor_fa
               (
                 .CLK(clk125),
                 .RSTa(areset_n),
                 .Start(fin2),

                 .Num(A_proyeccion_1_def<<16),
                 .Den(A_proyeccion_0_def),

                 .Coc(fasea),
                 .Res(),
                 .Done(finarca)

               );
 Divisor_Alg2 #(.tamanyo(32))
               divisor_fb
               (
                 .CLK(clk125),
                 .RSTa(areset_n),
                 .Start(fin2),

                 .Num(B_proyeccion_1_def<<16),
                 .Den(B_proyeccion_0_def),

                 .Coc(faseb),
                 .Res(),
                 .Done(finarcb)

               );             
               
*/
    

  fifo_un_fichero #(.LENGTH(32), .SIZE(8))  FIFO_M (.CLOCK(clk125),
                  .RESET_N(areset_n),
                  .DATA_IN(address_mem-1),
                  .READ(findiv),
                  .WRITE(fin2),
                  .CLEAR_N(1'b1),
                  .F_FULL_N(),
                  .F_EMPTY_N(),
                  .USE_DW(),
                  .DATA_OUT(address_mem2));
                  
  fifo_un_fichero #(.LENGTH(32), .SIZE(8))  FIFO_Pa (.CLOCK(clk125),
                  .RESET_N(areset_n),
                  .DATA_IN(address_mem-1),
                  .READ(finarctan),
                 // .READ(pulsito),
                  .WRITE(fin2),
                  .CLEAR_N(1'b1),
                  .F_FULL_N(),
                  .F_EMPTY_N(),
                  .USE_DW(),
                  .DATA_OUT(address_mem3));
              
  
  
  //si tuviera más área podria impementar el arco tangente
                  
  /*
  fifo_un_fichero #(.LENGTH(32), .SIZE(8))  FIFO_P (.CLOCK(clk125),
                  .RESET_N(areset_n),
                  .DATA_IN(address_mem-1),
                  .READ(finarctan),
                  .WRITE(fin2),
                  .CLEAR_N(1'b1),
                  .F_FULL_N(),
                  .F_EMPTY_N(),
                  .USE_DW(),
                  .DATA_OUT(address_mem3));
 */                
cordic_def ARCTANH_A      
(  
  .aclk(clk125),              // input wire aclk
  .aresetn(areset_n),                                  // input wire aresetn
  .s_axis_cartesian_tvalid(fin2),  // input wire s_axis_cartesian_tvalid
  .s_axis_cartesian_tdata({A_proyeccion_1_def,A_proyeccion_0_def}),    // input wire [31 : 0] s_axis_cartesian_tdata
//  .s_axis_cartesian_tready(s_axis_cartesian_tready),   
  .m_axis_dout_tvalid(finarctan),            // output wire m_axis_dout_tvalid
  .m_axis_dout_tdata(fasea)              // output wire [15 : 0] m_axis_dout_tdata
);                  

cordic_def ARCTANH_B      
(  
  .aclk(clk125),              // input wire aclk
  .aresetn(areset_n),                                  // input wire aresetn
  .s_axis_cartesian_tvalid(fin2),  // input wire s_axis_cartesian_tvalid
  .s_axis_cartesian_tdata({B_proyeccion_1_def,B_proyeccion_0_def}),    // input wire [31 : 0] s_axis_cartesian_tdata
 // .s_axis_cartesian_tready(s_axis_cartesian_tready),   
  // .m_axis_dout_tvalid(),            // output wire m_axis_dout_tvalid
  .m_axis_dout_tdata(faseb)              // output wire [15 : 0] m_axis_dout_tdata
);  


  always_ff@(posedge clk125 or negedge areset_n)

    if(!areset_n)
	begin
      //		MODULO<='0;
		PHASE<='0;
	end
    else
    begin
      VALID_P<=finarctan;
      if (finarctan)
      begin
        //MODULO<=cociente-shunt;
        // MODULO<=MODULOA_pre;
        // PHASE <=MODULOB_pre;
        PHASE <=fasea-faseb;        
      end
    end    

  always_ff@(posedge clk125 or negedge areset_n)

    if(!areset_n)
	begin
      		MODULO<='0;
		//PHASE<='0;

	end
    else
    begin
      VALID_M<=findiv;
      if (findiv)
      begin
        MODULO<=cociente-shunt;

        //PHASE <=PHASE_PRE; 
    
      end
    end
    

/*
  always_ff@(posedge clk125 or negedge areset_n)

    if(!areset_n)
	begin
   		pulso_fases<=1'b0;
   		pulso_fases_reg<=1'b0;
		PHASEA<='0;
		PHASEB<='0;
		pulsito<=1'b0;
	end
    else
    begin
      pulso_fases<= (pulso_fases|finarca|finarcb)&(!finarca)& (!finarcb);
      pulso_fases_reg<=pulso_fases;
      pulsito<=(pulso_fases==1'b0)&(&pulso_fases_reg==1'b1);
      VALID_P<=pulsito;
      if (pulsito)
      begin
        PHASEB<=faseb;
        PHASEA<=fasea;
      end
    end
*/

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
                       .fcos_o    (DAC_A_cos),
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

  assign incrementado = rom[address_mem]; //puro combinacional
  assign estado_pasos_cero= test1? state2: state1;


endmodule


