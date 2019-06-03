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


def is_prime(n, k):
    if n == 2:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_key_pairs(key_length):
    p = random.randrange(1 << int(0.5*key_length-1), 1 << int(0.5*key_length))
    while is_prime(p, 40) is not True:
        p = random.randrange(1 << int(0.5*key_length-1), 1 << int(0.5*key_length))

    e = 65537

    q = random.randrange(1 << int(0.5*key_length-1), 1 << int(0.5*key_length))
    while is_prime(q, 40) is not True or q == p or gcd(e, phi) != 1:
        q = random.randrange(1 << int(0.5*key_length-1), 1 << int(0.5*key_length))
        if p < q:
            p, q = q, p

            n = p*q
            phi = (p-1)*(q-1)

    for k in range(0, e):
        d = (1 + k*phi) / e
        if d.is_integer():
            d = int(d)
            break

    print("PUBLIC KEY: ", n, e)
    print("PRIVATE KEY: ", n, d)

    return [n, e, d]


generate_key_pairs(64)
