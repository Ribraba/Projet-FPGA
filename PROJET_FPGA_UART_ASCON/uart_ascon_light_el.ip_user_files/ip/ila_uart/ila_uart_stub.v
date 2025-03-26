// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.1 (win64) Build 5076996 Wed May 22 18:37:14 MDT 2024
// Date        : Mon Mar 24 15:54:29 2025
// Host        : GCP-E105-22 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub
//               c:/Users/eleves/Desktop/FINALLLL/FPGA_Emilie_uart_ascon_light_el_test/uart_ascon_light_el.gen/sources_1/ip/ila_uart/ila_uart_stub.v
// Design      : ila_uart
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg400-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* X_CORE_INFO = "ila,Vivado 2024.1" *)
module ila_uart(clk, probe0, probe1, probe2, probe3, probe4, probe5)
/* synthesis syn_black_box black_box_pad_pin="probe0[319:0],probe1[0:0],probe2[3:0],probe3[319:0],probe4[127:0],probe5[0:0]" */
/* synthesis syn_force_seq_prim="clk" */;
  input clk /* synthesis syn_isclock = 1 */;
  input [319:0]probe0;
  input [0:0]probe1;
  input [3:0]probe2;
  input [319:0]probe3;
  input [127:0]probe4;
  input [0:0]probe5;
endmodule
