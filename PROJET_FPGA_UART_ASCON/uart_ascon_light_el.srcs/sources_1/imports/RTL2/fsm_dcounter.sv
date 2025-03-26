`timescale 1ns / 1ps
//Description: counter for storing or flushing data to uart
module fsm_dcounter
  import uart_pkg::*;
(
    input  logic       clock_i,      //main clock
    input  logic       resetb_i,     //asynchronous reset active low
    input  logic       en_i,
    input  logic       init_c8_i,   //storing AD (6O+2o de padding)
    input  logic       init_c17_i,   //flushing tag (16o+1)
    input  logic       init_c16_i,   //storing key or nonce
    input  logic       init_c185_i,  //flushing cipher (184 o +1)
    input  logic       init_c184_i,  //storing wave (181+3o de padding)
    output logic [8:0] cpt_o
);
  logic [8:0] cpt_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin : seq_0
    if (resetb_i == 1'b0) cpt_s <= '1;
    else begin
      if (en_i == 1'b1) begin
        if (init_c8_i == 1'b1) begin
          cpt_s <= 9'd8;  //8
        end else begin
          if (init_c17_i == 1'b1) begin
            cpt_s <= 9'd17;
          end else begin
            if (init_c16_i == 1'b1) begin
              cpt_s <= 9'd16;  //16
            end else begin
              if (init_c185_i == 1'b1) begin
                cpt_s <= 9'd185;
              end else begin
                if (init_c184_i == 1'b1) begin
                  cpt_s <= 9'd184;  //184
                end else begin
                  cpt_s <= cpt_s - 1;
                end
              end
            end
          end
        end
      end else begin
        cpt_s <= cpt_s;
      end
    end
  end : seq_0
  assign cpt_o = cpt_s;

endmodule : fsm_dcounter
