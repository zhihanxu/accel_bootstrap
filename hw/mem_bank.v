// -----------------------------------------------------------------------------
// mem_bank.v (Verilog-2001)
// One bank with 8 sub-banks. Routes per-sub-bank resource counts.
// -----------------------------------------------------------------------------
`timescale 1ns/1ps

module mem_bank #(
    parameter integer SUBBANKS_PER_BANK  = 8,
    parameter integer COEFF_BITS         = 50,
    parameter integer COEFFS_PER_BLOCK   = 8,
    parameter integer LINE_WIDTH         = COEFF_BITS*COEFFS_PER_BLOCK,
    parameter integer DEPTH_PER_SUBBANK  = 1024
)(
    input  wire                              clk,
    input  wire                              rst,

    // Flattened per-sub-bank 1W/1R
    input  wire [SUBBANKS_PER_BANK-1:0]      we_bus,
    input  wire [SUBBANKS_PER_BANK*LINE_WIDTH-1:0] wdata_bus,
    input  wire [SUBBANKS_PER_BANK*$clog2(DEPTH_PER_SUBBANK)-1:0] waddr_bus,

    input  wire [SUBBANKS_PER_BANK-1:0]      re_bus,
    input  wire [SUBBANKS_PER_BANK*$clog2(DEPTH_PER_SUBBANK)-1:0] raddr_bus,
    output wire [SUBBANKS_PER_BANK*LINE_WIDTH-1:0] rdata_bus
);

    // -------------------------------------------------------------------------
    // Verilog-2001 friendly per-sub-bank resource split.
    //   URAM per sub-bank:   {3,3,3,3,3,3,3,4} = 25
    //   BRAM18 per sub-bank: {13,13,13,13,13,13,14,14} = 106
    // Promote these to parameters if you need per-bank overrides.
    // -------------------------------------------------------------------------
    localparam [3:0] URAM_CNT0 = 4'd3;
    localparam [3:0] URAM_CNT1 = 4'd3;
    localparam [3:0] URAM_CNT2 = 4'd3;
    localparam [3:0] URAM_CNT3 = 4'd3;
    localparam [3:0] URAM_CNT4 = 4'd3;
    localparam [3:0] URAM_CNT5 = 4'd3;
    localparam [3:0] URAM_CNT6 = 4'd3;
    localparam [3:0] URAM_CNT7 = 4'd4;

    localparam [6:0] BR18_CNT0 = 7'd13;
    localparam [6:0] BR18_CNT1 = 7'd13;
    localparam [6:0] BR18_CNT2 = 7'd13;
    localparam [6:0] BR18_CNT3 = 7'd13;
    localparam [6:0] BR18_CNT4 = 7'd13;
    localparam [6:0] BR18_CNT5 = 7'd13;
    localparam [6:0] BR18_CNT6 = 7'd14;
    localparam [6:0] BR18_CNT7 = 7'd14;

    genvar s;
    generate
      for (s=0; s<SUBBANKS_PER_BANK; s=s+1) begin : g_sb
        localparam integer AAW = $clog2(DEPTH_PER_SUBBANK);

        // Pick constants for this sub-bank (elaboration-time selection)
        localparam [3:0] URAM_TILES_S =
              (s==0) ? URAM_CNT0 :
              (s==1) ? URAM_CNT1 :
              (s==2) ? URAM_CNT2 :
              (s==3) ? URAM_CNT3 :
              (s==4) ? URAM_CNT4 :
              (s==5) ? URAM_CNT5 :
              (s==6) ? URAM_CNT6 :
                       URAM_CNT7 ;

        localparam [6:0] BRAM18_TILES_S =
              (s==0) ? BR18_CNT0 :
              (s==1) ? BR18_CNT1 :
              (s==2) ? BR18_CNT2 :
              (s==3) ? BR18_CNT3 :
              (s==4) ? BR18_CNT4 :
              (s==5) ? BR18_CNT5 :
              (s==6) ? BR18_CNT6 :
                       BR18_CNT7 ;

        // Slice per-sub-bank signals
        wire                    we    = we_bus[s];
        wire [LINE_WIDTH-1:0]   wdata = wdata_bus[s*LINE_WIDTH +: LINE_WIDTH];
        wire [AAW-1:0]          waddr = waddr_bus[s*AAW +: AAW];
        wire                    re    = re_bus[s];
        wire [AAW-1:0]          raddr = raddr_bus[s*AAW +: AAW];
        wire [LINE_WIDTH-1:0]   rdata;

        // Sub-bank instance with Verilog-2001 parameters
        subbank_mem_400 #(
          .COEFF_BITS        (COEFF_BITS),
          .COEFFS_PER_BLOCK  (COEFFS_PER_BLOCK),
          .LINE_WIDTH        (LINE_WIDTH),
          .DEPTH             (DEPTH_PER_SUBBANK),
          .URAM_TILES        (URAM_TILES_S),
          .BRAM18_TILES      (BRAM18_TILES_S)
        ) u_sb (
          .clk   (clk),
          .rst   (rst),
          .we    (we),
          .waddr (waddr),
          .wdata (wdata),
          .re    (re),
          .raddr (raddr),
          .rdata (rdata)
        );

        assign rdata_bus[s*LINE_WIDTH +: LINE_WIDTH] = rdata;
      end
    endgenerate

endmodule
