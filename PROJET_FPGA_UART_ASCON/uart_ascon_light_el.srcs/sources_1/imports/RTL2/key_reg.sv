`timescale 1ns / 1ps
//Description: register with enable
module key_reg
  import uart_pkg::*;
(
    input  logic         clock_i,   //main clock
    input  logic         resetb_i,  //asynchronous reset active low
    input  logic [  7:0] data_i,
    input  logic         en_i,
    input  logic         init_i,
    output logic [127:0] key_o      //Key register storing byte by the right hand side.
);
  logic [127:0] key_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) key_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          key_s <= '0;
        end else begin
          key_s <= {key_s[119:0], data_i};
        end
      end else begin
        key_s <= key_s;
      end
    end
  end : seq_0
  assign key_o = key_s;

endmodule : key_reg
