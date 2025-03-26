`timescale 1ns/1ps
import ascon_pack::*;

module ascon_top_tb ();

  localparam int NB_BLOCKS = 23;

  // Horloge & reset
  logic         clk_s=1'b0;
  logic         rst_n_s;
  // On reçoit juste un start pour lancer la séquence
  logic         start_s;
  // Clé et nonce fournis de l'extérieur
  logic [127:0] key_s;
  logic [127:0] nonce_s;
  logic [63:0] data_s;
  logic [63:0] data_associee_s;
  logic [63:0] plaintext_blocks_s [0:NB_BLOCKS];
  // Sorties
  logic [63:0]  cipher_s;
  logic [127:0] tag_s;
  logic [5:0] decalage_s;
  logic         done_s;
  
  // ===========================================================================
  // Instanciation du DUT 
  // ===========================================================================
  ascon_top DUT (
    // Horloge & reset
    .clk_i(clk_s),
    .rst_n_i(rst_n_s),
    // On reçoit juste un start pour lancer la séquence
    .start_i(start_s),
    // Clé et nonce fournis de l'extérieur
    .key_i(key_s),
    .nonce_i(nonce_s),
    .data_i(data_s),
    // Sorties
    .decalage_o(decalage_s),
    .cipher_o(cipher_s),
    .tag_o(tag_s),

    .done_o(done_s)
  );
  
  initial begin
    plaintext_blocks_s[0]  = 64'h4120746F20428000; //AD
    plaintext_blocks_s[1]  = 64'h5A5B5B5A5A5A5A5A;
    plaintext_blocks_s[2]  = 64'h59554E4A4C4F5455;
    plaintext_blocks_s[3]  = 64'h5351535456575857;
    plaintext_blocks_s[4]  = 64'h5A5A595756595B5A;
    plaintext_blocks_s[5]  = 64'h5554545252504F4F;
    plaintext_blocks_s[6]  = 64'h4C4C4D4D4A494444;
    plaintext_blocks_s[7]  = 64'h4747464442434140;
    plaintext_blocks_s[8]  = 64'h3B36383E44494947;
    plaintext_blocks_s[9]  = 64'h4746464443424345;
    plaintext_blocks_s[10]  = 64'h4745444546474A49;
    plaintext_blocks_s[11] = 64'h4745484F58697C92;
    plaintext_blocks_s[12] = 64'hAECEEDFFFFE3B47C;
    plaintext_blocks_s[13] = 64'h471600041729363C;
    plaintext_blocks_s[14] = 64'h3F3E40414141403F;
    plaintext_blocks_s[15] = 64'h3F403F3E3B3A3B3E;
    plaintext_blocks_s[16] = 64'h3D3E3C393C414646;
    plaintext_blocks_s[17] = 64'h46454447464A4C4F;
    plaintext_blocks_s[18] = 64'h4C505555524F5155;
    plaintext_blocks_s[19] = 64'h595C5A595A5C5C5B;
    plaintext_blocks_s[20] = 64'h5959575351504F4F;
    plaintext_blocks_s[21] = 64'h53575A5C5A5B5D5E;
    plaintext_blocks_s[22] = 64'h6060615F605F5E5A;
    // Dernier bloc partiel (index 22):  "5857545252" + "000000"
    plaintext_blocks_s[23] = 64'h5857545252800000;
  end

  // ===========================================================================
  // Génération d'horloge
  // ===========================================================================
  always #10 clk_s = ~clk_s;
  
  initial begin
    start_s=1'b0;
    key_s=128'h8a55114d1cb6a9a2be263d4d7aecaaff;
    nonce_s=128'h4ed0ec0b98c529b7c8cddf37bcd0284a;
    data_s=64'h0;
    data_associee_s=64'h4120746F20428000;//data_s=A1={A,0x8000}
    rst_n_s=1'b0;
    // Sortie du reset
    #2;
    rst_n_s = 1'b1; 
    #18; 
   
    start_s=1'b1;
    #350;
   
  end

assign data_s=plaintext_blocks_s[decalage_s];

endmodule : ascon_top_tb
