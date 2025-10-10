from operations import *


def sumcolvec(l):
    cycle = 0
    for i in range(8):
        cycle += rotate(l)
        cycle += hadd(l)
    
    cycle += cmult(l)
    
    for i in range(8):
        cycle += rotate(l)
        cycle += hadd(l)
        
    cycle += rescale(l)
    return cycle

def sumrowvec(l):
    cycle = 0
    for i in range(10):
        cycle += rotate(l)
        cycle += hadd(l)
    return cycle

def helr(lw, lz):
    cycle = hmult(lw)
    cycle += rescale(lw)        # M: depth 1
    
    
    # cycle += 8*rotate(lw-1)
    # cycle += 9*rescale(lw-1)
    # cycle += 8*hadd(lw-2)       # M: depth 2
    cycle_sumcolvec = sumcolvec(lw-1)
    cycle += cycle_sumcolvec
            
    cycle += hmult(lw-2)
    cycle += rescale(lw-2)  
    cycle += hadd(lw-3)         # M''
    
    cycle += cmult(lz)          # Z'
    cycle += cmult(lz)          # Z''
    cycle += 2*rescale(lz)
    cycle += moddown(lz, lw-2)  # Z'' -> Z'''
    cycle += hmult(lw-2)        # M * Z'''
    cycle += rescale(lw-2)      # M'
    
    cycle += hmult(lw-3)        # M' * M''
    cycle += rescale(lw-3)      # G
    
    cycle += moddown(lz, lw-4)  # Z' -> G
    cycle += hadd(lw-4)         
    cycle += moddown(lw, lw-4)  # V -> G
    cycle_sumrowvec = sumrowvec(lw-4)
    cycle += cycle_sumrowvec
    cycle += hadd(lw-4)         # W+
    
    cycle += moddown(lw, lw-4)  # W -> W+
    cycle += 2*cmult(lw-4)
    cycle += 2*rescale(lw-4)     
    cycle += hadd(lw-5)         # V+ 
    cycle += rescale(lw-4)      # W+
    time = cycle/freq
    print("-----------------HELR one iter-----------------")
    print ("sumcolvec cycles: ", cycle_sumcolvec, "percent: ", cycle_sumcolvec/cycle)
    print ("sumrowvec cycles: ", cycle_sumrowvec, "percent: ", cycle_sumrowvec/cycle)
    print ("cycles: ", cycle, "time: ", time*1e3, "ms")
    return cycle


if __name__ == "__main__":
    # L = 38; 6 iteration, bootstrap -> 24
    # 30 iteration, 6+6*4, 4 iter->boot; 6 boot
    L2 = 27
    total_cycle = 0
    boot_cycle = 0
    helr_cycle = 0
    for i in range(6):
        helr_cycle += helr(L-5*i, L)
    for j in range(6):
        boot_cycle += bootstrap_limb(7)
        for k in range(4):
            helr_cycle += helr(L2-5*k, L)
    
    total_cycle = boot_cycle + helr_cycle
    cycle_per_iter = total_cycle/30
    
    print("-----------------HELR starts----------------")
    print("boot cycle: ", boot_cycle, "percent: ", boot_cycle/total_cycle)
    print("helr cycle: ", helr_cycle, "percent: ", helr_cycle/total_cycle)
    print("total cycles: ", total_cycle, "total time: ", total_cycle/freq*1e3, "ms")
    print("cycle/iter: ", cycle_per_iter, "time/iter: ", cycle_per_iter/freq*1e3, "ms")
    print("-----------------HELR ends-----------------")
