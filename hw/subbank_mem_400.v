// -----------------------------------------------------------------------------
// subbank_mem_400.v
// One sub-bank memory: DEPTH × 400 bits, 1 write port, 1 read port.
// Internally split into URAM-backed stripe and BRAM18-backed stripe.
// The number of URAM and BRAM tiles are compile-time parameters so that the
// bank-level sum exactly hits 25 URAM + 106 BRAM18 per bank.
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module subbank_mem_400 #(
    parameter integer COEFF_BITS        = 50,
    parameter integer COEFFS_PER_BLOCK  = 8,
    parameter integer LINE_WIDTH        = COEFF_BITS*COEFFS_PER_BLOCK, // 400
    parameter integer DEPTH             = 1024,

    // Tile counts for this sub-bank (per the bank's distribution)
    parameter integer URAM_TILES        = 3,   // contributes to URAM usage
    parameter integer BRAM18_TILES      = 13   // contributes to BRAM18 usage
)(
    input  wire                      clk,
    input  wire                      rst,

    // 1W
    input  wire                      we,
    input  wire [$clog2(DEPTH)-1:0]  waddr,
    input  wire [LINE_WIDTH-1:0]     wdata,

    // 1R
    input  wire                      re,
    input  wire [$clog2(DEPTH)-1:0]  raddr,
    output wire [LINE_WIDTH-1:0]     rdata
);

    // -------------------------
    // Stripe split (compile-time)
    // -------------------------
    // Heuristic: map the lower portion to URAM, the rest to BRAM.
    // We aim for a rough proportion URAM:BRAM bits ~= URAM_TILES : BRAM18_TILES
    // but clamp to the physical line width.
    localparam integer TOTAL_TILES    = URAM_TILES + BRAM18_TILES;
    localparam integer URAM_BITS_EST  = (LINE_WIDTH * URAM_TILES) / (TOTAL_TILES>0?TOTAL_TILES:1);
    localparam integer URAM_BITS      = (URAM_BITS_EST>LINE_WIDTH) ? LINE_WIDTH : URAM_BITS_EST;
    localparam integer BRAM_BITS      = LINE_WIDTH - URAM_BITS;

    // Avoid degenerate zero-width stripes
    localparam integer URAM_W = (URAM_BITS < 1) ? 1 : URAM_BITS;
    localparam integer BRAM_W = (BRAM_BITS < 1) ? 1 : BRAM_BITS;

    // -------------------------
    // URAM stripe
    // -------------------------
    // Depth partitioning: split depth across URAM_TILES equally (last gets remainder)
    function integer div_ceil;
      input integer a,b; begin div_ceil = (a + b - 1)/b; end
    endfunction

    localparam integer URAM_DEPTH_SEG = (URAM_TILES>0)? div_ceil(DEPTH, URAM_TILES) : 0;

    // Write/read muxing across URAM depth segments
    // We implement a simple banked-depth organization:
    //   physical segment k stores logical addresses [k*URAM_DEPTH_SEG .. (k+1)*URAM_DEPTH_SEG-1]
    // This gives exact URAM_TILES instances.
    genvar u;
    wire [URAM_W-1:0] uram_rdata_vec [0:(URAM_TILES>0?URAM_TILES-1:0)];
    generate
      if (URAM_TILES>0) begin : g_uram
        for (u=0; u<URAM_TILES; u=u+1) begin : seg
          wire                   sel_w = we & (waddr >= (u*URAM_DEPTH_SEG)) & (waddr < ((u+1)*URAM_DEPTH_SEG));
          wire                   sel_r = re & (raddr >= (u*URAM_DEPTH_SEG)) & (raddr < ((u+1)*URAM_DEPTH_SEG));
          wire [$clog2(URAM_DEPTH_SEG)-1:0] waddr_loc = waddr - (u*URAM_DEPTH_SEG);
          wire [$clog2(URAM_DEPTH_SEG)-1:0] raddr_loc = raddr - (u*URAM_DEPTH_SEG);

          (* ram_style = "ultra" *) reg [URAM_W-1:0] uram_mem [0:URAM_DEPTH_SEG-1];

          // Simple 1W/1R
          reg [URAM_W-1:0] uram_q;
          always @(posedge clk) begin
            if (sel_w) uram_mem[waddr_loc] <= wdata[URAM_W-1:0];
            if (sel_r) uram_q <= uram_mem[raddr_loc];
          end
          assign uram_rdata_vec[u] = uram_q;
        end
      end
    endgenerate

    wire [URAM_W-1:0] uram_rdata = (URAM_TILES==0) ? {URAM_W{1'b0}} :
                                   uram_rdata_vec[(raddr/URAM_DEPTH_SEG)];

    // -------------------------
    // BRAM stripe
    // -------------------------
    localparam integer BRAM_DEPTH_SEG = (BRAM18_TILES>0)? div_ceil(DEPTH, BRAM18_TILES) : 0;

    genvar bti;
    wire [BRAM_W-1:0] bram_rdata_vec [0:(BRAM18_TILES>0?BRAM18_TILES-1:0)];
    generate
      if (BRAM18_TILES>0) begin : g_bram
        for (bti=0; bti<BRAM18_TILES; bti=bti+1) begin : seg
          wire                   sel_w = we & (waddr >= (bti*BRAM_DEPTH_SEG)) & (waddr < ((bti+1)*BRAM_DEPTH_SEG));
          wire                   sel_r = re & (raddr >= (bti*BRAM_DEPTH_SEG)) & (raddr < ((bti+1)*BRAM_DEPTH_SEG));
          wire [$clog2(BRAM_DEPTH_SEG)-1:0] waddr_loc = waddr - (bti*BRAM_DEPTH_SEG);
          wire [$clog2(BRAM_DEPTH_SEG)-1:0] raddr_loc = raddr - (bti*BRAM_DEPTH_SEG);

          (* ram_style = "block" *) reg [BRAM_W-1:0] bram_mem [0:BRAM_DEPTH_SEG-1];

          reg [BRAM_W-1:0] bram_q;
          always @(posedge clk) begin
            if (sel_w) bram_mem[waddr_loc] <= wdata[URAM_W +: BRAM_W];
            if (sel_r) bram_q <= bram_mem[raddr_loc];
          end
          assign bram_rdata_vec[bti] = bram_q;
        end
      end
    endgenerate

    wire [BRAM_W-1:0] bram_rdata = (BRAM18_TILES==0) ? {BRAM_W{1'b0}} :
                                   bram_rdata_vec[(raddr/BRAM_DEPTH_SEG)];

    // -------------------------
    // Combine stripes to 400-bit line
    // -------------------------
    assign rdata = { bram_rdata, uram_rdata };

endmodule
