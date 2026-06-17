import sys
from math import gcd

# ---------- Алфавит и словари замены ----------
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы (без 'ё')
ALPH_SIZE = len(ALPHABET)  # 32

# Замена знаков препинания на служебные слова (для подписи / проверки)
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}   # обратный словарь
space_repl = 'прб'                                   # заменитель пробела

def prepare_text(txt: str) -> str:
    """
    Подготовка текста перед вычислением хеша или подписью.
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
    Восстановление исходного вида текста:
    служебные слова заменяются обратно на знаки препинания и пробел.
    (В данной программе не используется, но оставлена для совместимости.)
    """
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt

def hash_message(text: str, N: int) -> int:
    """
    Квадратичная хеш-функция, использующая модуль N.
    Для каждого символа текста:
      h = ((h + код_буквы) ^ 2) mod N
    Код буквы – её позиция в алфавите от 1 до 32.
    Возвращает целое число – хеш сообщения.
    """
    h = 0
    for ch in text:
        mi = ALPHABET.index(ch) + 1   # код буквы 1..32
        h = (h + mi) % N
        h = (h * h) % N               # квадрат по модулю N
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
# RSA – подпись и проверка
# =====================================================================
def rsa_sign(message_hash: int, d: int, n: int) -> int:
    """
    Формирование цифровой подписи RSA.
    Подпись = (хеш)^d mod n, где d – секретный ключ.
    """
    return pow(message_hash, d, n)

def rsa_verify(message_hash: int, signature: int, e: int, n: int) -> bool:
    """
    Проверка цифровой подписи RSA.
    Вычисляет (подпись)^e mod n и сравнивает с исходным хешем.
    Возвращает True, если хеши совпадают.
    """
    return pow(signature, e, n) == message_hash

def demo_rsa_signature():
    """
    Демонстрация работы схемы подписи RSA на фиксированном примере.
    Используются небольшие простые числа для наглядности.
    """
    print("\n" + "="*60)
    print("  ДЕМОНСТРАЦИЯ ЦИФРОВОЙ ПОДПИСИ RSA")
    print("="*60)
    p_demo = 23
    q_demo = 29
    n_demo = p_demo * q_demo                    # модуль N = 667
    phi_demo = (p_demo - 1) * (q_demo - 1)      # φ(N) = 616
    e_demo = 13                                  # открытая экспонента (взаимно проста с φ(N))
    d_demo = mod_inverse(e_demo, phi_demo)       # секретный ключ D
    print(f"Открытый ключ: N = {n_demo}, E = {e_demo}")
    print(f"Закрытый ключ: D = {d_demo}")
    text = "приветмир"
    print(f"Исходный текст: {text}")
    prepared = prepare_text(text)
    h = hash_message(prepared, n_demo)           # хеш сообщения по модулю N
    print(f"Хеш сообщения: {h}")
    signature = rsa_sign(h, d_demo, n_demo)      # подпись
    print(f"Подпись: {signature}")
    valid = rsa_verify(h, signature, e_demo, n_demo)  # проверка подписи
    print(f"Проверка подписи: {'✅ верна' if valid else '❌ неверна'}")
    print()

def main():
    """Главное меню программы."""
    print("=" * 60)
    print("ЦИФРОВАЯ ПОДПИСЬ RSA С КВАДРАТИЧНЫМ ХЕШИРОВАНИЕМ")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    # Сначала демонстрация
    demo_rsa_signature()

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
            print("\n--- Подпись сообщения RSA ---")
            text = input("Введите текст для подписи: ")
            prepared = prepare_text(text)
            if not prepared:
                print("  [!] Текст пуст после предобработки.")
                continue

            print("\nВведите простые числа для генерации ключей:")
            p = input_int("Введите простое число P: ", low=1, is_prime_needed=True)
            q = input_int("Введите простое число Q (отличное от P): ", low=1, is_prime_needed=True)
            if p == q:
                print("  [!] P и Q должны быть различны.")
                continue
            n = p * q
            # Модуль должен быть больше размера алфавита, чтобы коды 1..32 не давали коллизий
            if n <= ALPH_SIZE:
                print(f"  [!] Модуль N = {n} должен быть больше размера алфавита ({ALPH_SIZE}).")
                print("     Выберите большие простые числа P и Q.")
                continue
            phi = (p-1)*(q-1)
            print(f"Вычислено N = {n}, φ(N) = {phi}")

            # Ввод открытой экспоненты E с проверкой взаимной простоты с φ(N)
            e = input_int(f"Введите число E (1 < E < {phi}, взаимно простое с φ): ", low=1, high=phi)
            while gcd(e, phi) != 1:
                print(f"  [!] E и φ(N) не взаимно просты.")
                e = input_int(f"Введите E (1 < E < {phi}, gcd(E,{phi})=1): ", low=1, high=phi)
            d = mod_inverse(e, phi)
            # Проверка, что D не равен E (нежелательное совпадение)
            if d == e:
                print("  [!] E и D совпали. Введите другое E.")
                continue
            print(f"Вычислен секретный ключ D = {d}")

            # Хеширование текста с модулем N и подписание
            h = hash_message(prepared, n)
            print(f"Хеш сообщения: {h}")
            signature = rsa_sign(h, d, n)
            print(f"Подпись: {signature}")
            print("\nСохраните следующие данные для проверки:")
            print(f"  - Сообщение: {text}")
            print(f"  - Открытый ключ: N = {n}, E = {e}")
            print(f"  - Подпись: {signature}")

        elif choice == 2:
            # --- Проверка подписи ---
            print("\n--- Проверка подписи RSA ---")
            text = input("Введите исходное сообщение: ")
            prepared = prepare_text(text)
            n = input_positive("Введите модуль N (открытый ключ): ")
            if n <= ALPH_SIZE:
                print(f"  [!] Модуль N = {n} должен быть больше размера алфавита ({ALPH_SIZE}).")
                continue
            e = input_positive("Введите число E (открытый ключ): ")
            signature = input_int("Введите подпись (целое число): ")
            # Вычисляем хеш заново и проверяем подпись
            h = hash_message(prepared, n)
            print(f"Вычисленный хеш сообщения: {h}")
            valid = rsa_verify(h, signature, e, n)
            print(f"Результат проверки: {'✅ Подпись верна' if valid else '❌ Подпись неверна'}")

        else:
            print("  [!] Неверный выбор.")

if __name__ == "__main__":
    main()