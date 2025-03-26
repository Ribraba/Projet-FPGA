package uart_pkg;
  localparam even = 1'b0;  //parity type
                           //1'b0 = even
                           //1'b1 = odd
  localparam parity = 1'b0;  //1'b0 no parity
                             //1'b1 with parity
                             //enable parity
  // const logic NDBits = 8;  //number of data bits
  localparam NDBits = 8;
  localparam debug = 1'b0;  //debug constant

endpackage : uart_pkg
