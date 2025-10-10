from subroutines import *

eval = 1
eval_hmult = eval
eval_hadd = eval
eval_rotate = eval
eval_rescale = eval
eval_pmult = eval

def hmult(limb):
    mult_cycle = (modMult + 2*N*limb/dp)
    mac_cycle = (modMAC + 2*N*limb/dp)
    keyswitch_cycle = keyswitch(limb, limb+k)
    add2_cycle = (modAdd + 2*N*limb/dp) 
    hmult_cycle = mult_cycle + mac_cycle + keyswitch_cycle + add2_cycle
    mem_time = read_ct_time * 3
    throughput = 1 / (hmult_cycle/freq)
    if (eval_hmult):
        print("----------hmult breakdown ----------")
        print("mult_cycle: ", mult_cycle, "%: ", mult_cycle/hmult_cycle)
        print("mac_cycle: ", mac_cycle, "%: ", mac_cycle/hmult_cycle)
        print("keyswitch_cycle: ", keyswitch_cycle, "%: ", keyswitch_cycle/hmult_cycle)
        print("add2_cycle: ", add2_cycle, "%: ", add2_cycle/hmult_cycle)
        print("Hmult cycles: ", hmult_cycle, "hmult time: ", hmult_cycle/freq*1e3, "ms")
        print("mem_time: ", mem_time*1e3, "ms")
        print("throughput: ", throughput, "op/s")
        print("----------hmult breakdown----------\n")
    return hmult_cycle
    
def pmult(limb):
    compute_cycle = modMult + 2*N*limb/dp
    compute_time = compute_cycle / freq
    mem_time = read_ct_pt_time# read ct pt; write ct\
    if eval_pmult:
        print("----------pmult breakdown----------")
        print("compute_cycle: ", compute_cycle, "compute time: ", compute_time*1e3, "ms")
        print("mem_time: ", mem_time*1e3, "ms")
        print("----------pmult breakdown----------\n")
    return compute_cycle

def cmult(limb):
    compute_cycle = modMult + 2*N*limb/dp
    compute_time = compute_cycle / freq
    mem_time = read_ct_time * 2
    # print("----------cmult breakdown----------")
    # print("compute_cycle: ", compute_cycle, "compute time: ", compute_time*1e3, "ms")
    # print("mem_time: ", mem_time*1e3, "ms")
    # print("----------cmult breakdown----------\n")
    return compute_cycle

def rotate(limb):
    permute_cycle = spn_cycles + 2 * limb * N/dp
    keyswitch_cycle = keyswitch(limb,limb+k)
    add_cycle = modAdd + limb*N/dp
    cycle = permute_cycle + keyswitch_cycle + add_cycle
    if eval_rotate:
        print("----------rotate breakdown----------")
        print("permute_cycle: ", permute_cycle)
        print("keyswitch_cycle: ", keyswitch_cycle)
        print("add_cycle: ", add_cycle)
        print("Rotate cycles: ", cycle, "Rotate time: ", cycle/freq*1e3, "ms")
        print("----------rotate breakdown----------\n")
    return cycle

def hrotate(limb, loop):
    cycle = 0
    cycle += decomp(limb)
    cycle += beta*modup(limb/beta, limb+k)
    for i in range(loop):
        cycle += beta*automorph(limb+k)
        cycle += automorph(limb)
        cycle += keyinnerprod(limb+k)
        cycle += 2*moddown(limb+k, limb)
        cycle += hadd(limb)
    return cycle

def conjugate(limb):
    permute_cycle = spn_cycles + 2 * limb * N/dp
    keyswitch_cycle = keyswitch(limb,limb+k)
    add_cycle = modAdd + limb*N/dp
    cycle = permute_cycle + keyswitch_cycle + add_cycle
    return cycle

def hadd(limb):
    compute_cycle = modAdd + 2*N*limb/dp
    compute_time = compute_cycle / freq
    mem_time = read_ct_time * 2     # 2 read ct, 1 write ct
    if eval_hadd:
        print("----------hadd breakdown----------")
        print("compute_cycle: ", compute_cycle, "compute time: ", compute_time*1e3, "ms")
        print("mem_time: ", mem_time*1e3, "ms")
        print("----------hadd breakdown----------\n")
    return compute_cycle

def rescale(limb):
    compute_cycle = moddown(limb, limb-1)
    compute_time = compute_cycle / freq
    mem_time = read_ct_time * 3
    if eval_rescale:
        print("----------rescale breakdown----------")
        print("compute_cycle: ", compute_cycle, "compute time: ", compute_time*1e3, "ms")
        print("mem_time: ", mem_time*1e3, "ms")
        print("----------rescale breakdown----------\n")
    return compute_cycle


def linear_transform_one_iter(limb):
    read_time = 2*limb * one_limb_size / HBM_bw
    decomp_cycle = decomp(limb)
    iter_cycle = 0
    for i in range(limb+k+1):
        if (i<limb+1):
            bconv_cycle = (beta-1)*bconv(limb/beta, 1) + bconv(limb, 1)
        else:
            bconv_cycle = beta*bconv(limb/beta, 1) + bconv(limb, 1)
        keyinnerprod_cycle = innerprod(2*beta)
        automorph_cycle = automorph(beta+1)
        padd_cycle = modAdd + 2*N*limb/dp
        diaginnerprod_cycle = innerprod(2*r)
        iter_cycle += (bconv_cycle + keyinnerprod_cycle + automorph_cycle + padd_cycle + diaginnerprod_cycle)
    moddown_cycle = moddown(limb+k+1, limb)
    cycle = decomp_cycle + iter_cycle + moddown_cycle
    # print("----------linear_transform breakdown----------")
    # print("decomp_cycle: ", decomp_cycle)
    # print("bconv_cycle: ", bconv_cycle)
    # print("keyinnerprod_cycle: ", keyinnerprod_cycle)
    # print("automorph_cycle: ", automorph_cycle)
    # print("padd_cycle: ", padd_cycle)
    # print("diaginnerprod_cycle: ", diaginnerprod_cycle)
    # print("iter_cycle: ", iter_cycle)
    # print("moddown_cycle: ", moddown_cycle)
    # print("Linear Transform cycles: ", cycle, "Linear Transform time: ", cycle/freq*1e3, "ms")
    # print("----------linear_transform breakdown----------\n")
    return cycle

def linear_transform(limb):
    cycle = 0
    for i in range(fftiter):
        cycle += linear_transform_one_iter(limb)
        limb-=1
    cycle += conjugate(limb) + hadd(limb)
    # print("Linear Transform cycles: ", cycle, "Linear Transform time: ", cycle/freq*1e3, "ms")
    return cycle

def poly_eval(limb):
    # read_T1_cycle = read_ct_time * freq
    # print("read T1 cycle: ", read_T1_cycle)
    compute_T2_cycle = hmult(limb)+hadd(limb)
    moddown_T1_cycle = moddown(limb, limb-2)
    rescale_T2_cycle = rescale(limb)
    compute_T3_cycle = hmult(limb-1)+hadd(limb-1)
    moddown_T2_cycle = moddown(limb-1, limb-2)
    rescale_T3_cycle = rescale(limb-1)
    compute_T4_cycle = compute_T3_cycle
    rescale_T4_cycle = rescale_T3_cycle
    T1_cycle = moddown_T1_cycle
    T2_cycle = compute_T2_cycle + moddown_T2_cycle + rescale_T2_cycle
    T3_cycle = compute_T3_cycle + rescale_T3_cycle
    T4_cycle = compute_T4_cycle + rescale_T4_cycle
    linear_combine_cycle = 8 * (4 * cmult(limb-2) + 3 * hadd(limb-2))
    # linear_combine_cycle = 8 * (4 * innerprod(limb-2))
    # recurse to upper levels
    compute_T8_cycle = 4 * rescale(limb-2) + 4 * (hmult(limb-2)+hadd(limb-4)) + 4 * moddown(limb-2, limb-4)
    compute_T16_cycle = 2 * rescale(limb-3) + 2 * (hmult(limb-3)+hadd(limb-4))
    compute_p_cycle = 1 * rescale(limb-4) + hmult(limb-4) + hadd(limb-5)
    poly_eval_cycle = T1_cycle+T2_cycle+T3_cycle+T4_cycle+linear_combine_cycle+compute_T8_cycle+compute_T16_cycle+compute_p_cycle
    # print("poly eval cycles: ", poly_eval_cycle, "poly eval time: ", poly_eval_cycle/freq*1e3, "ms")
    return poly_eval_cycle

def poly_eval_m4(limb):
    # read_T1_cycle = read_ct_time * freq
    # print("read T1 cycle: ", read_T1_cycle)
    compute_T2_cycle = hmult(limb)+hadd(limb)
    moddown_T1_cycle = moddown(limb, limb-2)
    rescale_T2_cycle = rescale(limb)
    compute_T3_cycle = hmult(limb-1)+hadd(limb-1)
    moddown_T2_cycle = moddown(limb-1, limb-2)
    rescale_T3_cycle = rescale(limb-1)
    compute_T4_cycle = compute_T3_cycle
    rescale_T4_cycle = rescale_T3_cycle
    T1_cycle = moddown_T1_cycle
    T2_cycle = compute_T2_cycle + moddown_T2_cycle + rescale_T2_cycle
    T3_cycle = compute_T3_cycle + rescale_T3_cycle
    T4_cycle = compute_T4_cycle + rescale_T4_cycle
    linear_combine_cycle = 4 * (4 * cmult(limb-2) + 3 * hadd(limb-2))
    # recurse to upper levels
    compute_T8_cycle = 4 * rescale(limb-2) + 2 * (hmult(limb-2)+hadd(limb-3))
    compute_p_cycle = hmult(limb-3) + hadd(limb-4)
    poly_eval_cycle = T1_cycle+T2_cycle+T3_cycle+T4_cycle+linear_combine_cycle+compute_T8_cycle+compute_p_cycle
    # print("poly eval cycles: ", poly_eval_cycle, "poly eval time: ", poly_eval_cycle/freq*1e3, "ms")
    return poly_eval_cycle


def bootstrap():
    cmult_cycle = cmult(fftiter+1) + cmult(L+1-fftiter-poly_level)
    stc_cycle = linear_transform(fftiter+1)
    modup_cycle = modup(1,L+1)
    cts_cycle = linear_transform(L+1)
    conjugate_cycle = conjugate(L+1-fftiter) + hadd(L+1-fftiter) + cmult(L+1-fftiter)
    poly_eval_cycle = poly_eval(L+1-fftiter)
    other_cycle = cmult_cycle + modup_cycle + conjugate_cycle
    boot_cycle = other_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    # print("-----------------Bootstrap starts-----------------")
    # print("cmult cycle: ", cmult_cycle)
    # print("StC cycle: ", stc_cycle)
    # print("modup cycle: ", modup_cycle)
    # print("cts cycle: ", cts_cycle)
    # print("conjugate cycle: ", conjugate_cycle)
    # print("poly eval cycle: ", poly_eval_cycle)
    # print("other cycle: ", other_cycle)
    # print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    # level = L-2*fftiter-poly_level
    # mult_cycle = 0
    # for i in range(level):
    #     mult_cycle += hmult(level-i+1)
    # print("mult cycle: ", mult_cycle)
    # amortized_cycle = (boot_cycle+mult_cycle)/(level*n)
    # print("amortized cycle: ", amortized_cycle, "time: ", amortized_cycle/freq*1e6, "us")
    # print("-----------------Bootstrap ends-----------------")
    return boot_cycle
    
def bootstrap_limb(l):
    cmult_cycle = cmult(l) + cmult(L+1-fftiter-poly_level)
    stc_cycle = linear_transform(l)
    modup_cycle = modup(l-fftiter,L+1)
    cts_cycle = linear_transform(L+1)
    conjugate_cycle = conjugate(L+1-fftiter) + hadd(L+1-fftiter) + cmult(L+1-fftiter)
    poly_eval_cycle = poly_eval(L+1-fftiter)
    other_cycle = cmult_cycle + modup_cycle + conjugate_cycle
    boot_cycle = other_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    # print("cmult cycle: ", cmult_cycle)
    # print("StC cycle: ", stc_cycle)
    # print("modup cycle: ", modup_cycle)
    # print("cts cycle: ", cts_cycle)
    # print("conjugate cycle: ", conjugate_cycle)
    # print("poly eval cycle: ", poly_eval_cycle)
    # print("other cycle: ", other_cycle)
    # print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    return boot_cycle
    
if __name__ == "__main__":
    print("-------Profiling Starts-----\n")
    if eval:
        hmult(L+1)
        pmult(L+1)
        keyinnerprod(L+1)
        rotate(L+1)
        hadd(L+1)
        rescale(L+1)
    # bootstrap()
     

        