`timescale 1ns / 1ps
//Description: register with enable
module nonce_reg
  import uart_pkg::*;
(
    input  logic         clock_i,   //main clock
    input  logic         resetb_i,  //asynchronous reset active low
    input  logic [  7:0] data_i,
    input  logic         en_i,
    input  logic         init_i,
    output logic [127:0] nonce_o    //Nonce register storing half byte by the right hand side.
);
  logic [127:0] nonce_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) nonce_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          nonce_s <= '0;
        end else begin
          nonce_s <= {nonce_s[119:0], data_i};
        end
      end else begin
        nonce_s <= nonce_s;
      end
    end
  end : seq_0
  assign nonce_o = nonce_s;

endmodule : nonce_reg
