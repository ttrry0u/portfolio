#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECC (эллиптические кривые) – асимметричный шифр.
Реализовано шифрование/расшифрование одного числа (m) с заданными параметрами,
а также шифрование текста (до 1000 символов) с автоматической генерацией
рандомизатора для каждой буквы. Порядок точки G вычисляется автоматически.
Добавлена возможность просмотра всех точек кривой и их порядков для выбора G.
Алфавит: 32 русские буквы (без ё, заменяется на е).
"""

import sys
import random
from typing import List, Tuple
from math import gcd

# =====================================================================
# Алфавит и словари для замены знаков препинания
# =====================================================================
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы (без 'ё')
ALPH_SIZE = len(ALPHABET)  # 32

# Замена знаков препинания на служебные слова (для шифрования)
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}   # обратный словарь
space_repl = 'прб'          # замена пробела

def prepare_text(txt: str) -> str:
    """
    Подготовка открытого текста к шифрованию:
    - перевод в нижний регистр;
    - замена 'ё' на 'е';
    - замена знаков препинания на кодовые слова;
    - замена пробелов на 'прб'.
    """
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt

def restore_text(txt: str) -> str:
    """
    Восстановление пробелов и знаков препинания после расшифрования.
    Выполняется обратная замена: 'прб' → пробел, 'тчк' → '.' и т.д.
    """
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def digitization(open_text: str) -> List[int]:
    """Перевод букв открытого текста в числовые коды (1..32)."""
    return [ALPHABET.index(ch) + 1 for ch in open_text]

def undigitization(numbers: List[int]) -> str:
    """Обратное преобразование: коды (1..32) → строка букв."""
    return ''.join(ALPHABET[n-1] for n in numbers)

def decryption_format(dec_text: str) -> str:
    """
    Форматирование расшифрованного текста:
    - замена служебных кодов на пробелы и знаки препинания;
    - первая буква становится заглавной;
    - после каждой точки следующий непробельный символ делается заглавным.
    """
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
    """Проверка, является ли число простым (делением до √n)."""
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
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y) такие, что a*x + b*y = gcd(a,b).
    """
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def mod_inverse(a: int, m: int) -> int:
    """Вычисление обратного элемента a^{-1} mod m."""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m

def input_int(prompt: str, low: int = None, high: int = None, is_prime_needed: bool = False) -> int:
    """
    Безопасный ввод целого числа с проверкой границ и, при необходимости, простоты.
    Продолжает запрашивать ввод, пока не будет получено корректное значение.
    """
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
    """Безопасный ввод положительного целого числа."""
    while True:
        try:
            val = int(input(prompt).strip())
            if val > 0:
                return val
            print("  [!] Введите положительное число.")
        except ValueError:
            print("  [!] Введите целое число.")

def input_point(prompt: str, p: int) -> Tuple[int, int]:
    """
    Безопасный ввод точки эллиптической кривой.
    Ожидается формат 'x y' (через пробел) или '(x, y)'.
    Координаты должны быть в диапазоне [0, p-1].
    """
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
# ECC (эллиптические кривые) – базовые операции
# =====================================================================
def ecc_point_add(P: Tuple[int, int], Q: Tuple[int, int], a: int, p: int) -> Tuple[int, int]:
    """
    Сложение двух точек эллиптической кривой y^2 = x^3 + a*x + b (mod p).
    Поддерживает случай P=O, Q=O, удвоение точки (P=Q) и обычное сложение.
    Возвращает точку (x3, y3) или бесконечно удалённую точку (0,0).
    """
    if P == (0,0) or P is None:       # O + Q = Q
        return Q
    if Q == (0,0) or Q is None:       # P + O = P
        return P
    x1, y1 = P
    x2, y2 = Q
    # Проверка на P = -Q (вертикальная прямая)
    if x1 == x2 and (y1 + y2) % p == 0:
        return (0,0)                  # точка на бесконечности
    # Вычисление наклона λ
    if P == Q:                        # удвоение точки
        if y1 == 0:                   # касательная вертикальна
            return (0,0)
        lam = (3 * x1 * x1 + a) * mod_inverse(2 * y1, p) % p
    else:                             # сложение разных точек
        lam = (y2 - y1) * mod_inverse(x2 - x1, p) % p
    # Координаты результирующей точки
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ecc_scalar_mult(k: int, P: Tuple[int, int], a: int, p: int) -> Tuple[int, int]:
    """
    Умножение точки P на скаляр k (двоичный метод "удвоить-и-сложить").
    Возвращает точку k*P.
    """
    result = (0,0)          # начальная точка – O
    Q = P
    while k:
        if k & 1:           # если текущий бит k равен 1, прибавляем Q
            result = ecc_point_add(result, Q, a, p)
        Q = ecc_point_add(Q, Q, a, p)   # Q = 2*Q
        k >>= 1
    return result

def point_order(G: Tuple[int, int], a: int, p: int) -> int:
    """
    Наивное вычисление порядка точки G (количество точек в подгруппе, порождённой G).
    Перебирает кратные 2G, 3G, ... пока не получит O.
    Ограничение перебора: p + 2*sqrt(p) + 10 (граница Хассе).
    """
    order = 1
    P = G
    while P != (0,0):                     # пока не достигнута бесконечно удалённая точка
        P = ecc_point_add(P, G, a, p)
        order += 1
        if order > p + 2 * int(p**0.5) + 10:
            raise ValueError("Не удалось найти порядок точки")
    return order

# =====================================================================
# НОВАЯ ФУНКЦИЯ: вывод всех точек кривой и их порядков
# =====================================================================
def list_points_and_orders(a: int, b: int, p: int) -> None:
    """
    Выводит таблицу всех точек эллиптической кривой
    y^2 = x^3 + a*x + b (mod p) и их порядков.
    Точка на бесконечности обозначена O.
    Удобно для выбора базовой точки G с нужным порядком.
    """
    print(f"\nВсе точки кривой y^2 = x^3 + {a}*x + {b} (mod {p}):")
    print("   O   - порядок 1 (бесконечно удалённая точка)")
    # Перебираем все возможные x
    for x in range(p):
        rhs = (x**3 + a*x + b) % p       # правая часть уравнения
        for y in range(p):
            if (y*y) % p == rhs:          # проверяем, является ли y^2 ≡ rhs (mod p)
                P = (x, y)
                order = point_order(P, a, p)
                print(f"  {P!r} -> порядок {order}")

# =====================================================================
# Шифрование / расшифрование
# =====================================================================
def ecc_encrypt(plain_numbers: List[int], a: int, p: int, G: Tuple[int, int],
                Cb: int, q: int) -> Tuple[List[int], List[int]]:
    """
    Шифрование списка числовых кодов m (1..32) с автоматической генерацией
    случайного рандомизатора k для каждого элемента.
    Cb – секретный ключ получателя (используется для вычисления открытого ключа).
    q – порядок точки G.
    Возвращает кортеж:
      - cipher: плоский список троек (Rx, Ry, e) для всех букв,
      - k_list: использованные рандомизаторы k (для отладки/вывода).
    Важно: генерирует k до тех пор, пока x-координата точки P не станет ≠ 0,
    чтобы избежать ошибки при расшифровании.
    """
    cipher = []
    k_list = []
    for m in plain_numbers:
        while True:
            k = random.randint(1, q - 1)          # случайный k из [1, q-1]
            R = ecc_scalar_mult(k, G, a, p)       # R = k * G
            if R == (0, 0):                       # O – плохо, пробуем снова
                continue
            # Вычисляем общий секрет P = k * (Cb * G)
            P = ecc_scalar_mult(k, ecc_scalar_mult(Cb, G, a, p), a, p)
            if P[0] != 0:                         # x-координата не ноль – ок
                break
        e = (m * P[0]) % p                        # шифрование: e = m * x_P mod p
        cipher.extend([R[0], R[1], e])
        k_list.append(k)
    return cipher, k_list

def ecc_decrypt(cipher_triples: List[int], a: int, p: int, Cb: int) -> List[int]:
    """
    Расшифрование плоского списка троек (Rx, Ry, e).
    Для каждой тройки:
      - восстанавливается точка R = (Rx, Ry),
      - вычисляется общий секрет Q = Cb * R = P,
      - m = e * (x_Q)^{-1} mod p.
    Возвращает список числовых кодов букв.
    """
    plain = []
    for i in range(0, len(cipher_triples), 3):
        R = (cipher_triples[i], cipher_triples[i+1])
        e = cipher_triples[i+2]
        Q = ecc_scalar_mult(Cb, R, a, p)          # Q = Cb * R = k * Cb * G = P
        if Q == (0,0):
            raise ValueError("Точка Q бесконечна")
        x_inv = mod_inverse(Q[0], p)              # (x_Q)^{-1} mod p
        m = (e * x_inv) % p                       # восстанавливаем код буквы
        plain.append(m)
    return plain

# Вариантные функции для работы с одним числом (для демонстрации)
def ecc_variant_encrypt(a: int, b: int, p: int, G: Tuple[int, int],
                        Cb: int, k: int, m: int) -> Tuple[Tuple[int, int], int]:
    """Шифрование одного числа m с фиксированным k (для демонстрации)."""
    b_mod = b % p
    R = ecc_scalar_mult(k, G, a, p)
    P = ecc_scalar_mult(k, ecc_scalar_mult(Cb, G, a, p), a, p)
    e = (m * P[0]) % p
    return R, e

def ecc_variant_decrypt(a: int, p: int, Cb: int, cipher: Tuple[int, int, int]) -> int:
    """Расшифрование одного шифртекста (тройка чисел)."""
    R = (cipher[0], cipher[1])
    e = cipher[2]
    Q = ecc_scalar_mult(Cb, R, a, p)
    x_inv = mod_inverse(Q[0], p)
    m = (e * x_inv) % p
    return m

# =====================================================================
# Демонстрационные и интерактивные функции
# =====================================================================
def ecc_demo_variant23():
    """Демонстрация для варианта 23."""
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
    """Интерактивное шифрование/расшифрование одного числа."""
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

def encrypt_text_menu():
    """
    Шифрование текста с автоматической генерацией рандомизатора для каждой буквы.
    Предлагает вывести все точки кривой для выбора подходящей базовой точки G.
    Порядок точки G вычисляется автоматически.
    """
    print("\n--- Шифрование текста (ECC) ---")
    a = input_int("Введите a: ")
    b = input_int("Введите b (может быть отрицательным): ")
    p = input_int("Введите p (простое): ", low=2, is_prime_needed=True)
    b_mod = b % p

    # Предложим посмотреть все точки кривой
    show = input("Показать все точки кривой и их порядки? (y/n): ").strip().lower()
    if show == 'y':
        list_points_and_orders(a, b_mod, p)

    G = input_point("Введите базовую точку G (x y): ", p)
    Cb = input_int("Введите секретный ключ получателя Cb (0 < Cb < p): ", low=0, high=p)

    # Автоматическое вычисление порядка точки G
    print("Вычисляется порядок точки G...")
    try:
        q = point_order(G, a, p)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return
    print(f"Порядок точки G: {q}")

    text = input("Введите открытый текст: ")
    prepared = prepare_text(text)
    nums = digitization(prepared)
    print(f"Текст преобразован в {len(nums)} числовых кодов (1..32).")

    # Шифруем
    cipher, k_list = ecc_encrypt(nums, a, p, G, Cb, q)

    print("\nЗашифрованный текст (тройки Rx Ry e через пробел):")
    print(' '.join(str(x) for x in cipher))

    print("\nИспользованные рандомизаторы k (для каждой буквы):")
    print(' '.join(str(k) for k in k_list))
    print("Готово.")

def decrypt_text_menu():
    """Расшифрование текста из одной строки с тройками чисел."""
    print("\n--- Расшифрование текста (ECC) ---")
    a = input_int("Введите a: ")
    p = input_int("Введите p (простое): ", low=2, is_prime_needed=True)
    Cb = input_int("Введите секретный ключ Cb (0 < Cb < p): ", low=0, high=p)
    raw = input("Введите зашифрованные данные (тройки Rx Ry e через пробел, всё в одну строку): ").strip()
    parts = raw.split()
    if len(parts) % 3 != 0:
        print("  [!] Количество чисел должно быть кратно 3.")
        return
    cipher_parts = []
    for s in parts:
        try:
            cipher_parts.append(int(s))
        except ValueError:
            print(f"  [!] Некорректное число: '{s}'")
            return
    try:
        plain_nums = ecc_decrypt(cipher_parts, a, p, Cb)
    except Exception as e:
        print(f"Ошибка при расшифровании: {e}")
        return
    text = undigitization(plain_nums)
    restored = restore_text(text)
    formatted = decryption_format(restored)
    print("\nРасшифрованный текст:")
    print(formatted)

# =====================================================================
# Главное меню
# =====================================================================
def main():
    print("=" * 60)
    print("ECC (ЭЛЛИПТИЧЕСКИЕ КРИВЫЕ) – ШИФРОВАНИЕ/РАСШИФРОВАНИЕ")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Шифрование одного числа m (ввод всех параметров)")
        print("  2. Расшифрование одного шифртекста (тройка чисел)")
        print("  3. Зашифровать текст (автоматическая генерация рандомизатора)")
        print("  4. Расшифровать текст (из списка троек в строку)")
        print("  5. Демонстрация варианта 23")
        print("  0. Выход")
        print("─" * 40)

        try:
            alg = int(input("Выберите действие: "))
        except ValueError:
            print("  [!] Введите число.")
            continue
        if alg == 0:
            print("До свидания!")
            break
        elif alg == 1:
            ecc_interactive()
        elif alg == 2:
            # Расшифрование одного шифртекста (тройка чисел)
            print("\n--- Расшифрование шифртекста ---")
            a = input_int("Введите a: ")
            p = input_int("Введите p (простое): ", low=2, is_prime_needed=True)
            Cb = input_int("Введите секретный ключ Cb (0 < Cb < p): ", low=0, high=p)
            cipher_input = input("Введите шифртекст в формате Rx Ry e (через пробел): ").strip()
            try:
                parts = cipher_input.split()
                if len(parts) != 3:
                    raise ValueError("Нужно три числа")
                Rx, Ry, e_val = map(int, parts)
                m_dec = ecc_variant_decrypt(a, p, Cb, (Rx, Ry, e_val))
                print(f"Расшифрованное сообщение: m = {m_dec}")
            except Exception as ex:
                print(f"Ошибка: {ex}")
        elif alg == 3:
            encrypt_text_menu()
        elif alg == 4:
            decrypt_text_menu()
        elif alg == 5:
            ecc_demo_variant23()
        else:
            print("  [!] Неверный выбор.")

if __name__ == "__main__":
    main()