import random

class RSA:
    def __init__(self, key_length):
        self.keyLength = key_length
        self.publicKey = None
        self.privateKey = None

    def gcd(self, a, b):
        if a < 0:
            a = -a
        if b < 0:
            b = -b
        if b > a:
            a, b = b, a
        while b > 0:
            a, b = b, a % b
        return a

    def rabin_miller(self, num):
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

    def is_prime(self, num):
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
        return self.rabin_miller(num)

    def mod(self, num, a):
        res = 0
        for i in range(0, len(num)):
            res = (res * 10 + int(num[i])) % a
        return res

    def generate_key_pairs(self):
        while True:
            p = random.randrange(1 << int(0.5 * self.keyLength - 1), 1 << int(0.5 * self.keyLength))
            if self.is_prime(p):
                break

        e = 65537
        phi = 0

        while True:
            q = random.randrange(1 << int(0.5*self.keyLength-1), 1 << int(0.5*self.keyLength))
            n = p*q
            phi = (p-1)*(q-1)
            if self.is_prime(q) and q != p and self.gcd(e, phi) == 1:
                break

        if q > p:
            p, q = q, p

        mod_inv = lambda a, b, s=1, t=0, N=0: (b < 2 and t % N or mod_inv(b, a % b, t, s - a // b * t, N or b), -1)[b < 1]

        d = mod_inv(e, phi)

        self.publicKey = [n, e]
        self.privateKey = [n, d]

    def encode(self, data):
        encoded_data = pow(data, self.publicKey[1], self.publicKey[0])
        return encoded_data

    def decode(self, data):
        decoded_data = pow(data, self.privateKey[1], self.privateKey[0])
        return decoded_data


