import math


logN = 16
N = 2**logN
n = N/2
fftiter = 4
rdx = 2**((logN-1)/fftiter)
r = 2*rdx-1
poly_level = 7
beta = 3
print("r: ", r, "rdx: ", rdx, "poly_level: ", poly_level, "beta: ", beta)

# FEB: logPQ = 1728; logQ=1242; same as FAB
# dp = 512
# L = 38
# k = 16
# logq = 32
# beta = 3

# dp = 512
# L = 38
# k = 14
# logq = 32
# beta = 3

# FAB
# dp = 256
# L = 22
# k = 9
# logq = 54
# beta = 3

# FAB & GPU: logPQ = 2364; logQ=1693
dp = 512
L = 54
k = 13
logq = 32
beta = 3
# dp = 256
# L = 32
# k = 13
# logq = 54
# beta = 3


# Poseidon & GPU: logPQ=2366; logQ=2305
# dp = 512
# L = 44
# k = 1
# logq = 32
# beta = 45

# HEAX: logQ=438
# N = 2**14
# dp = 512
# logq = 32
# L = 13
# k = 0
# beta = 3

freq = 300e6
modMult = 11 # 5
modAdd = 2
modMAC = 13
spn_cycles = 2*math.log2(dp) + N/dp;


one_limb_size = N * logq / 8 
ct_size = 2 * L * one_limb_size
pt_size = L * one_limb_size
ct_size_max = 2 * (L+k+1) * one_limb_size
one_key_size = (L+k+1) * one_limb_size * 2*beta


one_fifo_size = 128 * 32 # Byte
total_fifo_size = one_fifo_size * 32 # Byte
# print("one fifo size: ", one_fifo_size, "Byte")
# print("total fifo size: ", total_fifo_size, "Byte")
# HBM_bw = 13.27 * 32 * 10**9 # 425 GB/s
HBM_bw = 425 * 10**9 # 425 GB/s
HBM_freq = 450 * 10**6 # 450 MHz
# hbm_fifo_time = total_fifo_size / HBM_bw
# hbm_fifo_cycle = hbm_fifo_time * HBM_freq
# print("hbm fifo time: ", hbm_fifo_time, "s")
# print("hbm fifo cycle: ", hbm_fifo_cycle, "cycle")

fifo_bram_cycle = 128
hbm_read_bw = total_fifo_size / fifo_bram_cycle # Byte/cycle
read_one_limb_off = one_limb_size / hbm_read_bw
read_one_limb_off_time = read_one_limb_off / freq



# buffer_read_bw = dp * logq / 8
# read_one_limb_on = one_limb_size / buffer_read_bw
# print("read one limb_on: ", read_one_limb_on, "cycle")

read_one_limb_thrpt_time = one_limb_size / HBM_bw


one_limb_mult_cycle = modMult + N/dp
one_limb_mult_time = one_limb_mult_cycle / freq


ct_pt_mult_cycle = modMult + L*N/dp
ct_pt_mult_time = ct_pt_mult_cycle / freq
read_pt_time = pt_size / HBM_bw
read_ct_pt_time = (ct_size + pt_size) / HBM_bw
read_ct_time = ct_size / HBM_bw
read_ct_max_time = ct_size_max / HBM_bw
read_key_time = one_key_size / HBM_bw
# print("read ct time: ", read_ct_time*1e3, "ms")
print("one limb size: ", one_limb_size/1e6, "MB")
print("ct size: ", ct_size/1e6, "MB")
# print("pt size: ", pt_size/1e6, "MB")
print("ct size max: ", ct_size_max/1e6, "MB")
# print("one key size: ", one_key_size/1e6, "MB")

# print("hbm read bw: ", hbm_read_bw, "Byte/cycle")
# print("read one limb_off: ", read_one_limb_off, "cycle")
# print("read one limb_off time: ", read_one_limb_off_time, "s")
# print("read one limb_thrpt: ", read_one_limb_thrpt_time*1e3, "ms")
# print("one limb mult cycle: ", one_limb_mult_cycle, "cycle")
# print("one limb mult time: ", one_limb_mult_time*1e3, "ms")


# print("ct-pt mult time: ", ct_pt_mult_time, "s")
# print("read 2 ct time: ", read_ct_pt_time, "s")
# conclusion: ct-pt mult is memory-bound

print("spn cycles: ", spn_cycles)