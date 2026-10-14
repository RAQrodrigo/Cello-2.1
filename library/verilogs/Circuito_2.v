module circuit(output reg X, input A, B);
  always @(A, B)
  begin
    case ({A, B})
      2'b00: {X} = 1'b1;
      2'b01: {X} = 1'b0;
      2'b10: {X} = 1'b0;
      2'b11: {X} = 1'b1;
    endcase
  end
endmodule