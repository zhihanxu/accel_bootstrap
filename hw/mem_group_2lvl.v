// -----------------------------------------------------------------------------
// mem_group_2lvl.v 
// Two-level memory: 32 banks, each bank has 8 sub-banks.
// Each sub-bank stores blocks of 8 coefficients @ 50 bits each => 400-bit line.
// Simple 1R/1W at block granularity.
// Resource target per bank: exactly 25 URAM + 106 BRAM18, distributed across
// its 8 sub-banks (configure inside mem_bank).
// Developer: Zhihan Xu
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module mem_group_2lvl #(
    parameter integer BANKS              = 32,
    parameter integer SUBBANKS_PER_BANK  = 8,
    parameter integer COEFF_BITS         = 50,
    parameter integer COEFFS_PER_BLOCK   = 8,
    parameter integer LINE_WIDTH         = COEFF_BITS*COEFFS_PER_BLOCK, // 400
    parameter integer DEPTH_PER_SUBBANK  = 1024 // blocks per sub-bank (tunable)
)(
    input  wire                       clk,
    input  wire                       rst,

    // Per-bank, per-sub-bank write port (1W): flattened buses
    input  wire [BANKS*SUBBANKS_PER_BANK-1:0]            we_bus,
    input  wire [BANKS*SUBBANKS_PER_BANK*LINE_WIDTH-1:0] wdata_bus,
    input  wire [BANKS*SUBBANKS_PER_BANK*$clog2(DEPTH_PER_SUBBANK)-1:0] waddr_bus,

    // Per-bank, per-sub-bank read port (1R)
    input  wire [BANKS*SUBBANKS_PER_BANK-1:0]            re_bus,
    input  wire [BANKS*SUBBANKS_PER_BANK*$clog2(DEPTH_PER_SUBBANK)-1:0] raddr_bus,
    output wire [BANKS*SUBBANKS_PER_BANK*LINE_WIDTH-1:0] rdata_bus
);

    genvar b;
    generate
      for (b=0; b<BANKS; b=b+1) begin : g_bank
        // Slice per-bank buses
        localparam integer SB   = SUBBANKS_PER_BANK;
        localparam integer AAW  = $clog2(DEPTH_PER_SUBBANK);
        wire [SB-1:0]                 we_s;
        wire [SB*LINE_WIDTH-1:0]      wdata_s;
        wire [SB*AAW-1:0]             waddr_s;
        wire [SB-1:0]                 re_s;
        wire [SB*AAW-1:0]             raddr_s;
        wire [SB*LINE_WIDTH-1:0]      rdata_s;

        assign we_s    = we_bus   [b*SB +: SB];
        assign re_s    = re_bus   [b*SB +: SB];
        assign wdata_s = wdata_bus[b*SB*LINE_WIDTH +: SB*LINE_WIDTH];
        assign rdata_bus[b*SB*LINE_WIDTH +: SB*LINE_WIDTH] = rdata_s;
        assign waddr_s = waddr_bus[b*SB*AAW +: SB*AAW];
        assign raddr_s = raddr_bus[b*SB*AAW +: SB*AAW];

        // NOTE:
        // Verilog-2001 does not support unpacked array parameters or '{...} literals.
        // The per-sub-bank resource split (e.g., URAM: {3,3,3,3,3,3,3,4} and
        // BRAM18: {13,13,13,13,13,13,14,14}) should be encoded *inside* mem_bank
        // using localparams or parameters (URAM_CNT0..7, BR18_CNT0..7).

        mem_bank #(
          .SUBBANKS_PER_BANK (SUBBANKS_PER_BANK),
          .COEFF_BITS        (COEFF_BITS),
          .COEFFS_PER_BLOCK  (COEFFS_PER_BLOCK),
          .LINE_WIDTH        (LINE_WIDTH),
          .DEPTH_PER_SUBBANK (DEPTH_PER_SUBBANK)
        ) u_bank (
          .clk       (clk),
          .rst       (rst),
          .we_bus    (we_s),
          .wdata_bus (wdata_s),
          .waddr_bus (waddr_s),
          .re_bus    (re_s),
          .raddr_bus (raddr_s),
          .rdata_bus (rdata_s)
        );

      end
    endgenerate

endmodule
