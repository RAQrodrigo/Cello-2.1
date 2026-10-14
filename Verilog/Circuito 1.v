module circuit(output reg X, input A, B, C);
  always @(A, B, C)
  begin
    case ({A, B, C})
      3'b000: {X} = 1'b0;
      3'b001: {X} = 1'b1;
      3'b010: {X} = 1'b0;
      3'b011: {X} = 1'b0;
      3'b100: {X} = 1'b0;
      3'b101: {X} = 1'b0;
      3'b110: {X} = 1'b0;
      3'b111: {X} = 1'b0;
    endcase
  end
endmodule