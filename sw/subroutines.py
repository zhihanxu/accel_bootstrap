from parameters import *
# import matplotlib.pyplot as plt

# Number Theoretic Transform： compute-bound
def ntt(limb):
    cycle = limb*N/dp + (modMult + modAdd + spn_cycles) * math.log2(N)
    read_time = 2*limb * one_limb_size / HBM_bw
    write_time = limb * one_limb_size / HBM_bw
    mem_time = read_time + write_time
    throughput = limb / (cycle/freq + mem_time)
    # print("----------ntt breakdown----------")
    # print("compute_cycle: ", cycle, "compute time: ", cycle/freq*1e3, "ms")
    # print("mem_time: ", mem_time*1e3, "ms")
    # print("throughput: ", throughput, "op/s")
    # print("----------ntt breakdown----------\n")
    return cycle

# RNS Basis Conversion: compute-bound
def bconv(pre_limb,new_limb):    
    # cycle = modMult + (new_limb+1) * pre_limb * N/dp + modAdd + new_limb * (pre_limb-1) * N/dp  # for benchamarking latency: k
    cycle = modMult + 1 * pre_limb * N/dp + modMAC + new_limb * pre_limb * N/dp
    # one_new_limb_cycle = (2*modMult + modAdd) + pre_limb * N/dp
    # cycle = one_new_limb_cycle * new_limb
    read_time = pre_limb * one_limb_size / HBM_bw
    write_time = new_limb * one_limb_size / HBM_bw
    mem_time = read_time + write_time
    # print("----------bconv breakdown----------")
    # print("compute_cycle: ", cycle, "compute time: ", cycle/freq*1e3, "ms")
    # print("mem_time: ", mem_time*1e3, "ms")
    # print("----------bconv breakdown----------\n")
    return cycle


# Automorph
def automorph(limb):
    cycle = (limb*N/dp + spn_cycles)
    return cycle

def decomp(limb):
    cycle = modMult + limb*N/dp
    decomp_compute_time = cycle / freq
    read_time = limb * one_limb_size / HBM_bw
    write_time = limb * one_limb_size / HBM_bw
    # print("Decomp compute time: ", decomp_compute_time, "s")
    # print("Read time: ", read_time, "s")
    # print("Write time: ", write_time, "s")
    return cycle

def modup(pre_limb, new_limb):
    modup_intt_cycles = ntt(pre_limb)
    modup_bc_cycles = bconv(pre_limb, new_limb-pre_limb)
    modup_ntt_cycles = ntt(new_limb-pre_limb)
    cycles = modup_intt_cycles + modup_ntt_cycles + modup_bc_cycles
    return cycles

def moddown(in_limb, out_limb):
    moddown_intt_cycles = ntt(in_limb-out_limb)
    moddown_bc_cycles = bconv(in_limb-out_limb, out_limb)
    moddown_ntt_cycles = ntt(out_limb)
    moddown_extra_compute_cycles = (modMAC + N/dp) * out_limb
    cycles = moddown_intt_cycles + moddown_bc_cycles + moddown_extra_compute_cycles + moddown_ntt_cycles
    # print("----------moddown breakdown----------")
    # print("moddown_intt_cycles: ", moddown_intt_cycles)
    # print("moddown_bc_cycles: ", moddown_bc_cycles)
    # print("moddown_ntt_cycles: ", moddown_ntt_cycles)
    # print("moddown_extra_compute_cycles: ", moddown_extra_compute_cycles)
    # print("Moddown cycles: ", cycles, "Moddown time: ", cycles/freq*1e3, "ms")
    # print("----------moddown breakdown----------")
    return cycles

def innerprod(limb):
    # cycle = (modMult + limb * N/dp) + (modAdd + limb * N/dp)
    cycle = (modMult + modAdd + limb * N/dp)
    return cycle

# keyinnerprod: lightly compute-bound
def keyinnerprod(limb):
    compute_cycle = innerprod(2*beta*limb)
    ct_in_size = beta * limb * one_limb_size
    key_size = 2 * ct_size
    read_time = (ct_in_size + key_size) / HBM_bw
    ct_out_size = 2 * limb * one_limb_size
    write_time = ct_out_size / HBM_bw
    mem_time = read_time + write_time
    # print("----------keyinnerprod breakdown----------")
    # print("compute_cycle: ", compute_cycle, "compute time: ", compute_cycle/freq*1e3, "ms")
    # print("mem_time: ", mem_time*1e3, "ms")
    # print("----------keyinnerprod breakdown----------\n")
    return compute_cycle

def keyswitch(pre_limb, new_limb):
    decomp_cycles = decomp(pre_limb)
    modup_cycles = beta*modup(pre_limb/beta, new_limb)
    keyinnerprod_cycles = keyinnerprod(new_limb)
    moddown_cycles = 2*moddown(new_limb, pre_limb)
    cycle = decomp_cycles + modup_cycles + keyinnerprod_cycles + moddown_cycles
    print("----------keyswitch breakdown----------")
    print("decomp_cycles: ", decomp_cycles, "%: ", decomp_cycles/cycle)
    print("modup_cycles: ", modup_cycles, "%: ", modup_cycles/cycle)
    print("keyinnerprod_cycles: ", keyinnerprod_cycles, "%: ", keyinnerprod_cycles/cycle)
    print("moddown_cycles: ", moddown_cycles, "%: ", moddown_cycles/cycle)
    print("----------keyswitch breakdown----------\n")
    return cycle

if __name__ == "__main__":
    cycle = keyswitch(L+1, L+k+1)
    print("keyswitch cycle: ", cycle, "time: ", cycle/freq*1e3, "ms")