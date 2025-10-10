
module bram_bank1 #(
    parameter ADDR_WIDTH = 10,
    parameter DATA_WIDTH = 32,
    parameter dp = 512
) (
    input wire clk,
    input wire [ADDR_WIDTH-1:0] addr,              
    input wire [dp*DATA_WIDTH-1:0] data_in,       
    output wire [dp*DATA_WIDTH-1:0] data_out,        
    input wire we
);
    
    genvar i;

    // instantiate dp bram_col_2
    generate
        for (i = 0; i < dp; i = i + 1) begin : bram_col_2_instances
            bram_col_2 #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)) bram_col_2_inst (
                .clk(clk),
                .addr(addr[ADDR_WIDTH]),
                .data_in(data_in[i*DATA_WIDTH +: DATA_WIDTH]),
                .data_out(data_out[i*DATA_WIDTH +: DATA_WIDTH]),
                .we(we)
            );
        end
    endgenerate

endmodule


module bram_bank2 #(
    parameter ADDR_WIDTH = 11,
    parameter DATA_WIDTH = 32,
    parameter dp = 512
) (
    input wire clk,
    input wire [ADDR_WIDTH-1:0] addr,              
    input wire [dp*DATA_WIDTH-1:0] data_in,       
    output wire [dp*DATA_WIDTH-1:0] data_out,        
    input wire we
);
    
    genvar i;

    // instantiate dp bram_col_4
    generate
        for (i = 0; i < dp; i = i + 1) begin : bram_col_4_instances
            bram_col_4 #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)) bram_col_4_inst (
                .clk(clk),
                .addr(addr[ADDR_WIDTH]),
                .data_in(data_in[i*DATA_WIDTH +: DATA_WIDTH]),
                .data_out(data_out[i*DATA_WIDTH +: DATA_WIDTH]),
                .we(we)
            );
        end
    endgenerate

endmodule