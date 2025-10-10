from parameters import *

# degree of the polynomial
d = 24

#consumed levels
level_consumed = math.ceil(math.log2(d))
print("level consumed: ", level_consumed)

# m: smallest integer such that 2^m > d
m = math.ceil(math.log2(d+1))
print("m: ", m)

l = math.floor(m/2)
print("l: ", l)

# T_a(x) = 2*x * T_a-1(x) - T_{a-2}(x)
# T0(x) = 1
# T1(x) = x
# T2(x) = 2x^2 - 1 
# T3(x) = 4x^3 - 3x 

# T4(x) = 8x^4 - 8x^2 + 1
# T8(x) = 128x^8 - 256x^6 + 160x^4 - 32x^2 + 1
# T16(x) = 32768x^16 - 131072x^14 + 218368x^12 - 196608x^10 + 98560x^8 - 27440x^6 + 4112x^4 - 272x^2 + 1 

# non-scalar multiplication: 9
# x^2, x^3, x^4, x^6, x^8, x^10, x^12, x^14, x^16

# scalar multiplication: 16
# 2x^2, 8x^2, 32x^2, 272x^2, 8x^4, 160x^4, 4112x^4, 32x^6, 256x^6, 27440x^6, 128x^8, 98560x^8, 131072x^8, 196608x^10, 218368x^12, 32768x^16


# p(x) = (c00*T0(X) + c01*T1(x) + c02*T1(x) + c03*T2(x) + c03*T3(x))T4(x) + (c10*T0(X) + c11*T1(x) + c12*T1(x) + 
#         c13*T2(x) + c14*T3(x))T8(x) + (c20*T0(X) + c21*T1(x) + c22*T1(x) + c23*T2(x) + c24*T3(x))T16(x)

# p(x) = q(x) * T16(x) + r(x)

# q(x) = a1(x) * T8(x) + a2(x)
# q2(x) = a3(x) * T4(x) + a4(x)
# q3(x) = a5(x) * T2(x) + a6(x)
# q4(x) = a7(x) * T1(x) + a8(x)
# q5(x) = a9(x) * T0(x) + a10(x)

# r(x) = b1(x) * T8(x) + b2(x)
# r2(x) = b3(x) * T4(x) + b4(x)
# r3(x) = b5(x) * T2(x) + b6(x)
# r4(x) = b7(x) * T1(x) + b8(x)
# r5(x) = b9(x) * T0(x) + b10(x)




# T5(x) = 16x^5 - 20x^3 + 5x
# T6(x) = 32x^6 - 48x^4 + 18x^2 - 1
# T7(x) = 64x^7 - 112x^5 + 56x^3 - 7x
# T8(x) = 128x^8 - 256x^6 + 160x^4 - 32x^2 + 1
# T9(x) = 256x^9 - 576x^7 + 432x^5 - 120x^3 + 9x
# T10(x) = 512x^10 - 1280x^8 + 1120x^6 - 400x^4 + 50x^2 - 1
# T11(x) = 1024x^11 - 2816x^9 + 2816x^7 - 1232x^5 + 220x^3 - 11x
# T12(x) = 2048x^12 - 6144x^10 + 6912x^8 - 3584x^6 + 840x^4 - 72x^2 + 1
# T13(x) = 4096x^13 - 13312x^11 + 16640x^9 - 9984x^7 + 2912x^5 - 364x^3 + 13x
# T14(x) = 8192x^14 - 28672x^12 + 39424x^10 - 26880x^8 + 9408x^6 - 1568x^4 + 98x^2 - 1
# T15(x) = 16384x^15 - 61440x^13 + 92160x^11 - 70400x^9 + 28160x^7 - 5888x^5 + 560x^3 - 15x
# T16(x) = 32768x^16 - 131072x^14 + 218368x^12 - 196608x^10 + 98560x^8 - 27440x^6 + 4112x^4 - 272x^2 + 1





# Chebysev polynomial evaluation: T_a+b(x) = 2*T_a(x) * T_b(x) - T_{a-b}(x)
def poly_eval_cheby(p, x):
    if p == 0:
        return 1
    elif p == 1:
        return x
    else:
        return 2 * x * poly_eval_cheby(p-1, x) - poly_eval_cheby(p-2, x)

# Chebysev polynomial evaluation: T_a+b(x) = 2*T_a(x) * T_b(x) - T_{a-b}(x)
def chebyshev_iterative(p, x):
    if p == 0:
        return 1
    elif p == 1:
        return x
    else:
        T_prev = 1
        T_curr = x
        for i in range(2, p + 1):
            T_next = 2 * x * T_curr - T_prev
            T_prev = T_curr
            T_curr = T_next
        return T_curr


