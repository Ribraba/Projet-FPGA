-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.1 (win64) Build 5076996 Wed May 22 18:37:14 MDT 2024
-- Date        : Mon Mar 24 15:54:29 2025
-- Host        : GCP-E105-22 running 64-bit major release  (build 9200)
-- Command     : write_vhdl -force -mode synth_stub
--               c:/Users/eleves/Desktop/FINALLLL/FPGA_Emilie_uart_ascon_light_el_test/uart_ascon_light_el.gen/sources_1/ip/ila_uart/ila_uart_stub.vhdl
-- Design      : ila_uart
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg400-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ila_uart is
  Port ( 
    clk : in STD_LOGIC;
    probe0 : in STD_LOGIC_VECTOR ( 319 downto 0 );
    probe1 : in STD_LOGIC_VECTOR ( 0 to 0 );
    probe2 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    probe3 : in STD_LOGIC_VECTOR ( 319 downto 0 );
    probe4 : in STD_LOGIC_VECTOR ( 127 downto 0 );
    probe5 : in STD_LOGIC_VECTOR ( 0 to 0 )
  );

end ila_uart;

architecture stub of ila_uart is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "clk,probe0[319:0],probe1[0:0],probe2[3:0],probe3[319:0],probe4[127:0],probe5[0:0]";
attribute X_CORE_INFO : string;
attribute X_CORE_INFO of stub : architecture is "ila,Vivado 2024.1";
begin
end;
