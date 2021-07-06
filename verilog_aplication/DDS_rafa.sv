module DDS_rafa (
          input [31:0] phi_inc_i,
          input reset_n,
          input clken,
          output [13:0] fsin_o,
          output [13:0] fcos_o,
          output logic out_valid,
          input clk
          );

logic [31:0] accu;
logic valid;
logic [15:0] addr1,addr2;
logic [13:0] q1,q2;


always_ff @(posedge clk , negedge reset_n)
if (!reset_n)

    begin
        accu<='0;
        valid<=1'b0;
        out_valid<=1'b0;
    end
else
    begin
        accu<=accu+phi_inc_i;
        valid<=clken;
        out_valid<=valid;
    end




	assign addr1=accu[31:16]; //seno
    assign addr2=addr1+16*1024;  //coseno   
//para coseno 
//assign addr=punt_fijo_divid_pi[46]?punt_fijo_divid_pi[45:36]:(1023-punt_fijo_divid_pi[45:36]);  /
memoria_dual_port #(.DATA_WIDTH(14),.ADDR_WIDTH(16), .FICHERO_INICIAL("sin_total2.dat"))  my_memory_sin_cos  //forma parte del ciclo 2
						(   
                              .addr1(addr1),
                              .addr2(addr2),
                              .clk(clk),
			                  .enable(1'b1),
                              .q1(q1), //seno
                              .q2(q2)  //coseno
                              );
                            
                         
							
assign	fsin_o=clken?q1:'0	;
assign	fcos_o=clken?q2:'0	;							
  
 
endmodule
