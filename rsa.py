import math
import random


def is_prime(n):
    if n % 2 == 0 or n % 5 == 0:
        return False
    for i in range(3, int(math.sqrt(n)+1), 2):
        if n % i == 0:
            return False
    return True


def are_relatively_prime(a, b):
    for n in range(2, min(a, b) + 1):
        if a % n == b % n == 0:
            return False
    return True


def generate_key_pair(key_length):
    minimum = 1 << (key_length - 1)
    maximum = 1 << (key_length + 1)

    p = random.randint(math.pow(2, (key_length//2) - 1), math.pow(2, (key_length//2) + 1))
    q = random.randint(math.pow(2, (key_length//2) - 1), math.pow(2, (key_length//2) + 1))

    print("INITIAL P: " + str(p))
    print("INITIAL Q: " + str(q))

    while not is_prime(p):
        p = random.randint(math.pow(2, (key_length//2) - 1), math.pow(2, (key_length//2) + 1))
    while not is_prime(q) or not (minimum <= p*q <= maximum) or (q == p):
        q = random.randint(math.pow(2, (key_length//2) - 1), math.pow(2, (key_length//2) + 1))

    print("FINAL P: " + str(p))
    print("FINAL Q: " + str(q))

    for e in range(3, (p-1)*(q-1), 2):
        if are_relatively_prime(e, (p-1)*(q-1)):
            break

    print("E: " + str(e))

    for d in range(3, (p-1)*(q-1), 2):
        if d * e % (p-1)*(q-1) == 1:
            break

    print("D: " + str(d))


generate_key_pair(16)
