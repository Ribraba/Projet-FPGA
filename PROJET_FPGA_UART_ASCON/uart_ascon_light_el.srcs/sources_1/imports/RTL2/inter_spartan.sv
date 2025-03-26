`timescale 1ns / 1ps

module inter_spartan
  import uart_pkg::*;
(
    input  logic       clock_i,  //main clock
    input  logic       reset_i,  //asynchronous reset active low
    input  logic       Rx_i,     //RX to RS232
    input  logic [2:0] Baud_i,   //baud selection
    output logic       Tx_o,     //Tx to RS 232
    output logic [2:0] Baud_o,
    output logic       RTS_o
);

  logic RXErr_s;
  logic RXRdy_s;
  logic TxBusy_s;
  logic rdata_ld_s;
  logic [NDBits-1:0] rdata_s;
  logic [NDBits-1:0] Dout_s;
  logic clock_s;
  logic resetb_s;

  assign Baud_o   = ~Baud_i;
  assign resetb_s = ~reset_i;
  assign RTS_o    = RXRdy_s;  //from Nathan improve UART behavior (pin 1sur USB SERIAL)

  //internal signals for UART part
  logic [127:0] tag_s;
  logic [1471:0] wave_to_send_s;
  logic cipherRdy_s;
  logic [127:0] key_s;
  logic [127:0] nonce_s;
  logic [63:0] ad_s;
  logic [1471:0] wave_received_s;
  logic start_ascon_s;
  logic init_cpt_mux_s;
  logic en_cpt_mux_s;
  logic en_reg_ascon_s;
  logic cipher_valid_s;
  //internal signals for Ascon part
  //signals
  logic associate_data_s;
  logic finalisation_s;
  logic data_valid_s;
  logic end_associate_s;
  logic end_tag_s;
  logic end_initialisation_s;
  logic end_cipher_s;
  logic locked_s;

  //mux for injected data in ascon
  logic [63:0] data_s, cipher_s;
  logic [4:0] cpt_s;  //cpt 5 bits
  logic [0:23][63:0] wave_s;  //1472
  //logic [0:22][63:0] wave_o_s;  //1472+64 packed

  clk_wiz_0 clock_converter
   (
    // Clock out ports
    .clk_out1(clock_s),     // output clk_out1
    // Status and control signals
    .reset(reset_i), // input reset
    .locked(locked_s),       // output locked
   // Clock in ports
    .clk_in1(clock_i)      // input clk_in1
);

  uart_core uart_core_0 (
      .clock_i(clock_s),
      .resetb_i(resetb_s),
      .Din_i(rdata_s),
      .LD_i(rdata_ld_s),
      .Rx_i(Rx_i),
      .Baud_i(Baud_i),
      .RXErr_o(RXErr_s),
      .RXRdy_o(RXRdy_s),
      .Dout_o(Dout_s),
      .Tx_o(Tx_o),
      .TxBusy_o(TxBusy_s)
  );

  fsm_uart fsm_uart_0 (
      .clock_i(clock_s),
      .resetb_i(resetb_s),
      .RXErr_i(RXErr_s),
      .RXRdy_i(RXRdy_s),
      .TxBusy_i(TxBusy_s),
      .RxData_i(Dout_s),
      .Tag_i(tag_s),
      .Cipher_i(wave_to_send_s),
      .CipherRdy_i(end_tag_s),
      .TxByte_o(rdata_s),
      .Key_o(key_s),
      .Nonce_o(nonce_s),
      .Ad_o(ad_s),
      .Wave_o(wave_received_s),
      .Start_ascon_o(start_ascon_s),
      .Load_o(rdata_ld_s)
  );

  //instance de ascon
  
 ascon_top ascon_top_0 (
  // Horloge & reset
  .clk_i(clock_s),
  .rst_n_i(resetb_s),
  // On reçoit juste un start pour lancer la séquence
  .start_i(start_ascon_s),
  // Clé et nonce fournis de l'extérieur
  .key_i(key_s),
  .nonce_i(nonce_s),
  .data_i(data_s),
  // Sorties
  .decalage_o(cpt_s),
  .cipher_o(cipher_s),
  .tag_o(tag_s),
  .done_o(end_tag_s),
  .init_cipher_valid_o(en_reg_ascon_s),
  .init_o(init_cpt_mux_s)
  
);


//instanciate drive ascon here
  

  //counter to select the correct word from wavereceived and drive it to data_s
 
 
 //wave_s concatenate ad and wave received
  assign wave_s[0]  = ad_s;
  assign wave_s[1]  = wave_received_s[1471:1408];
  assign wave_s[2]  = wave_received_s[1407:1344];
  assign wave_s[3]  = wave_received_s[1343:1280];
  assign wave_s[4]  = wave_received_s[1279:1216];
  assign wave_s[5]  = wave_received_s[1215:1152];
  assign wave_s[6]  = wave_received_s[1151:1088];
  assign wave_s[7]  = wave_received_s[1087:1024];
  assign wave_s[8]  = wave_received_s[1023:960];
  assign wave_s[9]  = wave_received_s[959:896];
  assign wave_s[10] = wave_received_s[895:832];
  assign wave_s[11] = wave_received_s[831:768];
  assign wave_s[12] = wave_received_s[767:704];
  assign wave_s[13] = wave_received_s[703:640];
  assign wave_s[14] = wave_received_s[639:576];
  assign wave_s[15] = wave_received_s[575:512];
  assign wave_s[16] = wave_received_s[511:448];
  assign wave_s[17] = wave_received_s[447:384];
  assign wave_s[18] = wave_received_s[383:320];
  assign wave_s[19] = wave_received_s[319:256];
  assign wave_s[20] = wave_received_s[255:192];
  assign wave_s[21] = wave_received_s[191:128];
  assign wave_s[22] = wave_received_s[127:64];
  assign wave_s[23] = wave_received_s[63:0];

  
//  
  assign data_s     = wave_s[cpt_s];

//register to store cipher result 8 bytes
  ascon_reg u_ascon_reg (
      .clock_i (clock_s),
      //main clock
      .resetb_i(resetb_s),
      //asynchronous reset active low
      .data_i  (cipher_s),
      .en_i    (en_reg_ascon_s),
      .init_i  (init_cpt_mux_s),
      //wave register storing 8 bytes by the right hand side. (23*64bits)
      .wave_o  (wave_to_send_s)   //wave_o_s
  );
  
endmodule : inter_spartan
