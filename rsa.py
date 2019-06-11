import random


def gcd(a, b):
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    if b > a:
        a, b = b, a
    while b > 0:
        a, b = b, a % b
    return a


def rabin_miller(num):
    s = num - 1
    t = 0
    while s % 2 == 0:
        s = s // 2
        t += 1

    for trials in range(40):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % num
    return True


def is_prime(num):
    if num < 2:
        return False
    low_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
                  103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
                  211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
                  331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
                  449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577,
                  587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
                  709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839,
                  853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983,
                  991, 997]
    if num in low_primes:
        return True
    for prime in low_primes:
        if num % prime == 0:
            return False
    return rabin_miller(num)


def mod(num, a):
    res = 0
    for i in range(0, len(num)):
        res = (res * 10 + int(num[i])) % a
    return res


def generate_key_pairs(key_length):

    while True:
        p = random.randrange(1 << int(0.5 * key_length - 1), 1 << int(0.5 * key_length))
        if is_prime(p):
            break

    e = 65537
    phi = 0

    while True:
        q = random.randrange(1 << int(0.5*key_length-1), 1 << int(0.5*key_length))
        n = p*q
        phi = (p-1)*(q-1)
        if is_prime(q) and q != p and gcd(e, phi) == 1:
            break

    if q > p:
        p, q = q, p

    # print("FINAL P:", p)
    # print("FINAL Q:", q)

    mod_inv = lambda a, b, s=1, t=0, N=0: (b < 2 and t % N or mod_inv(b, a % b, t, s - a // b * t, N or b), -1)[b < 1]

    d = mod_inv(e, phi)

    # print("PUBLIC KEY: ", hex(n), hex(e))
    # print("PRIVATE KEY: ", hex(n), hex(d))
    # print("P: ", p, " Q: ", q, " N: ", n, "D: ", d)

    return [n, e, d]


def rsa_encode(n, e, data):
    encoded_data = pow(data, e, n)
    return encoded_data


def rsa_decode(n, d, data):
    decoded_data = pow(data, d, n)
    return decoded_data


[key, public_key, private_key] = generate_key_pairs(256)
m = b'\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
m = int.from_bytes(m, byteorder="big")

encoded = rsa_encode(key, public_key, m)
print(encoded.to_bytes(32, byteorder="big"))
decoded = rsa_decode(key, private_key, encoded)
print(decoded.to_bytes(32, byteorder="big"))


