`timescale 1ns/1ps
import ascon_pack::*;

module ascon_top (
  // Horloge & reset
  input  logic         clk_i,
  input  logic         rst_n_i,
  // On reçoit juste un start pour lancer la séquence
  input  logic         start_i,
  // Clé et nonce fournis de l'extérieur
  input  logic [127:0] key_i,
  input  logic [127:0] nonce_i,
  input  logic [63:0]  data_i,
  // Sorties
  output logic [4:0]     decalage_o,
  output logic [63:0]  cipher_o,
  output logic [127:0] tag_o,
  output logic         done_o,
  output logic init_cipher_valid_o,
  output logic init_o
  
);

  // --------------------------------------------------------------------------
  // Signaux internes connectés à la FSM
  // --------------------------------------------------------------------------
  logic init_s;
  logic associate_s;
  logic final_s;
  logic data_valid_s;
  logic end_init_s;
  logic end_assoc_s;
  logic end_cipher_s;
  logic end_tag_s;
  logic cipher_valid_s;
  logic init_cipher_valid_s;
  logic [4:0] decalage_s;
  logic en_count_s;
  logic init_count_s;
  assign init_cipher_valid_o=init_cipher_valid_s;
  // --------------------------------------------------------------------------
  // Instanciation de la FSM
  // --------------------------------------------------------------------------
  FSM_ascon u_fsm (
    .clk_i               (clk_i),
    .rst_n_i             (rst_n_i),
    .start_i             (start_i),
    

    // Signaux de fin venant de ascon.sv
    .end_initialisation_i(end_init_s),
    .end_associate_i     (end_assoc_s),
    .end_cipher_i        (end_cipher_s),
    .end_tag_i           (end_tag_s),
    .cipher_valid_i      (cipher_valid_s),
    .decalage_i(decalage_s),
    
    // Vers ascon.sv
    .init_o              (init_s),
    .associate_o         (associate_s),
    .final_o             (final_s),
    .data_valid_o        (data_valid_s),
    .en_count_o(en_count_s),
    .init_count_o(init_count_s),
    
    .init_cipher_valid_o(init_cipher_valid_s),

    // Signal global de fin
    .done_o              (done_o)
  );

  // --------------------------------------------------------------------------
  // Instanciation de ascon.sv (non modifié)
  // --------------------------------------------------------------------------
  ascon u_ascon (
    .clock_i              (clk_i),
    .reset_i              (~rst_n_i),  // si reset actif bas
    .init_i               (init_s),
    .associate_data_i     (associate_s),
    .finalisation_i       (final_s),
    .data_i               (data_i),
    .data_valid_i         (data_valid_s),
    .key_i                (key_i),
    .nonce_i              (nonce_i),

    // Sorties
    .end_associate_o      (end_assoc_s),
    .cipher_o             (cipher_o),
    .cipher_valid_o       (cipher_valid_s),
    .tag_o                (tag_o),
    .end_tag_o            (end_tag_s),
    .end_initialisation_o (end_init_s),
    .end_cipher_o         (end_cipher_s)
  );
  
  

compteur_simple_init compteur_simple
   (
    .clock_i(clk_i),
    .resetb_i(rst_n_i),
    .en_i(en_count_s),
    .init_a_i(init_count_s),
    .cpt_o(decalage_s)      
    ) ;


  // Exemple de branchement pour `decalage_o`
  assign decalage_o = decalage_s;
  assign init_o=init_s;
  // Ici, si nécessaire, on peut faire :
  // assign data_s = data_i;
  // ou relier data_s à un buffer / mémoire interne.

endmodule