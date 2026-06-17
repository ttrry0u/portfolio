import sys
import random
from typing import List, Tuple
from math import gcd

# ---------- Алфавит и словари замены ----------
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы (без 'ё')
ALPH_SIZE = len(ALPHABET)  # 32

# Замена знаков препинания на служебные слова (для шифрования)
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}   # обратный словарь
space_repl = 'прб'                                   # заменитель пробела

def prepare_text(txt: str) -> str:
    """
    Подготовка текста к шифрованию:
    - приведение к нижнему регистру,
    - замена 'ё' → 'е',
    - замена знаков препинания и пробела на служебные слова.
    """
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt

def restore_text(txt: str) -> str:
    """
    Восстановление исходного текста после расшифрования:
    - обратная замена служебных слов на знаки препинания и пробел.
    """
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def digitization(open_text: str) -> List[int]:
    """Преобразование букв открытого текста в числовые коды (1..32)."""
    return [ALPHABET.index(ch) + 1 for ch in open_text]

def undigitization(numbers: List[int]) -> str:
    """Обратное преобразование: коды (1..32) → строка букв."""
    return ''.join(ALPHABET[n-1] for n in numbers)

def decryption_format(dec_text: str) -> str:
    """
    Форматирование расшифрованного текста:
    - замена служебных кодов на знаки препинания и пробелы,
    - первая буква – заглавная,
    - после каждой точки следующий символ становится заглавным.
    """
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace(space_repl, ' ')
    if not dec_text:
        return ""
    result = dec_text[0].upper() + dec_text[1:]          # первая буква заглавная
    result_list = list(result)
    for i in range(len(result_list) - 2):
        if result_list[i] == ".":
            result_list[i+2] = result_list[i+2].upper()  # после точки – заглавная
    return ''.join(result_list)

# ---------- Математические функции ----------
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
    """Безопасный ввод целого числа с проверкой границ и, при необходимости, простоты."""
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

# ---------- ElGamal: шифрование и расшифрование ----------
def elgamal_encrypt(plain_numbers: List[int], p: int, g: int, y: int) -> List[int]:
    """
    Шифрование последовательности чисел открытым ключом (p, g, y).
    Для каждого числа m:
      - выбирается случайное число k (1 < k < p-1, взаимно простое с p-1),
      - вычисляется a = g^k mod p,
      - вычисляется b = m * y^k mod p.
    Пара (a, b) добавляется в результирующий список.
    """
    result = []
    for m in plain_numbers:
        # Выбор случайного k, взаимно простого с p-1
        k = random.randint(2, p-2)
        while gcd(k, p-1) != 1:
            k = random.randint(2, p-2)
        a = pow(g, k, p)                 # a = g^k mod p
        b = (m * pow(y, k, p)) % p       # b = m * y^k mod p
        result.append(a)
        result.append(b)
    return result

def elgamal_decrypt(cipher_pairs: List[int], p: int, x: int) -> List[int]:
    """
    Расшифрование последовательности пар (a, b) секретным ключом x.
    Для каждой пары:
      - a_inv = a^{p-1-x} mod p   (так как a^{p-1} ≡ 1 mod p),
      - m = b * a_inv mod p.
    """
    plain = []
    for i in range(0, len(cipher_pairs), 2):
        a = cipher_pairs[i]
        b = cipher_pairs[i+1]
        # a^{p-1-x} ≡ a^{-x} (mod p), что позволяет вычислить (y^k)^{-1} без нахождения обратного
        a_inv = pow(a, p-1-x, p)
        m = (b * a_inv) % p
        plain.append(m)
    return plain

def elgamal_cipher(operation: int, text: str) -> None:
    """
    Основная логика ElGamal: генерация ключей (для шифрования) и выполнение операций.
    operation = 1 → шифрование, operation = 2 → расшифрование.
    """
    if operation == 1:
        # ----- Шифрование -----
        print("\n--- Параметры ElGamal (шифрование) ---")
        # Ввод простого числа p (модуль), p должно быть > 32 (размер алфавита)
        p = input_int("Введите простое число p (должно быть > 32): ", low=32, is_prime_needed=True)
        # Ввод порождающего элемента g (1 < g < p)
        g = input_int(f"Введите g (1 < g < {p}): ", low=1, high=p)
        # Ввод секретного ключа x (1 < x < p-1)
        x = input_int(f"Введите секретный ключ x (1 < x < {p-1}): ", low=1, high=p-1)
        # Вычисление открытого ключа y = g^x mod p
        y = pow(g, x, p)
        # Преобразование подготовленного текста в числа
        plain_numbers = digitization(text)
        # Шифрование
        cipher = elgamal_encrypt(plain_numbers, p, g, y)
        print(f"\nОткрытые параметры: p = {p}, g = {g}, y = {y}")
        print(f"Секретный ключ (x) = {x} (запомните для расшифровки)")
        print("Зашифрованный текст (пары a,b):", ' '.join(str(c) for c in cipher))

    else:
        # ----- Расшифрование -----
        print("\n--- Параметры ElGamal (расшифрование) ---")
        p = input_positive("Введите p: ")
        if not is_prime(p):
            print("  [!] Предупреждение: p не является простым. Расшифровка может быть некорректной.")
        x = input_positive("Введите секретный ключ x: ")
        if not (1 < x < p):
            raise ValueError("x должно быть в интервале (1, p)")
        # Входная строка – числа через пробел (пары a,b)
        cipher_text = text.strip()
        cipher_numbers = [int(c) for c in cipher_text.split()]
        if len(cipher_numbers) % 2 != 0:
            raise ValueError("Количество чисел должно быть чётным (пары a,b)")
        # Проверка, что все числа лежат в [0, p-1]
        for val in cipher_numbers:
            if not (0 <= val < p):
                raise ValueError(f"Число {val} выходит за пределы [0, {p-1}]")
        # Расшифрование
        plain_numbers = elgamal_decrypt(cipher_numbers, p, x)
        # Преобразование чисел в буквы
        plain_letters = undigitization(plain_numbers)
        # Восстановление знаков препинания и форматирование
        restored = decryption_format(plain_letters)
        print("\nРасшифрованный текст:", restored)


def main():
    """Главное меню программы."""
    print("=" * 60)
    print("АСИММЕТРИЧНЫЙ ШИФР ELGAMAL")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Шифрование")
        print("  2. Расшифрование")
        print("  0. Выход")
        print("─" * 40)

        try:
            op = int(input("Ваш выбор: "))
        except ValueError:
            print("  [!] Введите число.")
            continue
        if op == 0:
            print("До свидания!")
            break
        if op not in (1, 2):
            print("  [!] Неверный выбор.")
            continue

        raw_text = input("Введите текст: ").strip()
        if op == 1:
            # При шифровании текст предварительно обрабатывается
            prepared = prepare_text(raw_text)
        else:
            # При расшифровании ожидается строка чисел (шифртекст)
            prepared = raw_text

        try:
            elgamal_cipher(op, prepared)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()