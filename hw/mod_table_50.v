// -----------------------------------------------------------------------------
// mod_table_50.v
// Returns a 50-bit modulus (in 64b container) and its Montgomery n0' constant.
// n0' = -mod^{-1} mod 2^64  (mod is odd < 2^50)
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module mod_table_50 (
    input  wire [5:0]  id,            // 0..32
    output reg  [63:0] modulus,       // use [49:0] in your datapath
    output reg  [63:0] modulus_inv    // Montgomery n0' for 64-bit radix
);

  always @* begin
    case (id)
      6'd0 : begin modulus=64'h000221B97B9E1E53; modulus_inv=64'h48C8F70AACA42A25; end
      6'd1 : begin modulus=64'h00024702F355DA01; modulus_inv=64'hE310FFBE1DB1D9FF; end
      6'd2 : begin modulus=64'h0002485C2DD60489; modulus_inv=64'h4D0F4384F76B4E47; end
      6'd3 : begin modulus=64'h0002579051511D75; modulus_inv=64'hB3AD12310ED8F523; end
      6'd4 : begin modulus=64'h00028301EEB7D483; modulus_inv=64'hBB2E9CA3FBD1E5D5; end
      6'd5 : begin modulus=64'h0002A0B5C0B07F71; modulus_inv=64'h9C604E206B619E6F; end
      6'd6 : begin modulus=64'h0002B1E63E00F6B1; modulus_inv=64'hF589025808AE6DAF; end
      6'd7 : begin modulus=64'h0002D0F8E3F4C7BF; modulus_inv=64'h89D395F2BC4CD7C1; end
      6'd8 : begin modulus=64'h0002E0A8F2C4E2E3; modulus_inv=64'h69BDE206A7828D35; end
      6'd9 : begin modulus=64'h0002E3B3B5A6A0E3; modulus_inv=64'hCADC2D7B02705B35; end
      6'd10: begin modulus=64'h0002E9E2C2E7F4EF; modulus_inv=64'h7B1F7286B74245F1; end
      6'd11: begin modulus=64'h00031E3A2F7B0B9D; modulus_inv=64'hB7C54CB57FBD2D4B; end
      6'd12: begin modulus=64'h000323B4B7B2E0B1; modulus_inv=64'h420F8BC8993097AF; end
      6'd13: begin modulus=64'h000336A8A9B1C2E1; modulus_inv=64'h958873E2744CFEDF; end
      6'd14: begin modulus=64'h00033B8C4B3F7A11; modulus_inv=64'hDFC0AF4224E9490F; end
      6'd15: begin modulus=64'h00033F9E3B9A4C37; modulus_inv=64'hB9EA08FAD484D679; end
      6'd16: begin modulus=64'h000342B0E6B9D7B7; modulus_inv=64'hDD362B725B1649F9; end
      6'd17: begin modulus=64'h000345B7D1A1E8C3; modulus_inv=64'hA7329B51CF29F815; end
      6'd18: begin modulus=64'h00034C41A0F9D4A7; modulus_inv=64'hE75A4E47B3C16CE9; end
      6'd19: begin modulus=64'h0003531B2E5A0C41; modulus_inv=64'hAF0FEA891E07FC3F; end
      6'd20: begin modulus=64'h00035A1F4C27B7D9; modulus_inv=64'hE1DCBA1A4644A797; end
      6'd21: begin modulus=64'h00035C9AD4E1B0E7; modulus_inv=64'h5B5CDB30BA1B9D29; end
      6'd22: begin modulus=64'h0003630E0B9D7C4D; modulus_inv=64'h53D2A4471911E37B; end
      6'd23: begin modulus=64'h00036A9F3B21E5B5; modulus_inv=64'h81F9FF769ECE5F63; end
      6'd24: begin modulus=64'h00036D01F0C2B8D1; modulus_inv=64'h898DE1BB6E475FCF; end
      6'd25: begin modulus=64'h000372E4B19FA06B; modulus_inv=64'hE183A9FB8BE3F3BD; end
      6'd26: begin modulus=64'h000378A95B0E6C61; modulus_inv=64'hE1BD0DA2433AC85F; end
      6'd27: begin modulus=64'h00037D2E9C51F0E7; modulus_inv=64'h7C3CC7AB94AFDD29; end
      6'd28: begin modulus=64'h0003B0E88C8B9A9B; modulus_inv=64'h83DD18633B5A446D; end
      6'd29: begin modulus=64'h0003C0BDE2C7A7A1; modulus_inv=64'h7C368FD95208039F; end
      6'd30: begin modulus=64'h0003D2A3F1E5D54D; modulus_inv=64'h5920B72FBB4A947B; end
      6'd31: begin modulus=64'h0003E18B4D3D3753; modulus_inv=64'h364CAEE82D81DB25; end
      6'd32: begin modulus=64'h0003E61FB278B617; modulus_inv=64'h3EFFB113481E1E59; end
      default: begin modulus=64'd0; modulus_inv=64'd0; end
    endcase
  end

endmodule
