`timescale 1ns / 1ps
//Description: register with enable
module ad_reg
  import uart_pkg::*;
(
    input  logic        clock_i,   //main clock
    input  logic        resetb_i,  //asynchronous reset active low
    input  logic [ 7:0] data_i,
    input  logic        en_i,
    input  logic        init_i,
    output logic [63:0] ad_o       //ad register storing half byte by the right hand side.
);
  logic [63:0] ad_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) ad_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          ad_s <= '0;
        end else begin
          ad_s <= {ad_s[55:0], data_i};
        end
      end else begin
        ad_s <= ad_s;
      end
    end
  end : seq_0
  assign ad_o = ad_s;

endmodule : ad_reg
