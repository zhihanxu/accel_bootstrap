from operations import *

# ciphertext class
class ciphertext:
    def __init__(self, degree, level, logq):
        self.degree = degree
        self.level = level
        self.logq = logq
        self.digit = 1
    
    # ciphertext size in mega bytes
    def size(self):
        return 2 * self.degree * self.level * self.logq * self.digit / (8 * 10**6)
    
    def decomp(self):
        self.digit = beta
        
    def rescale(self):
        self.level -= 1
    
    def modup(self):
        self.level += k
        
    def moddown(self):
        self.level -= k
    
    def key_size(self):
        return 2 * self.degree * self.level * self.logq * beta / (8 * 10**6)
    
    def keyswitch(self):
        self.digit = 0


print("one limb size: ", L * N * logq / (8 * 10**6), "MB\n")

n = 25        
# Pre n1 rotations:
n1 = 5
n2 = 5
ct = ciphertext(N, L, logq)
ct.decomp()
ct.modup()
print("Input size of ct: ", ct.size(), "MB")
single_key_size = ct.key_size()
all_key_size = single_key_size * n1
print("Input size of a key: ", single_key_size, "MB\n", "all key size: ", all_key_size, "MB")
mem_read = ct.size() + all_key_size
print("Memory read: ", mem_read, "MB")
mem_write = (n1-1) * ct.size()
print("Memory write: ", mem_write, "MB\n")


# BSGS main steps:
diag_size = n * ct.size()
print("Diagonal size: ", diag_size, "MB")

input_ct_read = n * ct.size() + n2 * ct.size()
key_read = n2 * single_key_size
output_ct_write = n2 * ct.size()
print("Input ciphertext read: ", input_ct_read, "MB")
print("Key read: ", key_read, "MB")
print("Output ciphertext write: ", output_ct_write, "MB")

mem_read_BSGS = diag_size + input_ct_read + key_read
mem_write_BSGS = output_ct_write
print("Memory read BSGS: ", mem_read_BSGS, "MB")
print("Memory write BSGS: ", mem_write_BSGS, "MB\n")


key_read_all = all_key_size + key_read
print("Key read all: ", key_read_all, "MB")


        


