`timescale 1ns / 1ps
//Description: register with enable
module cipher_reg
  import uart_pkg::*;
(
    input  logic          clock_i,   //main clock
    input  logic          resetb_i,  //asynchronous reset active low
    input  logic [1471:0] cipher_i,
    input  logic          en_i,
    input  logic          init_i,
    output logic [   7:0] data_o     //cipher register exit byte by the left hand side.
);
  logic [1471:0] cipher_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) cipher_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          cipher_s <= cipher_i;
        end else begin
          cipher_s <= {cipher_s[1463:0], 8'h0};
        end
      end else begin
        cipher_s <= cipher_s;
      end
    end
  end : seq_0
  assign data_o = cipher_s[1471:1464];

endmodule : cipher_reg
