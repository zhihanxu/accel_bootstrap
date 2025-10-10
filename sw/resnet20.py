from operations import *

def conv(l, ci, co, kernel_size):
    cycle = 0
    # ci packed process in parallel, rotate ci times
    cn = ci    
    rotate_cycle = 0  
    # for h in range(kernel_size*kernel_size):
    #     rotate_cycle += rotate(l)  # rotate input (single ct)
    rotate_cycle += hrotate(l, cn)
    rotate_cycle += hrotate(l, kernel_size*kernel_size)
    cycle += rotate_cycle
    
    # per packed SISO
    # for k in range(co):
    #     level = l
    #     for i in range(kernel_size):
    #         for j in range(kernel_size):
    #             cycle += hmult(level)
    #             cycle += rescale(level)
    #             level-=1
    #             cycle += hadd(level)       
    #     cycle += hadd(level-kernel_size*kernel_size)  
         
    for i in range(kernel_size):
        for j in range(kernel_size):
            cycle += hmult(l)
            cycle += rescale(l)
            l -= 1
            cycle += hadd(l)     
              
    cycle += co * hadd(l-kernel_size*kernel_size)     
    other_cycle = cycle - rotate_cycle
    print("rotate cycle: ", rotate_cycle, "percent: ", rotate_cycle/cycle, "other cycle: ", other_cycle)   
    return cycle

def relu(l, ci):
    cycle = 0
    p1 = 7
    p2 = 15
    p3 = 27 # consume 5 levels
    cycle += 2 * poly_eval_m4(l)
    cycle += poly_eval(l)
    cycle += 2 * rescale(l-4) + 3 * moddown(l, l-5) + 3 * cmult(l-5) + 3 * hadd(l-5)
    cycle += 3 * hmult(l-5) + 3 * rescale(l-5)
    # consume 6 levels in total
    return cycle

def ap(l):
    cycle = 2 * hrotate(l, 3)
    cycle += 2 * 3 * hadd(l)
    return cycle

def fc(l):
    cycle = 0
    for i in range (8):
        cycle += pmult(l)
        cycle += rescale(l)
        cycle += hadd(l-1)
    return cycle
        

if __name__ == "__main__":
    print("-----------Profiling-----------")
    # test_cycle = conv(38, 64, 64, 3)
    # test2_cycle = relu(38, 16)    
    # print("Conv cycle: ", test_cycle, "time: ", test_cycle/freq*1e3, "ms")
    # print("Relu cycle: ", test2_cycle, "time: ", test2_cycle/freq*1e3, "ms")
    
    L1_cycle = 0
    L2_cycle = 0
    L2_boot_cycle = 0
    L3_cycle = 0
    L4_cycle = 0
    L5_cycle = 0
    
    L_boot = 29 # bootstrap to 29 limbs
    
    con1_cycle = conv(L+1, 3, 3, 3)   # consume 9 levels
    relu1_cycle = relu(L-8, 16)     # consume 6 levels
    L1_cycle = con1_cycle + relu1_cycle
    print("\n-------L1 breakdown-------")
    print("L1 conv cycle: ", con1_cycle, "time: ", con1_cycle/freq*1e3, "ms", "percent: ", con1_cycle/L1_cycle)
    print("L1 relu cycle: ", relu1_cycle, "time: ", relu1_cycle/freq*1e3, "ms", "percent: ", relu1_cycle/L1_cycle)
    print("L1 cycle: ", L1_cycle, "time: ", L1_cycle/freq*1e3, "ms")
    print("-------L1 breakdown-------\n")
    
    conv2_1_cycle = conv(L-14, 16, 16, 3)   
    relu2_1_cycle = relu(L-23, 16)        
    boot2_1_cycle = bootstrap_limb(L-29)       
    conv2_1_cycle += conv(L_boot, 16, 16, 3)   
    shortcut2_1_cycle = moddown(L-14, L_boot-9) + hadd(L_boot-9)
    relu2_1_cycle += relu(L_boot-9, 16)
    L2_cycle = conv2_1_cycle + relu2_1_cycle + boot2_1_cycle + shortcut2_1_cycle
    
    conv2_2_cycle = conv(L_boot-15, 16, 16, 3)
    boot2_2_cycle = bootstrap_limb(L_boot-24)
    relu2_2_cycle = relu(L_boot, 16)
    conv2_2_cycle += conv(L_boot-6, 16, 16, 3)
    shortcut2_2_cycle = hadd(L_boot-15)
    relu2_2_cycle += relu(L_boot-15, 16)
    L2_cycle += conv2_2_cycle + boot2_2_cycle + relu2_2_cycle + shortcut2_2_cycle
    
    boot2_3_cycle = bootstrap_limb(L_boot-21)
    conv2_3_cycle = conv(L_boot, 16, 16, 3)
    relu2_3_cycle = relu(L_boot-9, 16)
    conv2_3_cycle += conv(L_boot-15, 16, 16, 3)
    shortcut2_3_cycle = moddown(L_boot-21, L_boot-24) + hadd(L_boot-24)
    boot2_3_cycle += bootstrap_limb(L_boot-24)
    relu2_3_cycle += relu(L_boot, 16)
    L2_cycle += boot2_3_cycle + conv2_3_cycle + relu2_3_cycle + shortcut2_3_cycle
    L2_boot_cycle = boot2_1_cycle + boot2_2_cycle + boot2_3_cycle
    L2_conv_cycle = conv2_1_cycle + conv2_2_cycle + conv2_3_cycle
    L2_relu_cycle = relu2_1_cycle + relu2_2_cycle + relu2_3_cycle
    L2_others_cycle = L2_cycle - L2_conv_cycle - L2_relu_cycle - L2_boot_cycle
    print("-------L2 breakdown-------")
    print("L2 conv cycle: ", L2_conv_cycle, "time: ", L2_conv_cycle/freq*1e3, "ms", "percent: ", L2_conv_cycle/L2_cycle)
    print("L2 relu cycle: ", L2_relu_cycle, "time: ", L2_relu_cycle/freq*1e3, "ms", "percent: ", L2_relu_cycle/L2_cycle)
    print("L2 boot cycle: ", L2_boot_cycle, "time: ", L2_boot_cycle/freq*1e3, "ms", "percent: ", L2_boot_cycle/L2_cycle)
    print("L2 others cycle: ", L2_others_cycle, "time: ", L2_others_cycle/freq*1e3, "ms", "percent: ", L2_others_cycle/L2_cycle)
    print("L2 cycle: ", L2_cycle, "time: ", L2_cycle/freq*1e3, "ms")
    print("-------L2 breakdown-------\n")
    
    
    conv_3_1_cycle = conv(L_boot-6, 16, 32, 3)
    relu_3_1_cycle = relu(L_boot-15, 32)
    boot_3_1_cycle = bootstrap_limb(L_boot-21)
    conv_3_1_cycle += conv(L_boot, 32, 32, 3)
    shortcut_3_1_cycle = conv(L_boot-6, 16, 32, 1) + moddown(L_boot-7, L_boot-9) + hadd(L_boot-9) 
    relu_3_1_cycle += relu(L_boot-9, 32)
    L3_cycle = conv_3_1_cycle + relu_3_1_cycle + boot_3_1_cycle + shortcut_3_1_cycle
    
    conv_3_2_cycle = conv(L_boot-15, 32, 32, 3)
    boot_3_2_cycle = bootstrap_limb(L_boot-24)
    relu_3_2_cycle = relu(L_boot, 32)
    conv_3_2_cycle += conv(L_boot-6, 32, 32, 3)
    shortcut_3_2_cycle = hadd(L_boot-15)
    relu_3_2_cycle += relu(L_boot-15, 32)
    L3_cycle += conv_3_2_cycle + boot_3_2_cycle + relu_3_2_cycle + shortcut_3_2_cycle
    
    boot_3_3_cycle = bootstrap_limb(L_boot-21)
    conv_3_3_cycle = conv(L_boot, 32, 32, 3)
    relu_3_3_cycle = relu(L_boot-9, 32)
    conv_3_3_cycle += conv(L_boot-15, 32, 32, 3)
    shortcut_3_3_cycle = moddown(L_boot-21, L_boot-24) + hadd(L_boot-24)
    boot_3_3_cycle += bootstrap_limb(L_boot-24)
    relu_3_3_cycle += relu(L_boot, 32)
    L3_cycle += boot_3_3_cycle + conv_3_3_cycle + relu_3_3_cycle + shortcut_3_3_cycle
    L3_boot_cycle = boot_3_1_cycle + boot_3_2_cycle + boot_3_3_cycle
    L3_conv_cycle = conv_3_1_cycle + conv_3_2_cycle + conv_3_3_cycle
    L3_relu_cycle = relu_3_1_cycle + relu_3_2_cycle + relu_3_3_cycle
    L3_others_cycle = L3_cycle - L3_conv_cycle - L3_relu_cycle - L3_boot_cycle
    print("-------L3 breakdown-------")
    print("L3 conv cycle: ", L3_conv_cycle, "time: ", L3_conv_cycle/freq*1e3, "ms", "percent: ", L3_conv_cycle/L3_cycle)
    print("L3 relu cycle: ", L3_relu_cycle, "time: ", L3_relu_cycle/freq*1e3, "ms", "percent: ", L3_relu_cycle/L3_cycle)
    print("L3 boot cycle: ", L3_boot_cycle, "time: ", L3_boot_cycle/freq*1e3, "ms", "percent: ", L3_boot_cycle/L3_cycle)
    print("L3 others cycle: ", L3_others_cycle, "time: ", L3_others_cycle/freq*1e3, "ms", "percent: ", L3_others_cycle/L3_cycle)
    print("L3 cycle: ", L3_cycle, "time: ", L3_cycle/freq*1e3, "ms")
    print("-------L3 breakdown-------\n")
    
    conv_4_1_cycle = conv(L_boot-6, 32, 64, 3)
    relu_4_1_cycle = relu(L_boot-15, 64)
    boot_4_1_cycle = bootstrap_limb(L_boot-21)
    conv_4_1_cycle += conv(L_boot, 64, 64, 3)
    shortcut_4_1_cycle = conv(L_boot-6, 32, 64, 1) + moddown(L_boot-7, L_boot-9) + hadd(L_boot-9)
    relu_4_1_cycle += relu(L_boot-9, 64)
    L4_cycle = conv_4_1_cycle + relu_4_1_cycle + boot_4_1_cycle + shortcut_4_1_cycle
    
    conv_4_2_cycle = conv(L_boot-15, 64, 64, 3)
    boot_4_2_cycle = bootstrap_limb(L_boot-24)
    relu_4_2_cycle = relu(L_boot, 64)
    conv_4_2_cycle += conv(L_boot-6, 64, 64, 3)
    shortcut_4_2_cycle = hadd(L_boot-15)
    relu_4_2_cycle += relu(L_boot-15, 64)
    L4_cycle += conv_4_2_cycle + boot_4_2_cycle + relu_4_2_cycle + shortcut_4_2_cycle
    
    boot_4_3_cycle = bootstrap_limb(L_boot-21)
    conv_4_3_cycle = conv(L_boot, 64, 64, 3)
    relu_4_3_cycle = relu(L_boot-9, 64)
    conv_4_3_cycle += conv(L_boot-15, 64, 64, 3)
    shortcut_4_3_cycle = moddown(L_boot-21, L_boot-24) + hadd(L_boot-24)
    boot_4_3_cycle += bootstrap_limb(L_boot-24)
    relu_4_3_cycle += relu(L_boot, 64)
    L4_cycle += boot_4_3_cycle + conv_4_3_cycle + relu_4_3_cycle + shortcut_4_3_cycle
    L4_boot_cycle = boot_4_1_cycle + boot_4_2_cycle + boot_4_3_cycle
    L4_conv_cycle = conv_4_1_cycle + conv_4_2_cycle + conv_4_3_cycle
    L4_relu_cycle = relu_4_1_cycle + relu_4_2_cycle + relu_4_3_cycle
    L4_others_cycle = L4_cycle - L4_conv_cycle - L4_relu_cycle - L4_boot_cycle
    print("-------L4 breakdown-------")
    print("L4 conv cycle: ", L4_conv_cycle, "time: ", L4_conv_cycle/freq*1e3, "ms", "percent: ", L4_conv_cycle/L4_cycle)
    print("L4 relu cycle: ", L4_relu_cycle, "time: ", L4_relu_cycle/freq*1e3, "ms", "percent: ", L4_relu_cycle/L4_cycle)
    print("L4 boot cycle: ", L4_boot_cycle, "time: ", L4_boot_cycle/freq*1e3, "ms", "percent: ", L4_boot_cycle/L4_cycle)
    print("L4 others cycle: ", L4_others_cycle, "time: ", L4_others_cycle/freq*1e3, "ms", "percent: ", L4_others_cycle/L4_cycle)
    print("L4 cycle: ", L4_cycle, "time: ", L4_cycle/freq*1e3, "ms")
    print("-------L4 breakdown-------\n")
    
    
    ap_cycle = ap(L_boot-6)
    fc_cycle = fc(L_boot-6)
    # softmax
    sm_cycle = 0
    for i in range(10):
        sm_cycle += cmult(L_boot-7)
        sm_cycle += poly_eval_m4(L_boot-7)
        for j in range(6):
            sm_cycle += hmult(L_boot-11)
            sm_cycle += rescale(L_boot-11)
        sm_cycle += hadd(L_boot-12)
    sm_cycle += cmult(L_boot-12)
    level = L_boot-12
    for k in range(16):
        sm_cycle += hmult(level)
        sm_cycle += rescale(level)
        level -= 1
        sm_cycle += hadd(level)
        sm_cycle += hmult(level)
        sm_cycle += rescale(level)
        level -= 1
        if (level <= 4):
            sm_cycle += bootstrap()
            level = L_boot
    for i in range(10):
        sm_cycle += hmult(level)
        sm_cycle += rescale(level)
    # softmax done
    L5_cycle = ap_cycle + fc_cycle + sm_cycle
    L5_boot_cycle = bootstrap()
    
    total_cycle = L1_cycle + L2_cycle + L3_cycle + L4_cycle + L5_cycle
    total_boot_cycle = L2_boot_cycle + L3_boot_cycle + L4_boot_cycle + L5_boot_cycle
    
    print("Total cycle: ", total_cycle, "time: ", total_cycle/freq*1e3, "ms")
    print("Total boot cycle: ", total_boot_cycle, "time: ", total_boot_cycle/freq*1e3, "ms")
    
    
    print("--------------Done------------")
    