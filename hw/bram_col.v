module bram_col_2 # (
    parameter DATA_WIDTH = 54,
    parameter ADDR_WIDTH = 10
)(
    input clk,
    input [ADDR_WIDTH-1:0] addr_read,        // 10-bit address for 1024 locations
    input [ADDR_WIDTH-1:0] addr_write,       // 10-bit address for 1024 locations
    input [DATA_WIDTH-1:0] data_in,        // 54-bit data input
    output [DATA_WIDTH-1:0] data_out,      // 54-bit data output
    input we                     // Write enable
);
    
    // Split the 32-bit input into two 18-bit inputs
    wire [17:0] data_in_bram0 = data_in[17:0];
    wire [17:0] data_in_bram1 = {4'b0, data_in[31:18]};
    
    // Outputs from each BRAM
    wire [17:0] data_out_bram0;
    wire [17:0] data_out_bram1;

    // Combine the 18-bit outputs into one 32-bit output
    assign data_out = {data_out_bram1[13:0], data_out_bram0};

    // Instantiate three BRAMs
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram0 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );
    
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram1 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram1),
        .data_out(data_out_bram1),
        .we(we)
    );
  
endmodule

module bram_col_4 # (
    parameter DATA_WIDTH = 32, 
    parameter ADDR_WIDTH = 11
)(
    input clk,
    input [ADDR_WIDTH-1:0] addr_read,        // 11-bit address for 2048 locations
    input [ADDR_WIDTH-1:0] addr_write,       // 11-bit address for 2048 locations
    input [DATA_WIDTH-1:0] data_in,          // 32-bit data input (update comment if DATA_WIDTH=54)
    output reg [DATA_WIDTH-1:0] data_out,    // 32-bit data output (update comment if DATA_WIDTH=54)
    input we                                   // Write enable
);
    
    // Change data_out_bramX from reg to wire
    reg [17:0] data_in_bram0, data_in_bram1, data_in_bram2, data_in_bram3;
    wire [17:0] data_out_bram0, data_out_bram1, data_out_bram2, data_out_bram3;
    
    always @(posedge clk) begin
        if (we) begin
            if (addr_write[ADDR_WIDTH-1] == 0) begin
                data_in_bram0 <= data_in[17:0];
                data_in_bram1 <= {4'b0, data_in[31:18]}; 
            end
            else begin
                data_in_bram2 <= data_in[17:0];
                data_in_bram3 <= {4'b0, data_in[31:18]}; 
            end
        end 
        else begin
            if (addr_read[ADDR_WIDTH-1] == 0) begin
                data_out <= {data_out_bram1[13:0], data_out_bram0};
            end
            else begin
                data_out <= {data_out_bram3[13:0], data_out_bram2};
            end
        end
    end

    // Instantiate four BRAM units
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram0 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );
    
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram1 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram1),
        .data_out(data_out_bram1),
        .we(we)
    );

    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram2 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram2),
        .data_out(data_out_bram2),
        .we(we)
    );

    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram3 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram3),
        .data_out(data_out_bram3),
        .we(we)
    );
  
endmodule
