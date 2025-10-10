// -----------------------------------------------------------------------------
// compute_array.v
// Compute array with 256 modular adders and multipliers (Verilog-2001)
// - Per-lane limb_id selects modulus & Montgomery n0' via mod_table_50
// - Flattened bus interfaces for portability
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module compute_array #(
    parameter integer DATA_WIDTH = 50,
    parameter integer ARRAY_SIZE = 256
) (
    input  wire                         clk,
    input  wire                         rst,

    // Adder control
    input  wire                         ctrl_ma,

    // Per-lane limb IDs (6 bits per lane, 0..32)
    input  wire [ARRAY_SIZE*6-1:0]      limb_id_add_bus,
    input  wire [ARRAY_SIZE*6-1:0]      limb_id_mul_bus,

    // Adder inputs/outputs (flattened)
    input  wire [ARRAY_SIZE*DATA_WIDTH-1:0] add_in0_bus,
    input  wire [ARRAY_SIZE*DATA_WIDTH-1:0] add_in1_bus,
    output wire [ARRAY_SIZE*DATA_WIDTH-1:0] add_out_bus,

    // Multiplier inputs/outputs (flattened)
    input  wire [ARRAY_SIZE*DATA_WIDTH-1:0] mult_in0_bus,
    input  wire [ARRAY_SIZE*DATA_WIDTH-1:0] mult_in1_bus,
    output wire [ARRAY_SIZE*DATA_WIDTH-1:0] mult_out_bus
);

    // -------------------------------------------------------------
    // Adder lanes
    // -------------------------------------------------------------
    genvar i;
    generate
      for (i = 0; i < ARRAY_SIZE; i = i + 1) begin : g_add
        // Slice per-lane signals
        wire [5:0]             limb_id_add_i = limb_id_add_bus[i*6 +: 6];
        wire [DATA_WIDTH-1:0]  add_in0_i     = add_in0_bus[i*DATA_WIDTH +: DATA_WIDTH];
        wire [DATA_WIDTH-1:0]  add_in1_i     = add_in1_bus[i*DATA_WIDTH +: DATA_WIDTH];
        wire [DATA_WIDTH-1:0]  add_out_i;

        // Lookup modulus for this lane
        wire [63:0] mod_i;
        wire [63:0] modinv_unused;
        mod_table_50 LUT_ADD (
          .id          (limb_id_add_i),
          .modulus     (mod_i),
          .modulus_inv (modinv_unused)
        );

        ma_unit_50 #(
          .DATA_WIDTH(DATA_WIDTH)
        ) u_ma (
          .clk         (clk),
          .rst         (rst),
          .ctrl_ma     (ctrl_ma),
          .modulus     (mod_i[DATA_WIDTH-1:0]),
          .input_data0 (add_in0_i),
          .input_data1 (add_in1_i),
          .output_data (add_out_i)
        );

        // Pack output
        assign add_out_bus[i*DATA_WIDTH +: DATA_WIDTH] = add_out_i;
      end
    endgenerate

    // -------------------------------------------------------------
    // Multiplier lanes
    // -------------------------------------------------------------
    genvar j;
    generate
      for (j = 0; j < ARRAY_SIZE; j = j + 1) begin : g_mul
        // Slice per-lane signals
        wire [5:0]             limb_id_mul_j = limb_id_mul_bus[j*6 +: 6];
        wire [DATA_WIDTH-1:0]  mult_in0_j    = mult_in0_bus[j*DATA_WIDTH +: DATA_WIDTH];
        wire [DATA_WIDTH-1:0]  mult_in1_j    = mult_in1_bus[j*DATA_WIDTH +: DATA_WIDTH];
        wire [DATA_WIDTH-1:0]  mult_out_j;

        // Lookup modulus & Montgomery n0' for this lane
        wire [63:0] mod_j;
        wire [63:0] modinv_j;
        mod_table_50 LUT_MUL (
          .id          (limb_id_mul_j),
          .modulus     (mod_j),
          .modulus_inv (modinv_j)
        );

        mm_unit_50 #(
          .DATA_WIDTH(DATA_WIDTH)
        ) u_mm (
          .clk         (clk),
          .rst         (rst),
          .modulus     (mod_j[DATA_WIDTH-1:0]),
          .modulus_inv (modinv_j),                 // 64-bit n0' (radix 2^64)
          .input_data0 (mult_in0_j),
          .input_data1 (mult_in1_j),
          .output_data (mult_out_j)
        );

        // Pack output
        assign mult_out_bus[j*DATA_WIDTH +: DATA_WIDTH] = mult_out_j;
      end
    endgenerate

endmodule
