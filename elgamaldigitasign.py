import sys
import random
from math import gcd

# ---------- Алфавит и словари замены ----------
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы (без 'ё')
ALPH_SIZE = len(ALPHABET)  # 32

# Замена знаков препинания на служебные слова (для подготовки текста)
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}   # обратный словарь
space_repl = 'прб'                                   # заменитель пробела

def prepare_text(txt: str) -> str:
    """
    Подготовка текста перед вычислением хеша и подписью.
    Приводит к нижнему регистру, заменяет 'ё' → 'е',
    знаки препинания и пробелы заменяет на служебные слова.
    """
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt

def restore_text(txt: str) -> str:
    """
    Восстановление исходного вида текста (для совместимости,
    в данной программе не используется).
    """
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def hash_message(text: str, p: int) -> int:
    """
    Квадратичная хеш-функция по модулю p.
    Для каждого символа текста:
      h = ((h + код_буквы) ^ 2) mod p
    Код буквы – её позиция в алфавите от 1 до 32.
    Возвращает целое число – хеш сообщения.
    """
    h = 0
    for ch in text:
        mi = ALPHABET.index(ch) + 1   # код буквы 1..32
        h = (h + mi) % p
        h = (h * h) % p               # квадрат по модулю p
    return h

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

def extended_gcd(a: int, b: int):
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

# =====================================================================
# ElGamal – подпись и проверка
# =====================================================================
def elgamal_sign(message_hash: int, p: int, g: int, x: int) -> tuple:
    """
    Формирование цифровой подписи ElGamal.
    Параметры:
      message_hash – хеш подписываемого сообщения (должен быть в интервале (0, p)),
      p – большое простое число (модуль),
      g – порождающий элемент (1 < g < p),
      x – секретный ключ (1 < x < p-1).
    Возвращает кортеж (a, b, k), где k – случайный рандомизатор, использованный при подписи.
    """
    # Проверка корректности входных данных
    if not (0 < message_hash < p):
        raise ValueError("Хеш должен быть в интервале (0, p)")
    if not (1 < g < p):
        raise ValueError("g должно быть в интервале (1, p)")
    if not (1 < x < p-1):
        raise ValueError("x должно быть в интервале (1, p-1)")

    # Выбор случайного k, взаимно простого с p-1.
    # Это необходимо, чтобы существовал обратный элемент k^{-1} mod (p-1).
    while True:
        k = random.randint(2, p-2)
        if gcd(k, p-1) == 1:
            break

    # Вычисление a = g^k mod p
    a = pow(g, k, p)
    if a == 0:                     # крайне маловероятно, но проверяем
        raise ValueError("a = 0, попробуйте другое k")

    # Вычисление b = (hash - x * a) * k^{-1} mod (p-1)
    k_inv = mod_inverse(k, p-1)
    b = ((message_hash - x * a) % (p-1)) * k_inv % (p-1)
    if b == 0:
        # b = 0 допустимо, но может указывать на нестойкость; оставляем как есть
        pass

    return (a, b, k)


def elgamal_verify(message_hash: int, a: int, b: int, p: int, g: int, y: int) -> bool:
    """
    Проверка цифровой подписи ElGamal.
    Параметры:
      message_hash – хеш сообщения,
      a, b – компоненты подписи,
      p, g – параметры системы,
      y – открытый ключ (y = g^x mod p).
    Возвращает True, если подпись корректна.
    """
    # Проверка диапазонов компонент
    if not (0 < message_hash < p):
        print("  [!] Хеш вне диапазона (0, p)")
        return False
    if not (0 < a < p):
        print("  [!] a вне диапазона (0, p)")
        return False
    if not (0 < b < p-1):
        print("  [!] b вне диапазона (0, p-1)")
        return False
    if not (1 < g < p):
        print("  [!] g вне диапазона (1, p)")
        return False
    if not (0 < y < p):
        print("  [!] y вне диапазона (0, p)")
        return False

    # Вычисление левой и правой частей проверочного равенства
    # Левая часть: y^a * a^b mod p
    left = (pow(y, a, p) * pow(a, b, p)) % p
    # Правая часть: g^{hash} mod p
    right = pow(g, message_hash, p)

    return left == right


def demo_elgamal_signature():
    """
    Демонстрация работы схемы подписи ElGamal на фиксированных маленьких числах.
    Используются p=47, g=11, x=5, текст="приветмир".
    """
    print("\n" + "="*60)
    print("  ДЕМОНСТРАЦИЯ ЦИФРОВОЙ ПОДПИСИ ELGAMAL")
    print("="*60)
    # Параметры для демонстрации (маленькие, но рабочие)
    p_demo = 47
    g_demo = 11
    x_demo = 5
    y_demo = pow(g_demo, x_demo, p_demo)        # открытый ключ: 11^5 mod 47 = 22 (примерно)
    text = "приветмир"
    print(f"Открытые параметры: p = {p_demo}, g = {g_demo}, y = {y_demo}")
    print(f"Секретный ключ: x = {x_demo}")
    print(f"Исходный текст: {text}")
    prepared = prepare_text(text)
    h = hash_message(prepared, p_demo)           # хеш сообщения по модулю p
    print(f"Хеш сообщения: {h}")
    a, b, k = elgamal_sign(h, p_demo, g_demo, x_demo)  # формирование подписи
    print(f"Случайный рандомизатор k = {k}")
    print(f"Подпись: a = {a}, b = {b}")
    valid = elgamal_verify(h, a, b, p_demo, g_demo, y_demo)  # проверка подписи
    print(f"Проверка подписи: {'✅ верна' if valid else '❌ неверна'}")
    print()


def main():
    """Главное меню программы."""
    print("=" * 60)
    print("ЦИФРОВАЯ ПОДПИСЬ ELGAMAL С КВАДРАТИЧНЫМ ХЕШИРОВАНИЕМ")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    demo_elgamal_signature()    # сначала демонстрация

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Подписать сообщение")
        print("  2. Проверить подпись")
        print("  0. Выход")
        print("─" * 40)

        try:
            choice = int(input("Выберите действие: "))
        except ValueError:
            print("  [!] Введите число.")
            continue

        if choice == 0:
            print("До свидания!")
            break

        elif choice == 1:
            # --- Подписание сообщения ---
            print("\n--- Подпись сообщения ElGamal ---")
            text = input("Введите текст для подписи: ")
            prepared = prepare_text(text)
            if not prepared:
                print("  [!] Текст пуст после предобработки.")
                continue

            # Ввод параметров
            p = input_int("Введите простое число p (модуль подписи, >32): ", low=32, is_prime_needed=True)

            # Хеширование по модулю p
            h = hash_message(prepared, p)
            if h == 0:
                print("  [!] Хеш сообщения равен 0. Это допустимо, но может снизить стойкость.")
            if h >= p:
                print("  [!] Хеш должен быть меньше p. Проверьте параметры.")
                continue
            print(f"Хеш сообщения: {h}")

            # Ввод порождающего элемента g
            g = input_int(f"Введите g (1 < g < {p}): ", low=1, high=p)
            if g == 1:
                print("  [!] g не должно быть равно 1.")
                continue
            if gcd(g, p) != 1:
                print("  [!] Предупреждение: g не взаимно просто с p. Подпись может быть некорректной.")

            # Ввод секретного ключа x
            x = input_int(f"Введите секретный ключ x (1 < x < {p-1}): ", low=1, high=p-1)
            if x == 1 or x == p-2:
                print("  [!] x не должно быть крайним значением (1 или p-2).")
                continue

            # Генерация подписи
            try:
                a, b, k = elgamal_sign(h, p, g, x)
            except ValueError as e:
                print(f"  [!] Ошибка: {e}")
                continue
            print(f"Случайный рандомизатор k = {k}")
            print(f"Подпись: a = {a}, b = {b}")

            # Вычисление открытого ключа y = g^x mod p для информации
            y = pow(g, x, p)
            print("Сохраните следующие данные для проверки:")
            print(f"  - Сообщение: {text}")
            print(f"  - Открытые параметры: p = {p}, g = {g}, y = {y}")
            print(f"  - Подпись: a = {a}, b = {b}")

        elif choice == 2:
            # --- Проверка подписи ---
            print("\n--- Проверка подписи ElGamal ---")
            text = input("Введите исходное сообщение: ")
            prepared = prepare_text(text)
            p = input_int("Введите простое число p (модуль подписи): ", is_prime_needed=True)
            h = hash_message(prepared, p)
            if h >= p:
                print("  [!] Хеш не меньше p. Проверка невозможна.")
                continue
            print(f"Вычисленный хеш сообщения: {h}")
            g = input_int(f"Введите g (1 < g < {p}): ", low=1, high=p)
            if not (1 < g < p):
                print("  [!] g вне диапазона.")
                continue
            y = input_int(f"Введите открытый ключ y (0 < y < {p}): ", low=0, high=p)
            if y == 0:
                print("  [!] y не может быть 0.")
                continue
            a = input_int("Введите a (подпись): ")
            b = input_int("Введите b (подпись): ")
            valid = elgamal_verify(h, a, b, p, g, y)
            print(f"Результат проверки: {'✅ Подпись верна' if valid else '❌ Подпись неверна'}")

        else:
            print("  [!] Неверный выбор.")

if __name__ == "__main__":
    main()