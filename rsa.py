import sys
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
    """Вычисление обратного элемента a^{-1} mod m с помощью расширенного алгоритма Евклида."""
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

# ---------- RSA: шифрование и расшифрование ----------
def rsa_encrypt(plain_numbers: List[int], n: int, e: int) -> List[int]:
    """
    Шифрование последовательности чисел открытым ключом (n, e).
    Для каждого числа m вычисляется c = m^e mod n.
    """
    return [pow(m, e, n) for m in plain_numbers]

def rsa_decrypt(cipher_numbers: List[int], n: int, d: int) -> List[int]:
    """
    Расшифрование последовательности чисел секретным ключом d.
    Для каждого зашифрованного числа c вычисляется m = c^d mod n.
    """
    return [pow(c, d, n) for c in cipher_numbers]

def rsa_cipher(operation: int, text: str) -> None:
    """
    Основная логика RSA: генерация ключей (для шифрования) и выполнение операций.
    operation = 1 → шифрование, operation = 2 → расшифрование.
    """
    if operation == 1:
        # ----- Шифрование -----
        print("\n--- Параметры RSA (шифрование) ---")
        # Ввод простых чисел p и q, образующих модуль n = p * q
        p = input_int("Введите простое число P: ", low=1, is_prime_needed=True)
        q = input_int("Введите простое число Q (отличное от P): ", low=1, is_prime_needed=True)
        if p == q:
            raise ValueError("P и Q должны быть различными")
        n = p * q
        # Модуль должен быть больше размера алфавита, чтобы коды 1..32 помещались
        if n < ALPH_SIZE:
            raise ValueError(f"n = {n} должно быть больше {ALPH_SIZE}")
        phi = (p-1)*(q-1)
        print(f"φ(N) = {phi}")

        # Ввод открытой экспоненты e (взаимно простой с φ(n))
        e = input_int(f"Введите число E (1 < E < {phi}, взаимно простое с φ): ", low=1, high=phi)
        while True:
            while gcd(e, phi) != 1:
                print(f"  [!] E и φ(N) не взаимно просты. Введите другое E.")
                e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
            # Вычисление секретного ключа d = e^{-1} mod φ(n)
            d = mod_inverse(e, phi)
            # Проверка, что e и d не совпадают (небезопасно)
            if d == e:
                print("  [!] E и D совпали. Это нежелательно. Введите другое E.")
                e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
            else:
                break

        # Преобразование подготовленного текста в числа
        plain_numbers = digitization(text)
        # Шифрование
        cipher_numbers = rsa_encrypt(plain_numbers, n, e)

        print(f"\nОткрытый ключ: N = {n}, E = {e}")
        print(f"Секретный ключ (d) = {d} (сохраните для расшифровки)")
        print("Зашифрованный текст (числа):", ' '.join(str(c) for c in cipher_numbers))

    else:
        # ----- Расшифрование -----
        print("\n--- Параметры RSA (расшифрование) ---")
        n = input_positive("Введите N: ")
        d = input_positive("Введите секретный ключ d: ")
        # Входная строка – числа через пробел
        cipher_numbers = [int(x) for x in text.split()]
        # Расшифрование
        plain_numbers = rsa_decrypt(cipher_numbers, n, d)
        # Преобразование чисел в буквы
        plain_letters = undigitization(plain_numbers)
        # Восстановление знаков препинания и форматирование
        restored = decryption_format(plain_letters)
        print("\nРасшифрованный текст:", restored)


def main():
    """Главное меню программы."""
    print("=" * 60)
    print("АСИММЕТРИЧНЫЙ ШИФР RSA")
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
            rsa_cipher(op, prepared)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()