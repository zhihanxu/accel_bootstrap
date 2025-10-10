from operations import *
import math

r1 = math.ceil(math.log2(r))
r2 = math.floor(r/r1)
print("r: ", r, "r1: ", r1, "r2: ", r2)


def bsgs_no_hoist_one_iter(limb):
    compute_cycle = 0
    for i in range(r1):
        compute_cycle += 2*rotate(limb)
    
    for j in range(r2):
        for i in range(r1):
            compute_cycle += 2*(pmult(limb) + hadd(limb))
        compute_cycle += 2*rotate(limb)
        compute_cycle += 2*hadd(limb)
        
    compute_cycle += 2*rescale(limb)
    print("----------bsgs_no_hoist_one_iter breakdown----------")
    print("compute_cycle: ", compute_cycle, "compute time: ", compute_cycle/freq*1e3, "ms")
    print("----------bsgs_no_hoist_one_iter breakdown----------\n")
    return compute_cycle
        

def bsgs_hoist_one_iter(limb):
    cycle = decomp(limb)
    cycle += beta*modup(limb/beta,limb+k) + 2*modup(limb,limb+k)
    for i in range(r1):
        cycle += 2*automorph(limb+k)
        # cycle += automorph(2*(limb+k))
        cycle += hadd(limb+k)
        cycle += 2*keyinnerprod(limb+k)
        # cycle += keyinnerprod(2*(limb+k))
        
    for j in range(r2):
        for i in range(r1):
            # cycle += 2*(pmult(limb) + hadd(limb)) # matter much
            cycle += 2*innerprod(limb)
        cycle += moddown(limb+k,limb)
        cycle += decomp(limb)
        cycle += beta*modup(limb/beta,limb+k)
        cycle += 2*automorph(limb+k)  # matter little
        # cycle += automorph(2*(limb+k))
        cycle += hadd(limb+k)
        cycle += 2*keyinnerprod(limb+k)   # matter little
        # cycle += keyinnerprod(2*(limb+k))
    
    cycle += 2*moddown(limb+k,limb)
    cycle += 2*rescale(limb)
    
    # print("----------bsgs_linear breakdown----------")
    # print("compute_cycle: ", cycle, "compute time: ", cycle/freq*1e3, "ms")
    # print("----------bsgs_linear breakdown----------\n")
    return cycle

def bsgs_all_iter(limb):
    cycle = 0
    for i in range(fftiter):
        cycle += bsgs_hoist_one_iter(limb)
        limb-=1
    # print("Linear Transform cycles: ", cycle, "Linear Transform time: ", cycle/freq*1e3, "ms")
    return cycle


def base_poly_eval(limb):
    compute_T2_cycle = hmult(limb)+hadd(limb)
    rescale_T1_cycle = rescale(limb)
    rescale_T2_cycle = rescale(limb)
    compute_T3_cycle = hmult(limb-1)+hadd(limb-1)
    moddown_T2_cycle = moddown(limb-1, limb-2)
    moddown_T1_cycle = moddown(limb, limb-2)
    rescale_T3_cycle = rescale(limb-1)
    compute_T4_cycle = compute_T3_cycle
    rescale_T4_cycle = rescale_T3_cycle
    T1_cycle = moddown_T1_cycle + rescale_T1_cycle
    T2_cycle = compute_T2_cycle + moddown_T2_cycle + rescale_T2_cycle
    T3_cycle = compute_T3_cycle + rescale_T3_cycle
    T4_cycle = compute_T4_cycle + rescale_T4_cycle
    linear_combine_cycle = 8 * (4 * cmult(limb-2) + 3 * hadd(limb-2))
    # linear_combine_cycle = 8 * (4 * innerprod(limb-2))
    # recurse to upper levels
    compute_T8_cycle = 8 * rescale(limb-2) + 4 * (hmult(limb-2)+hadd(limb-3))
    compute_T16_cycle = 4 * rescale(limb-3) + 2 * (hmult(limb-3)+hadd(limb-4))
    compute_p_cycle = 2 * rescale(limb-4) + hmult(limb-4) + hadd(limb-5)
    poly_eval_cycle = T1_cycle+T2_cycle+T3_cycle+T4_cycle+linear_combine_cycle+compute_T8_cycle+compute_T16_cycle+compute_p_cycle
    print("base poly eval cycles: ", poly_eval_cycle, "poly eval time: ", poly_eval_cycle/freq*1e3, "ms")
    return poly_eval_cycle

def base_bootstrap():
    modup_cycle = modup(1,L+1)
    stc_cycle = bsgs_all_iter(L+1)
    poly_eval_cycle = base_poly_eval(L+1-fftiter)
    cts_cycle = bsgs_all_iter(L+1-fftiter-7)
    boot_cycle = modup_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    print("-----------------base Bootstrap starts-----------------")
    print("modup cycle: ", modup_cycle)
    print("StC cycle: ", stc_cycle)
    print("poly eval cycle: ", poly_eval_cycle)
    print("Cts cycle: ", cts_cycle)
    print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    print("-----------------base Bootstrap ends-----------------\n")
    return boot_cycle

def base_and_aba():
    cmult_cycle = cmult(fftiter+1) + cmult(L+1-fftiter-poly_level)
    stc_cycle = bsgs_all_iter(fftiter+1)
    modup_cycle = modup(1,L+1)
    cts_cycle = bsgs_all_iter(L+1)
    conjugate_cycle = conjugate(L+1-fftiter) + hadd(L+1-fftiter) + cmult(L+1-fftiter)
    poly_eval_cycle = base_poly_eval(L+1-fftiter)
    other_cycle = cmult_cycle + modup_cycle + conjugate_cycle
    boot_cycle = other_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    print("-----------------base and aba starts-----------------")
    print("cmult cycle: ", cmult_cycle)
    print("StC cycle: ", stc_cycle)
    print("modup cycle: ", modup_cycle)
    print("cts cycle: ", cts_cycle)
    print("conjugate cycle: ", conjugate_cycle)
    print("poly eval cycle: ", poly_eval_cycle)
    print("other cycle: ", other_cycle)
    print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    print("-----------------base and aba ends-----------------\n")
    return boot_cycle
    
def base_and_mehlt():
    modup_cycle = modup(1,L+1)
    stc_cycle = linear_transform(L+1)
    poly_eval_cycle = base_poly_eval(L+1-fftiter)
    cts_cycle = linear_transform(L+1-fftiter-7)
    boot_cycle = modup_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    print("-----------------base and mehlt starts-----------------")
    print("modup cycle: ", modup_cycle)
    print("StC cycle: ", stc_cycle)
    print("poly eval cycle: ", poly_eval_cycle)
    print("Cts cycle: ", cts_cycle)
    print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    print("-----------------base and mehlt ends-----------------\n")
    return boot_cycle

def base_and_poly():
    modup_cycle = modup(1,L+1)
    stc_cycle = bsgs_all_iter(L+1)
    poly_eval_cycle = poly_eval(L+1-fftiter)
    cts_cycle = bsgs_all_iter(L+1-fftiter-7)
    boot_cycle = modup_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    print("-----------------base and poly starts-----------------")
    print("modup cycle: ", modup_cycle)
    print("StC cycle: ", stc_cycle)
    print("poly eval cycle: ", poly_eval_cycle)
    print("Cts cycle: ", cts_cycle)
    print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    print("-----------------base and poly ends-----------------\n")
    return boot_cycle

def aba_and_mehlt():
    cmult_cycle = cmult(fftiter+1) + cmult(L+1-fftiter-poly_level)
    stc_cycle = linear_transform(fftiter+1)
    modup_cycle = modup(1,L+1)
    cts_cycle = linear_transform(L+1)
    conjugate_cycle = conjugate(L+1-fftiter) + hadd(L+1-fftiter) + cmult(L+1-fftiter)
    poly_eval_cycle = base_poly_eval(L+1-fftiter)
    other_cycle = cmult_cycle + modup_cycle + conjugate_cycle
    boot_cycle = other_cycle + stc_cycle + cts_cycle  + poly_eval_cycle
    print("-----------------mehlt and aba starts-----------------")
    print("cmult cycle: ", cmult_cycle)
    print("StC cycle: ", stc_cycle)
    print("modup cycle: ", modup_cycle)
    print("cts cycle: ", cts_cycle)
    print("conjugate cycle: ", conjugate_cycle)
    print("poly eval cycle: ", poly_eval_cycle)
    print("other cycle: ", other_cycle)
    print("total cycle: ", boot_cycle, "time: ", boot_cycle/freq*1e3, "ms")
    print("-----------------mehlt and aba ends-----------------\n")
    return boot_cycle

if __name__ == "__main__":
    # bsgs_no_hoist_one_iter(L)
    # bsgs_hoist_one_iter(L)
    base_bootstrap()
    # base_and_aba()
    base_and_mehlt()
    # base_and_poly()
    # aba_and_mehlt()
    
    # poly_eval(L+1-fftiter)
    # base_poly_eval(L+1-fftiter)