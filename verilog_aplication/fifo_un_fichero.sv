//
// Verilog Module tarea1_2020_lib.fifo_un_fichero
//
// Created:
//          by - rgadea.UNKNOWN (HYPERION7)
//          at - 11:46:36 14/05/2020
//
// using Mentor Graphics HDL Designer(TM) 2019.4 (Build 4)
//

`resetall
`timescale 1ns/10ps
module fifo_un_fichero 
  
#(parameter LENGTH=32,
  parameter SIZE=8)  
(
input logic [SIZE-1:0] DATA_IN,
input logic READ,
input logic WRITE,
input CLOCK,
input CLEAR_N,
input RESET_N,
output [$clog2(LENGTH-1)-1:0] USE_DW,
output logic F_FULL_N,
output logic F_EMPTY_N,

output logic [SIZE-1:0] DATA_OUT


);
localparam tamano=$clog2(LENGTH-1);
logic [0:LENGTH-1][SIZE-1:0] aux;
logic [tamano-1:0] count ;
assign USE_DW=count;
enum logic [1:0] {vacio,otros,lleno} estado;


always_ff @(posedge CLOCK or negedge RESET_N)
if (!RESET_N)
      begin
        aux<={LENGTH{'0}};
        count<=0;
        estado<=vacio;
        DATA_OUT<='0;
      end
else
  if (CLEAR_N==1'b0)
  begin
        aux<={LENGTH{'0}};
        count<=0;
        estado<=vacio;
        DATA_OUT<='0;
  end
  else
    case (estado)
      vacio:  begin
                case ({READ,WRITE})
                  2'b01:
           
                    begin
                      estado<=otros;
                      count<=count+1;
                      aux<={DATA_IN,aux[0:LENGTH-2]};
                    end              
                  2'b11:
                    begin
                      aux<={DATA_IN,aux[0:LENGTH-2]};
                     DATA_OUT<=DATA_IN;
                    end  
                endcase

              end
      otros:  begin
                case ({READ,WRITE})
                  2'b01:
                    begin
                      if (count==LENGTH-1)
                          estado<=lleno;
                      count<=count+1;
                      aux<={DATA_IN,aux[0:LENGTH-2]};
                    end
                  2'b10:
                    begin
                      if (count==1)
                          estado<=vacio;
                      count<=count-1;
                	    DATA_OUT<=aux[count-1]; 
                    end                
                  2'b11:
                    begin
                      aux<={DATA_IN,aux[0:LENGTH-2]};
                	    DATA_OUT<=aux[count-1]; 
                    end 
                endcase

              end                 
      lleno:  begin
                case ({READ,WRITE})
                  2'b10:
                    begin
                      estado<=otros;
                      count<=count-1;
                	    DATA_OUT<=aux[LENGTH-1]; 
                    end                
                  2'b11:
                    begin
                      aux<={DATA_IN,aux[0:LENGTH-2]};
                	    DATA_OUT<=aux[LENGTH-1]; 
                    end                   
                endcase
 
              end
      endcase                                              


assign F_FULL_N=(estado==lleno)?1'b0:1'b1;
assign F_EMPTY_N=(estado==vacio)?1'b0:1'b1;


// ### Please start your Verilog code here ### 

endmodule
