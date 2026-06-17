import sys
import random
from typing import List, Tuple
from math import gcd

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPH_SIZE = len(ALPHABET)  # 32

punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}
space_repl = 'прб'

def prepare_text(txt: str) -> str:
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt

def restore_text(txt: str) -> str:
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def digitization(open_text: str) -> List[int]:
    return [ALPHABET.index(ch) + 1 for ch in open_text]

def undigitization(numbers: List[int]) -> str:
    return ''.join(ALPHABET[n-1] for n in numbers)

def decryption_format(dec_text: str) -> str:
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace(space_repl, ' ')
    if not dec_text:
        return ""
    result = dec_text[0].upper() + dec_text[1:]
    result_list = list(result)
    for i in range(len(result_list) - 2):
        if result_list[i] == ".":
            result_list[i+2] = result_list[i+2].upper()
    return ''.join(result_list)

# =====================================================================
# Вспомогательные математические функции
# =====================================================================
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def mod_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m

def input_int(prompt: str, low: int = None, high: int = None, is_prime_needed: bool = False) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if low is not None and val <= low:
                print(f"  [!] Число должно быть > {low}. Повторите.")
                continue
            if high is not None and val >= high:
                print(f"  [!] Число должно быть < {high}. Повторите.")
                continue
            if is_prime_needed and not is_prime(val):
                print("  [!] Число должно быть простым. Повторите.")
                continue
            return val
        except ValueError:
            print("  [!] Введите целое число.")

def input_positive(prompt: str) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if val > 0:
                return val
            print("  [!] Введите положительное число.")
        except ValueError:
            print("  [!] Введите целое число.")

def input_point(prompt: str, p: int) -> Tuple[int, int]:
    while True:
        try:
            s = input(prompt).strip().replace('(', '').replace(')', '').replace(',', ' ')
            parts = s.split()
            if len(parts) != 2:
                raise ValueError()
            x = int(parts[0])
            y = int(parts[1])
            if 0 <= x < p and 0 <= y < p:
                return (x, y)
            print(f"  [!] Координаты должны быть в [0, {p-1}].")
        except ValueError:
            print("  [!] Введите точку в формате x y или (x, y).")

# =====================================================================
# RSA
# =====================================================================
def rsa_encrypt(plain_numbers: List[int], n: int, e: int) -> List[int]:
    return [pow(m, e, n) for m in plain_numbers]

def rsa_decrypt(cipher_numbers: List[int], n: int, d: int) -> List[int]:
    return [pow(c, d, n) for c in cipher_numbers]

def rsa_cipher(operation: int, text: str) -> None:
    if operation == 1:
        print("\n--- Параметры RSA (шифрование) ---")
        p = input_int("Введите простое число P: ", low=1, is_prime_needed=True)
        q = input_int("Введите простое число Q (отличное от P): ", low=1, is_prime_needed=True)
        if p == q:
            raise ValueError("P и Q должны быть различными")
        n = p * q
        if n < ALPH_SIZE:
            raise ValueError(f"n = {n} должно быть больше {ALPH_SIZE}")
        phi = (p-1)*(q-1)
        print(f"φ(N) = {phi}")
        e = input_int(f"Введите число E (1 < E < {phi}, взаимно простое с φ): ", low=1, high=phi)
        while True:
            while gcd(e, phi) != 1:
                print(f"  [!] E и φ(N) не взаимно просты. Введите другое E.")
                e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
            d = mod_inverse(e, phi)
            if d == e:
                print("  [!] E и D совпали. Это нежелательно. Введите другое E.")
                e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
            else:
                break
        plain_numbers = digitization(text)
        cipher_numbers = rsa_encrypt(plain_numbers, n, e)
        print(f"\nОткрытый ключ: N = {n}, E = {e}")
        print(f"Секретный ключ (d) = {d} (сохраните для расшифровки)")
        print("Зашифрованный текст (числа):", ' '.join(str(c) for c in cipher_numbers))
    else:
        print("\n--- Параметры RSA (расшифрование) ---")
        n = input_positive("Введите N: ")
        d = input_positive("Введите секретный ключ d: ")
        cipher_numbers = [int(x) for x in text.split()]
        plain_numbers = rsa_decrypt(cipher_numbers, n, d)
        plain_letters = undigitization(plain_numbers)
        restored = decryption_format(plain_letters)
        print("\nРасшифрованный текст:", restored)

# =====================================================================
# ElGamal
# =====================================================================
def elgamal_encrypt(plain_numbers: List[int], p: int, g: int, y: int) -> List[int]:
    result = []
    for m in plain_numbers:
        k = random.randint(2, p-2)
        while gcd(k, p-1) != 1:
            k = random.randint(2, p-2)
        a = pow(g, k, p)
        b = (m * pow(y, k, p)) % p
        result.append(a)
        result.append(b)
    return result

def elgamal_decrypt(cipher_pairs: List[int], p: int, x: int) -> List[int]:
    plain = []
    for i in range(0, len(cipher_pairs), 2):
        a = cipher_pairs[i]
        b = cipher_pairs[i+1]
        a_inv = pow(a, p-1-x, p)
        m = (b * a_inv) % p
        plain.append(m)
    return plain

def elgamal_cipher(operation: int, text: str) -> None:
    if operation == 1:
        print("\n--- Параметры ElGamal (шифрование) ---")
        p = input_int("Введите простое число p (должно быть > 32): ", low=32, is_prime_needed=True)
        g = input_int(f"Введите g (1 < g < {p}): ", low=1, high=p)
        # Ввод секретного ключа x с проверкой диапазона
        x = input_int(f"Введите секретный ключ x (1 < x < {p-1}): ", low=1, high=p-1)
        y = pow(g, x, p)
        plain_numbers = digitization(text)
        cipher = elgamal_encrypt(plain_numbers, p, g, y)
        print(f"\nОткрытые параметры: p = {p}, g = {g}, y = {y}")
        print(f"Секретный ключ (x) = {x} (запомните для расшифровки)")
        print("Зашифрованный текст (пары a,b):", ' '.join(str(c) for c in cipher))
    else:
        print("\n--- Параметры ElGamal (расшифрование) ---")
        p = input_positive("Введите p: ")
        if not is_prime(p):
            print("  [!] Предупреждение: p не является простым. Расшифровка может быть некорректной.")
        x = input_positive("Введите секретный ключ x: ")
        if not (1 < x < p):
            raise ValueError("x должно быть в интервале (1, p)")
        cipher_text = text.strip()
        cipher_numbers = [int(c) for c in cipher_text.split()]
        if len(cipher_numbers) % 2 != 0:
            raise ValueError("Количество чисел должно быть чётным (пары a,b)")
        for val in cipher_numbers:
            if not (0 <= val < p):
                raise ValueError(f"Число {val} выходит за пределы [0, {p-1}]")
        plain_numbers = elgamal_decrypt(cipher_numbers, p, x)
        plain_letters = undigitization(plain_numbers)
        restored = decryption_format(plain_letters)
        print("\nРасшифрованный текст:", restored)

# =====================================================================
# ECC (эллиптические кривые)
# =====================================================================
def ecc_point_add(P: Tuple[int, int], Q: Tuple[int, int], a: int, p: int) -> Tuple[int, int]:
    if P == (0,0) or P is None:
        return Q
    if Q == (0,0) or Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return (0,0)
    if P == Q:
        if y1 == 0:
            return (0,0)
        lam = (3 * x1 * x1 + a) * mod_inverse(2 * y1, p) % p
    else:
        lam = (y2 - y1) * mod_inverse(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ecc_scalar_mult(k: int, P: Tuple[int, int], a: int, p: int) -> Tuple[int, int]:
    result = (0,0)
    Q = P
    while k:
        if k & 1:
            result = ecc_point_add(result, Q, a, p)
        Q = ecc_point_add(Q, Q, a, p)
        k >>= 1
    return result

def point_order(G: Tuple[int, int], a: int, p: int) -> int:
    order = 1
    P = G
    while P != (0,0):
        P = ecc_point_add(P, G, a, p)
        order += 1
        if order > p + 2 * int(p**0.5) + 10:
            raise ValueError("Не удалось найти порядок точки")
    return order

def ecc_encrypt(plain_numbers: List[int], a: int, p: int, G: Tuple[int, int], Cb: int, q: int) -> List[int]:
    cipher = []
    for m in plain_numbers:
        k = random.randint(1, q-1)
        R = ecc_scalar_mult(k, G, a, p)
        while R == (0,0):
            k = random.randint(1, q-1)
            R = ecc_scalar_mult(k, G, a, p)
        P = ecc_scalar_mult(k, ecc_scalar_mult(Cb, G, a, p), a, p)
        e = (m * P[0]) % p
        cipher.append(R[0])
        cipher.append(R[1])
        cipher.append(e)
    return cipher

def ecc_decrypt(cipher_triples: List[int], a: int, p: int, Cb: int) -> List[int]:
    plain = []
    for i in range(0, len(cipher_triples), 3):
        R = (cipher_triples[i], cipher_triples[i+1])
        e = cipher_triples[i+2]
        Q = ecc_scalar_mult(Cb, R, a, p)
        if Q == (0,0):
            raise ValueError("Точка Q бесконечна")
        x_inv = mod_inverse(Q[0], p)
        m = (e * x_inv) % p
        plain.append(m)
    return plain

def ecc_variant_encrypt(a: int, b: int, p: int, G: Tuple[int, int], Cb: int, k: int, m: int) -> Tuple[Tuple[int, int], int]:
    b_mod = b % p
    R = ecc_scalar_mult(k, G, a, p)
    P = ecc_scalar_mult(k, ecc_scalar_mult(Cb, G, a, p), a, p)
    e = (m * P[0]) % p
    return R, e

def ecc_variant_decrypt(a: int, p: int, Cb: int, cipher: Tuple[int, int, int]) -> int:
    R = (cipher[0], cipher[1])
    e = cipher[2]
    Q = ecc_scalar_mult(Cb, R, a, p)
    x_inv = mod_inverse(Q[0], p)
    m = (e * x_inv) % p
    return m

def ecc_demo_variant23():
    print("\n" + "="*60)
    print("  ДЕМОНСТРАЦИЯ ДЛЯ ВАРИАНТА 23")
    print("="*60)
    a = 3
    b = -7
    p = 11
    G = (0, 9)
    Cb = 6
    k = 5
    b_mod = b % p
    print(f"Параметры: a={a}, b={b} (mod {p} -> {b_mod}), p={p}, G={G}, Cb={Cb}, k={k}")
    m = 10
    R, e = ecc_variant_encrypt(a, b_mod, p, G, Cb, k, m)
    print(f"Задание 1.1: шифрование m={m} -> R={R}, e={e}")
    print(f"Ожидаемый шифртекст из таблицы: ((4,6), 9)")
    cipher_from_table = (4, 6, 9)
    dec_m = ecc_variant_decrypt(a, p, Cb, cipher_from_table)
    print(f"Задание 1.2: расшифрование шифртекста {cipher_from_table} -> m={dec_m}")

def ecc_interactive():
    print("\n--- Режим работы с параметрами из таблицы вариантов ---")
    a = input_int("Введите a: ")
    b = input_int("Введите b (может быть отрицательным): ")
    p = input_int("Введите p (простое): ", low=2, is_prime_needed=True)
    b_mod = b % p
    G = input_point("Введите базовую точку G (x y): ", p)
    Cb = input_int("Введите секретный ключ Cb (0 < Cb < p): ", low=0, high=p)
    k = input_int("Введите случайное число k (0 < k < p): ", low=0, high=p)
    m = 10
    print("\n--- Шифрование m=10 ---")
    try:
        R, e = ecc_variant_encrypt(a, b_mod, p, G, Cb, k, m)
        print(f"Результат: R = {R}, e = {e}")
    except Exception as ex:
        print(f"Ошибка при шифровании: {ex}")
    print("\n--- Расшифрование заданного шифртекста ---")
    cipher_input = input("Введите шифртекст в формате Rx Ry e (через пробел): ").strip()
    try:
        parts = cipher_input.split()
        if len(parts) != 3:
            raise ValueError("Нужно три числа")
        Rx, Ry, e_val = map(int, parts)
        m_dec = ecc_variant_decrypt(a, p, Cb, (Rx, Ry, e_val))
        print(f"Расшифрованное сообщение: m = {m_dec}")
    except Exception as ex:
        print(f"Ошибка при расшифровании: {ex}")

# =====================================================================
# Главное меню
# =====================================================================
def main():
    print("=" * 60)
    print("АСИММЕТРИЧНЫЕ ШИФРЫ: RSA, ElGamal, ECC")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. RSA")
        print("  2. ElGamal")
        print("  3. ECC (эллиптические кривые)")
        print("  4. Демонстрация варианта 23 (ECC)")
        print("  0. Выход")
        print("─" * 40)

        try:
            alg = int(input("Выберите алгоритм: "))
        except ValueError:
            print("  [!] Введите число.")
            continue
        if alg == 0:
            print("До свидания!")
            break
        if alg == 4:
            ecc_demo_variant23()
            continue
        if alg not in (1,2,3):
            print("  [!] Неверный выбор.")
            continue

        print("\nВыберите действие:")
        print("  1. Шифрование")
        print("  2. Расшифрование")
        try:
            op = int(input("Ваш выбор: "))
        except ValueError:
            print("  [!] Введите число.")
            continue
        if op not in (1,2):
            print("  [!] Неверный выбор.")
            continue

        raw_text = input("Введите текст: ").strip()
        if op == 1:
            prepared = prepare_text(raw_text)
        else:
            prepared = raw_text

        try:
            if alg == 1:
                rsa_cipher(op, prepared)
            elif alg == 2:
                elgamal_cipher(op, prepared)
            elif alg == 3:
                ecc_interactive()
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()