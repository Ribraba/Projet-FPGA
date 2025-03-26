`timescale 1ns / 1ps
//Description: register with enable
module ascon_reg (
    input logic clock_i,  //main clock
    input logic resetb_i,  //asynchronous reset active low
    input logic [63:0] data_i,
    input logic en_i,
    input logic init_i,
    output logic [1471:0] wave_o     //wave register storing 8 bytes by the right hand side. (23*64bits)
);
  logic [1471:0] wave_s;  //1767

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) wave_s <= '0;
    else begin
      if (en_i == 1'b1) begin
        if (init_i == 1'b1) begin
          wave_s <= '0;
        end else begin
          wave_s <= {wave_s[1407:0], data_i};  //1763
        end
      end else begin
        wave_s <= wave_s;
      end
    end
  end : seq_0
  assign wave_o = wave_s;

endmodule : ascon_reg
