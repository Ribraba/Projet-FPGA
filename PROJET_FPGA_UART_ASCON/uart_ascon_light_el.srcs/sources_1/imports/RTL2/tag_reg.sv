`timescale 1ns / 1ps
//Description: register with enable
module tag_reg
  import uart_pkg::*;
(
    input  logic         clock_i,   //main clock
    input  logic         resetb_i,  //asynchronous reset active low
    input  logic [127:0] tag_i,
    input  logic         en_i,
    input  logic         init_i,
    output logic [  7:0] data_o     //tag register exit byte by the left hand side.
);
  logic [127:0] tag_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) tag_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          tag_s <= tag_i;
        end else begin
          tag_s <= {tag_s[119:0], 8'h0};
        end
      end else begin
        tag_s <= tag_s;
      end
    end
  end : seq_0
  assign data_o = tag_s[127:120];

endmodule : tag_reg
