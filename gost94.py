import sys
import random

# ---------- Подготовка текста ----------
def preprocess(text: str) -> str:
    """
    Предварительная обработка текста перед подписью / проверкой.
    Заменяет точку на 'тчк', запятую на 'зпт', пробел на 'прб',
    затем переводит строку в нижний регистр.
    (Аналог prepare_text в других программах, но без замены 'ё' -> 'е').
    """
    text = text.replace('.', 'тчк')
    text = text.replace(',', 'зпт')
    text = text.replace(' ', 'прб')
    return text.lower()

# ---------- Хеш-функция (квадратичная) ----------
def hash_quad(text: str, p: int, verbose: bool = False) -> int:
    """
    Квадратичная хеш-функция по модулю p.
    Для каждого символа обработанного текста:
        h = ((h + индекс_буквы + 1) ^ 2) mod p
    Индекс буквы берётся из алфавита (0..31), к нему добавляется 1,
    чтобы коды были от 1 до 32.
    Если итоговый хеш равен 0, он заменяется на 1.
    Если verbose=True, выводит пошаговый процесс вычисления.
    """
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы
    h = 0
    if verbose:
        print(f"\n  Формула: h_i = (h_{{i-1}} + индекс(буквы) + 1)² mod {p}")
        print(f"  {'Буква':<6} {'Индекс':<8} {'Вычисление':<38} {'h'}")
        print("  " + "-"*65)
    for ch in text:
        idx = alphabet.index(ch) + 1          # получаем код буквы (1..32)
        h_prev = h
        h = ((h_prev + idx) ** 2) % p         # квадратичное обновление
        if verbose:
            calc = f"({h_prev} + {idx})² % {p} = {(h_prev+idx)**2} % {p}"
            print(f"  '{ch}'    {idx:<8} {calc:<38} {h}")
    result = h if h != 0 else 1               # 0 заменяем на 1
    if verbose and h == 0:
        print("  h = 0 → заменяем на 1")
    return result

# ---------- Математические утилиты ----------
def is_prime(n: int) -> bool:
    """Проверка, является ли число простым (перебор делителей до √n)."""
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

def mod_inv(a: int, p: int) -> int:
    """
    Вычисление обратного элемента a^{-1} mod p с помощью встроенной функции pow.
    Требует Python 3.8+ (поддержка отрицательной степени для вычисления обратного).
    """
    a = a % p
    if a == 0:
        raise ZeroDivisionError("Обратный элемент не существует")
    return pow(a, -1, p)

# ---------- Вычисление параметра a (образующей подгруппы) ----------
def compute_a(p: int, q: int) -> int:
    """
    Интерактивный выбор параметра a, удовлетворяющего условиям:
      a = d^{(p-1)/q} mod p,
      a != 1,
      a^q mod p == 1.
    Выводит таблицу кандидатов и позволяет выбрать один из них.
    """
    print(f"\n{'='*60}")
    print(f"  ВЫЧИСЛЕНИЕ ПАРАМЕТРА a (ГОСТ Р 34.10-94)")
    print(f"{'='*60}")
    print(f"  Формула: a = d^((p-1)/q) mod p")
    print(f"  Условие: a != 1  и  a^q mod p = 1")
    print(f"  (p-1)/q = ({p}-1)/{q} = {(p-1)//q}\n")
    exp = (p - 1) // q
    candidates = []
    print(f"  {'d':<6} {'a = d^exp mod p':<25} {'a^q mod p':<12} {'Статус'}")
    print(f"  {'-'*60}")
    # Перебираем d от 2 до p-1
    for d in range(2, p):
        a = pow(d, exp, p)
        check = pow(a, q, p)
        ok = (a != 1) and (check == 1)
        status = "✓ подходит" if ok else "✗ не подходит"
        print(f"  {d:<6} {a:<25} {check:<12} {status}")
        if ok:
            candidates.append((d, a))
    if not candidates:
        raise ValueError("Не найдено подходящих значений a!")
    print(f"\n  Найдено {len(candidates)} подходящих значений a.")
    print("  Выберите одно из них (введите номер d или само a):")
    for idx, (d, a_val) in enumerate(candidates, 1):
        print(f"    {idx}. d={d}, a={a_val}")
    # Ожидаем ввод номера из списка или самого значения a
    while True:
        choice = input("  Ваш выбор: ").strip()
        # Пробуем интерпретировать как номер
        try:
            idx = int(choice)
            if 1 <= idx <= len(candidates):
                return candidates[idx-1][1]
        except ValueError:
            pass
        # Или как само значение a
        try:
            a_val = int(choice)
            for d, a_candidate in candidates:
                if a_candidate == a_val:
                    return a_val
        except ValueError:
            pass
        print("  Неверный ввод. Введите номер из списка или значение a.")

# ---------- Подпись ГОСТ Р 34.10-94 ----------
def gost94_sign(text: str, p: int, q: int, a: int, x: int) -> tuple:
    """
    Формирование цифровой подписи по ГОСТ Р 34.10-94.
    Параметры:
      text – подготовленный текст,
      p – большое простое число (модуль),
      q – простой делитель p-1 (порядок циклической группы),
      a – образующая подгруппы порядка q (a^q ≡ 1 mod p, a ≠ 1),
      x – секретный ключ (0 < x < q).
    Возвращает (r, s, m), где m – хеш сообщения по модулю q.
    """
    # Вычисляем хеш сообщения (результат не должен быть 0, но hash_quad гарантирует >0)
    m = hash_quad(text, q, verbose=False)
    # Случайный выбор k (1 < k < q)
    candidates = list(range(1, q))
    random.shuffle(candidates)
    for k in candidates:
        # r = (a^k mod p) mod q
        r = pow(a, k, p) % q
        # s = (x * r + k * m) mod q
        s = (x * r + k * m) % q
        # Допустимы только ненулевые компоненты
        if r != 0 and s != 0:
            return (r, s, m)
    # Если ни одно k не подошло (крайне маловероятно)
    raise ValueError("Не удалось найти подходящее k")

# ---------- Проверка подписи ГОСТ Р 34.10-94 ----------
def gost94_verify(text: str, r: int, s: int, p: int, q: int, a: int, y: int) -> bool:
    """
    Проверка подписи по ГОСТ Р 34.10-94.
    Параметры:
      text – подготовленный текст,
      r, s – компоненты подписи,
      p, q, a – параметры схемы,
      y – открытый ключ (y = a^x mod p).
    Возвращает True, если подпись корректна.
    """
    # Вычисляем хеш сообщения заново
    m = hash_quad(text, q, verbose=False)
    # Проверка диапазонов r и s
    if not (0 < r < q and 0 < s < q):
        return False
    # v = m^{q-2} mod q (обратный элемент к m, так как q простое)
    v = pow(m, q - 2, q)
    # z1 = s * v mod q
    z1 = (s * v) % q
    # z2 = (q - r) * v mod q   (т.е. -r * v mod q)
    z2 = ((q - r) * v) % q
    # u = (a^{z1} * y^{z2} mod p) mod q
    u = (pow(a, z1, p) * pow(y, z2, p)) % p % q
    # Подпись верна, если u == r
    return u == r

# ---------- Главное меню ----------
def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-94 – ЦИФРОВАЯ ПОДПИСЬ")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Подписать сообщение")
        print("  2. Проверить подпись")
        print("  0. Выход")
        print("─" * 40)

        try:
            op = int(input("Выберите действие: "))
        except ValueError:
            print("  [!] Введите число.")
            continue
        if op == 0:
            break
        if op not in (1, 2):
            print("  [!] Неверный выбор.")
            continue

        # Ввод текста и его предобработка
        text = input("Введите текст: ")
        text = preprocess(text)
        print(f"Обработанный текст: {text}\n")

        if op == 1:
            # --- Подпись сообщения ---
            p = int(input(" - Введите P (простое, P > 32): "))
            if not is_prime(p):
                print("P должно быть простым!")
                continue
            if p <= 32:
                print(f"P должно быть > 32! Вы ввели {p}")
                continue

            q = int(input(f" - Введите Q (простой делитель {p-1}): "))
            if not is_prime(q) or (p - 1) % q != 0:
                print(f"Q должно быть простым делителем {p-1}!")
                continue

            # Вычисляем образующую a
            a = compute_a(p, q)

            x = int(input(f" - Введите X (закрытый ключ, 0 < X < {q}): "))
            if not (0 < x < q):
                print("X должен быть в диапазоне (0, q)!")
                continue

            # Вычисляем открытый ключ y = a^x mod p
            y = pow(a, x, p)
            print(f"\nОткрытый ключ Y = {y}")

            try:
                r, s, m = gost94_sign(text, p, q, a, x)
                print(f"\nПодпись: r = {r}, s = {s}")
                print(f"Хеш сообщения: {m}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif op == 2:
            # --- Проверка подписи ---
            p = int(input(" - Введите P: "))
            q = int(input(" - Введите Q: "))
            a = int(input(" - Введите a: "))
            y = int(input(" - Введите Y (открытый ключ): "))
            r = int(input(" - Введите r: "))
            s = int(input(" - Введите s: "))
            valid = gost94_verify(text, r, s, p, q, a, y)
            print(f"\nРезультат проверки: {'✅ ПОДПИСЬ ВЕРНА' if valid else '❌ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА'}")

if __name__ == "__main__":
    main()