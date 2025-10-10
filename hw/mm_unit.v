// 50-bit Modular Multiplier

module mm_unit_50 # (
  parameter DATA_WIDTH = 50
) (
  modulus,
  modulus_inv,
  input_data0,
  input_data1,
  output_data,
  clk,
  rst
);

  input clk, rst; 
  input [DATA_WIDTH:0] modulus;
  input [DATA_WIDTH:0] modulus_inv;
  input [DATA_WIDTH-1:0] input_data0;
  input [DATA_WIDTH-1:0] input_data1;

  output reg [DATA_WIDTH-1:0] output_data;

  reg [DATA_WIDTH-1:0] a_stage_01,a_stage_12,a_stage_23,a_stage_34,a_stage_45,a_stage_56;
  reg [DATA_WIDTH:0] b_stage_01,b_stage_12,b_stage_23,b_stage_34,b_stage_45,b_stage_56;
  reg [2*DATA_WIDTH-1:0] u_stage_01,u_stage_12,u_stage_23,u_stage_34,u_stage_45,u_stage_56;
  reg [DATA_WIDTH:0] v_stage_01,v_stage_12,v_stage_23,v_stage_34,v_stage_45,v_stage_56;

  reg [DATA_WIDTH:0] y_stage_01,y_stage_12,y_stage_23,y_stage_34,y_stage_45,y_stage_56,y_stage_67,y_stage_78,y_stage_89,y_stage_910,y_stage_1011,y_stage_1112,y_stage_1213,y_stage_1314;

  reg [2*DATA_WIDTH+1:0] w_stage_01,w_stage_12,w_stage_23,w_stage_34,w_stage_45,w_stage_56;
  reg [DATA_WIDTH:0] w_stage_67,w_stage_78,w_stage_89,w_stage_910,w_stage_1011,w_stage_1112;

  reg [2*DATA_WIDTH:0] x_stage_01,x_stage_12,x_stage_23,x_stage_34,x_stage_45,x_stage_56;
  reg [DATA_WIDTH-1:0] z_stage_01;

  always @(posedge clk or negedge rst)
  begin
    if(!rst) 
      output_data<=64'd0;
    else begin
        // Full IntMult1 data preparation
        a_stage_01<={input_data0};
        b_stage_01<={input_data1};
        
        a_stage_12<=a_stage_01;
        a_stage_23<=a_stage_12;
        a_stage_34<=a_stage_23;
        a_stage_45<=a_stage_34;
        a_stage_56<=a_stage_45;

        b_stage_12<=b_stage_01;
        b_stage_23<=b_stage_12;
        b_stage_34<=b_stage_23;
        b_stage_45<=b_stage_34;
        b_stage_56<=b_stage_45;
        
        // Full IntMult1 U=A*B
        u_stage_01<=input_data0[25:0]*input_data1[16:0];                                  // Stage 1: A0xB0
        u_stage_12<=u_stage_01+((a_stage_01[25:0]*b_stage_01[33:17])<<17);                // Stage 2: A0xB1
        u_stage_23<=u_stage_12+((a_stage_12[49:26]*b_stage_12[16:0])<<26);                // Stage 3: A1xB0
        u_stage_34<=u_stage_23+((a_stage_34[25:0]*b_stage_34[49:34])<<34);                // Stage 4: A0xB2
        u_stage_45<=u_stage_34+((a_stage_45[49:26]*b_stage_45[34:17])<<43);               // Stage 5: A1xB1
        u_stage_56<=u_stage_45+((a_stage_56[49:26]*b_stage_56[49:35])<<61);               // Stage 6: A1xB2
        
        // UH IntMult2 data preparation
        v_stage_01<=u_stage_56>>(DATA_WIDTH-1);
        v_stage_12<=v_stage_01;
        v_stage_23<=v_stage_12;
        v_stage_34<=v_stage_23;
        v_stage_45<=v_stage_34;
        v_stage_56<=v_stage_45;
    
        // UH IntMult2 W=V*T (T=modulus_inv) 51*51bit
        w_stage_01<=v_stage_01[25:0]*modulus_inv[16:0];                                 
        w_stage_12<=w_stage_01+((v_stage_01[25:0]*modulus_inv[33:17])<<17);               
        w_stage_23<=w_stage_12+((v_stage_12[50:26]*modulus_inv[16:0])<<26);               
        w_stage_34<=w_stage_23+((v_stage_34[25:0]*modulus_inv[50:34])<<34);               
        w_stage_45<=w_stage_34+((v_stage_45[50:26]*modulus_inv[34:18])<<43);                                   
        w_stage_56<=w_stage_45+((v_stage_56[50:26]*modulus_inv[50:35])<<61);         

        // LH IntMult2 data preparation
        w_stage_67<=w_stage_56>>(DATA_WIDTH+1);
        w_stage_78<=w_stage_67;
        w_stage_89<=w_stage_78;
        w_stage_910<=w_stage_89;
        w_stage_1011<=w_stage_910;
        w_stage_1112<=w_stage_1011;

        // LH IntMult2 X=W*q (q=modulus) 51*51bit
        x_stage_01<=w_stage_67[25:0]*modulus[16:0];
        x_stage_12<=x_stage_01+((w_stage_78[25:0]*modulus[33:17])<<17);
        x_stage_23<=x_stage_12+((w_stage_89[50:26]*modulus[16:0])<<26);
        x_stage_34<=x_stage_23+((w_stage_910[25:0]*modulus[50:34])<<34);
        x_stage_45<=x_stage_34+((w_stage_1011[50:26]*modulus[34:18])<<43);
        // x_stage_56<=x_stage_45+((w_stage_1112[50:26]*modulus[50:35])<<);

        // Final process
        y_stage_01<=u_stage_56[DATA_WIDTH:0]; //63bit
        y_stage_12<=y_stage_01;
        y_stage_23<=y_stage_12;
        y_stage_34<=y_stage_23;
        y_stage_45<=y_stage_34;
        y_stage_56<=y_stage_45;
        y_stage_67<=y_stage_56;
        y_stage_78<=y_stage_67;
        y_stage_89<=y_stage_78;
        y_stage_910<=y_stage_89;
        y_stage_1011<=y_stage_910;
        y_stage_1112<=y_stage_1011;
        y_stage_1213<=y_stage_1112;
        // y_stage_1314<=y_stage_1213;

        z_stage_01<=y_stage_1213-x_stage_45[DATA_WIDTH:0];
        
        if(z_stage_01>=2*modulus) begin
          output_data<=z_stage_01-2*modulus;
        end else if (z_stage_01>modulus) begin
          output_data<=z_stage_01-modulus;
        end else begin
          output_data<=z_stage_01;
        end
    end
  end
endmodule
