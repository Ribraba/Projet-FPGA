import ascon_pack::*;

module FSM_ascon
(

  // Horloge, reset
  input  logic clk_i,
  input  logic rst_n_i,

  // Déclencheur général
  input  logic start_i,

  // Signaux de fin provenant de ascon.sv
  input  logic end_initialisation_i,
  input  logic end_associate_i,
  input  logic end_cipher_i,
  input  logic end_tag_i,
  input logic cipher_valid_i,
  input logic [4:0] decalage_i,

  // Ordres vers ascon.sv
  output logic init_o,
  output logic associate_o,
  output logic final_o,
  output logic data_valid_o,
  output logic en_count_o,
  output logic init_count_o,
  output logic init_cipher_valid_o,

  // Indicateur de fin générale
  output logic done_o
);

  // --------------------------------------------------------------------------
  // Déclaration des états
  // --------------------------------------------------------------------------
  typedef enum logic [3:0] {
    ST_IDLE,
    ST_INIT,
    ST_WAIT_INIT,
    ST_ASSOC,
    ST_WAIT_ASSOC,
    ST_END_ASSOC,
    ST_CIPHER,
    ST_WAIT_CIPHER,
    ST_END_CIPHER,
    ST_FINAL,
    LAST_WAIT_CIPHER,
    LAST_END_CIPHER,
    ST_WAIT_FINAL,
    ST_DONE
  } fsm_state_e;

  fsm_state_e current_state_s, next_state_s;

  localparam  int NB_BLOCKS = 22;
  logic [4:0] count_s ;
  

  // --------------------------------------------------------------------------
  // Séquentiel : Registre d'état
  // --------------------------------------------------------------------------
  always_ff @(posedge clk_i or negedge rst_n_i) begin
    if (!rst_n_i)
      current_state_s <= ST_IDLE;
    else
      current_state_s <= next_state_s;
  end

  // --------------------------------------------------------------------------
  // Combinatoire : calcul du prochain état
  // --------------------------------------------------------------------------
  always_comb begin
    next_state_s = current_state_s;
    case (current_state_s)
      ST_IDLE: begin
        if (start_i) begin
          next_state_s = ST_INIT;
        end
      end

      ST_INIT: begin
        // On attend que ascon nous signale la fin d'init
        next_state_s = ST_WAIT_INIT;
      end

      ST_WAIT_INIT: begin
        // Un mini-état pour relâcher init et passer à l'association
        if (end_initialisation_i) begin
          next_state_s = ST_ASSOC;
        end
        else begin
            next_state_s=ST_WAIT_INIT;
        end
           
      end

      ST_ASSOC: begin
        next_state_s = ST_WAIT_ASSOC;
      end

      ST_WAIT_ASSOC: begin
        if (end_associate_i) begin
          next_state_s = ST_END_ASSOC;
        end
        else begin
            next_state_s = ST_WAIT_ASSOC;
        end
      end
      ST_END_ASSOC: begin
        next_state_s=ST_CIPHER;
      end

      ST_CIPHER: begin  
        next_state_s = ST_WAIT_CIPHER;
      end

      ST_WAIT_CIPHER: begin
          if (end_cipher_i) begin
            next_state_s = ST_END_CIPHER;
          end
          else begin
            next_state_s = ST_WAIT_CIPHER;
          end
      end
      
      ST_END_CIPHER: begin
        if (decalage_i < NB_BLOCKS) begin
          next_state_s = ST_CIPHER;
        end
        else begin
            next_state_s = ST_FINAL;
        end
      end

      ST_FINAL: begin
        next_state_s = LAST_WAIT_CIPHER;
      end

      LAST_WAIT_CIPHER: begin
        if (end_tag_i) begin
            next_state_s = LAST_END_CIPHER;
        end else begin
            next_state_s = LAST_WAIT_CIPHER;
          end
      end
      
      LAST_END_CIPHER: begin
         next_state_s = ST_WAIT_FINAL;
      end 
      
      ST_WAIT_FINAL: begin
        if (end_tag_i) begin
          next_state_s = ST_DONE;
        end
        else begin 
            next_state_s = ST_WAIT_FINAL;
        end
      end

      ST_DONE: begin
        // On reste en ST_DONE ou on peut retourner en ST_IDLE si on veut
        // relancer plus tard.
        next_state_s = ST_IDLE; // si on veut autoriser un restart
      end

      default: next_state_s = ST_IDLE;
    endcase
  end

  // --------------------------------------------------------------------------
  // Sorties type Moore : pilotées par l'état courant
  // --------------------------------------------------------------------------
  always_comb begin
    // Par défaut, on met tout à 0
    init_o       = 1'b0;
    associate_o  = 1'b0;
    final_o      = 1'b0;
    data_valid_o = 1'b0;
    done_o       = 1'b0;
    init_cipher_valid_o = 1'b0;
    en_count_o =1'b0;
    init_count_o =1'b0;
    
    // En fonction de l'état, on active les sorties voulues
    case (current_state_s)
      // Phase init
      ST_IDLE: begin
      end
      ST_INIT:begin
        en_count_o =1'b1;
        init_count_o =1'b1;
      end

        
      ST_WAIT_INIT: begin
        init_o       = 1'b1;
        init_cipher_valid_o = 1'b1;
      end
      
      // Phase association
      ST_ASSOC: begin
        associate_o  = 1'b1;
        data_valid_o = 1'b1;  // on envoie la data associée
      end
      
      ST_WAIT_ASSOC:begin
      end
      
      ST_END_ASSOC: begin
        en_count_o =1'b1;
      end

      // Phase chiffrement
      ST_CIPHER: begin
        data_valid_o = 1'b1; // on envoie le plaintext
      end
      
      ST_WAIT_CIPHER: begin
      end
      
      ST_END_CIPHER: begin
        en_count_o =1'b1; // on envoie le plaintext
        init_cipher_valid_o=1'b1;
      end

      // Phase final
      ST_FINAL: begin
        final_o      = 1'b1;
        data_valid_o = 1'b1; // envoi d'un dernier bloc, selon ascon_tb
      end
      
      LAST_WAIT_CIPHER: begin
      end
      
      LAST_END_CIPHER: begin
        //en_count_o =1'b1; // on envoie le plaintext
        init_cipher_valid_o=1'b1;
      end

      ST_WAIT_FINAL: begin
      end

      // État final
      ST_DONE: begin
        done_o = 1'b1;
      end
      // Les autres états = tout par défaut
    endcase
  end

endmodule : FSM_ascon
