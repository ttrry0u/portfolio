import sys
import random

# =====================================================================
# Обработка текста
# =====================================================================
def preprocess(text: str) -> str:
    """
    Предварительная обработка текста перед подписью или проверкой.
    Заменяет точку на 'тчк', запятую на 'зпт', пробел на 'прб'.
    Затем переводит строку в нижний регистр.
    (Буква 'ё' не заменяется, так как в алфавите её нет;
    при необходимости пользователь должен вводить 'е' вместо 'ё'.)
    """
    text = text.replace('.', 'тчк')
    text = text.replace(',', 'зпт')
    text = text.replace(' ', 'прб')
    return text.lower()

def hash_quad(text: str, p: int, verbose: bool = False) -> int:
    """
    Квадратичная хеш-функция по модулю p.
    Для каждого символа обработанного текста:
        h = ((h + код_буквы) ^ 2) mod p
    Код буквы – её позиция в алфавите (1..32).
    Если итоговый хеш равен 0, он заменяется на 1 (чтобы избежать
    проблем с вычислением обратного элемента при проверке).
    При verbose=True выводится подробная таблица вычислений.
    """
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"  # 32 буквы
    h = 0
    if verbose:
        print(f"\n  Формула: h_i = (h_{{i-1}} + индекс(буквы) + 1)² mod {p}")
        print(f"  {'Буква':<6} {'Индекс':<8} {'Вычисление':<38} {'h'}")
        print("  " + "-"*65)
    for ch in text:
        idx = alphabet.index(ch) + 1          # код буквы (1..32)
        h_prev = h
        h = ((h_prev + idx) ** 2) % p         # квадратичное обновление
        if verbose:
            calc = f"({h_prev} + {idx})² % {p} = {(h_prev+idx)**2} % {p}"
            print(f"  '{ch}'    {idx:<8} {calc:<38} {h}")
    result = h if h != 0 else 1               # 0 заменяем на 1
    if verbose and h == 0:
        print("  h = 0 → заменяем на 1")
    return result

# =====================================================================
# Вспомогательные математические функции
# =====================================================================
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

# =====================================================================
# Операции с точками эллиптической кривой
# =====================================================================
def point_add(P, Q, a: int, p: int):
    """
    Сложение двух точек эллиптической кривой y^2 = x^3 + a*x + b (mod p).
    Поддерживает P=O (None) и Q=O, а также удвоение (P=Q).
    Возвращает новую точку [x3, y3] или None (бесконечно удалённую точку).
    """
    # Обработка бесконечно удалённой точки
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = int(P[0]) % p, int(P[1]) % p
    x2, y2 = int(Q[0]) % p, int(Q[1]) % p

    # Если x1 == x2, то либо P = -Q (вертикальная прямая), либо P = Q
    if x1 == x2:
        if y1 != y2 or y1 == 0:    # P = -Q или касательная вертикальна → O
            return None
        # Удвоение: λ = (3*x1^2 + a) / (2*y1) mod p
        try:
            lam = (3 * x1 * x1 + a) % p * mod_inv(2 * y1, p) % p
        except ZeroDivisionError:
            return None
    else:
        # Сложение: λ = (y2 - y1) / (x2 - x1) mod p
        try:
            lam = (y2 - y1) % p * mod_inv(x2 - x1, p) % p
        except ZeroDivisionError:
            return None

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return [int(x3), int(y3)]

def scalar_mult(k: int, P, a: int, p: int):
    """
    Умножение точки P на скаляр k (двоичный метод "удвоить-и-сложить").
    Если k отрицательное, точка предварительно инвертируется по y.
    Возвращает точку k·P или None для бесконечно удалённой точки.
    """
    if k == 0:
        return None
    if k < 0:
        k = -k
        P = [int(P[0]) % p, (-int(P[1])) % p]   # инвертирование точки
    result = None
    addend = [int(P[0]) % p, int(P[1]) % p]
    while k:
        if k & 1:          # если текущий бит k равен 1, прибавляем addend
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)   # удвоение
        k >>= 1
    return result

# =====================================================================
# Вычисление порядка точки (учебная демонстрация)
# =====================================================================
def compute_order(G, a: int, p: int) -> int:
    """
    Наивное вычисление порядка точки G путём перебора кратных 2G, 3G, ...
    до получения бесконечно удалённой точки.
    Выводит таблицу k·G для наглядности.
    Ограничение: до 10000 кратных.
    """
    print(f"\n{'='*60}")
    print(f"  ВЫЧИСЛЕНИЕ ПОРЯДКА q ТОЧКИ G={G}")
    print(f"{'='*60}")
    print(f"  Ищем наименьшее q такое, что q·G = O\n")
    print(f"  {'k':<5} {'k·G'}")
    print(f"  {'-'*30}")
    current = [int(G[0]) % p, int(G[1]) % p]
    for k in range(1, 10000):
        print(f"  {k:<5} {current}")
        nxt = point_add(current, G, a, p)   # (k+1)·G = k·G + G
        if nxt is None:                     # достигнута бесконечно удалённая точка
            q = k + 1
            print(f"  {k+1:<5} O  ← точка на бесконечности!")
            print(f"\n  >>> q = {q}")
            return q
        current = nxt
    raise ValueError("Порядок точки слишком большой (> 10000)")

def get_curve_points(a: int, b: int, p: int):
    """
    Перечисление всех аффинных точек кривой y^2 = x^3 + a*x + b (mod p).
    Возвращает список точек [x, y].
    """
    pts = []
    for x in range(p):
        rhs = (x**3 + a*x + b) % p          # правая часть уравнения
        for y in range(p):
            if (y * y) % p == rhs:          # проверка квадратичного вычета
                pts.append([x, y])
    return pts

# =====================================================================
# ГОСТ Р 34.10-2012 – подпись и проверка
# =====================================================================
def gost2012_sign(text: str, a: int, b: int, p: int, G: tuple, q: int, x_a: int) -> tuple:
    """
    Формирование цифровой подписи по ГОСТ Р 34.10-2012.
    Параметры:
      text – подготовленный текст,
      a, b, p – коэффициенты эллиптической кривой,
      G – базовая точка (порождающая подгруппу порядка q),
      q – порядок точки G,
      x_a – секретный ключ (0 < x_a < q).
    Возвращает (r, s, m), где m – хеш сообщения (по модулю q).
    """
    # Хеш сообщения: сначала полный хеш по модулю p, затем остаток от деления на q
    m = hash_quad(text, p, verbose=False) % q
    # Перебор случайного k (1..q-1)
    candidates = list(range(1, q))
    random.shuffle(candidates)
    for k in candidates:
        C = scalar_mult(k, G, a, p)          # C = k·G
        if C is None:                        # бесконечно удалённая точка – редко, пропускаем
            continue
        r = C[0] % q                         # r = x_C mod q
        s = (k * m + r * x_a) % q            # s = (k*m + r*x) mod q
        if r != 0 and s != 0:               # допустимы только ненулевые компоненты
            return (r, s, m)
    raise ValueError("Не удалось найти подходящее k")

def gost2012_verify(text: str, r: int, s: int, a: int, b: int, p: int, G: tuple, q: int, Y: tuple) -> bool:
    """
    Проверка цифровой подписи по ГОСТ Р 34.10-2012.
    Параметры:
      text – текст,
      r, s – компоненты подписи,
      a, b, p – кривая,
      G – базовая точка,
      q – порядок G,
      Y – открытый ключ (Y = x_a·G).
    Возвращает True, если подпись верна.
    """
    # Вычисляем хеш сообщения заново
    m = hash_quad(text, p, verbose=False) % q
    # Проверка диапазонов компонент подписи
    if not (0 < r < q and 0 < s < q):
        return False
    # h_inv = m^{-1} mod q (с помощью малой теоремы Ферма, q – простое)
    h_inv = pow(m, q - 2, q)
    u1 = (s * h_inv) % q                     # u1 = s * m^{-1} mod q
    u2 = (-r * h_inv) % q                    # u2 = -r * m^{-1} mod q
    # Вычисляем точку R = u1·G + u2·Y
    A1 = scalar_mult(u1, G, a, p)
    A2 = scalar_mult(u2, Y, a, p)
    R = point_add(A1, A2, a, p)
    if R is None:
        return False
    # Подпись верна, если x_R mod q == r
    return R[0] % q == r

# =====================================================================
# Главное меню
# =====================================================================
def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-2012 – ЦИФРОВАЯ ПОДПИСЬ (эллиптические кривые)")
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

        text = input("Введите текст: ")
        text = preprocess(text)
        print(f"Обработанный текст: {text}\n")

        if op == 1:
            # ----- Подписание сообщения -----
            a = int(input(" - Введите a (коэффициент кривой): "))
            b = int(input(" - Введите b (коэффициент кривой): "))
            p = int(input(" - Введите p (простое): "))
            if not is_prime(p):
                print("p должно быть простым!")
                continue
            Gx, Gy = map(int, input(" - Введите G (x y через пробел): ").split())
            G = (Gx, Gy)

            # Вывод всех точек кривой (для учебных целей)
            pts = get_curve_points(a, b, p)
            print(f"\n  Все точки кривой (+ O):")
            for pt in pts:
                print(f"    {pt}")
            print(f"    O (бесконечность)")
            print(f"  Всего точек: {len(pts) + 1}")

            # Определение порядка точки G
            q = compute_order(G, a, p)

            # Ввод секретного ключа
            x_a = int(input(f" - Введите x_A (закрытый ключ, 0 < x_A < {q}): "))
            if not (0 < x_a < q):
                print("x_A должен быть в диапазоне (0, q)!")
                continue

            # Открытый ключ Y = x_a·G
            Y = scalar_mult(x_a, G, a, p)
            print(f"Открытый ключ Y_A = {Y}")

            # Формирование подписи
            try:
                r, s, m = gost2012_sign(text, a, b, p, G, q, x_a)
                print(f"\nПодпись: r = {r}, s = {s}")
                print(f"Хеш сообщения: {m}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif op == 2:
            # ----- Проверка подписи -----
            a = int(input(" - Введите a: "))
            b = int(input(" - Введите b: "))
            p = int(input(" - Введите p: "))
            Gx, Gy = map(int, input(" - Введите G (x y через пробел): ").split())
            G = (Gx, Gy)
            q = int(input(" - Введите q (порядок точки): "))
            Yx, Yy = map(int, input(" - Введите Y (x y через пробел): ").split())
            Y = (Yx, Yy)
            r = int(input(" - Введите r: "))
            s = int(input(" - Введите s: "))
            valid = gost2012_verify(text, r, s, a, b, p, G, q, Y)
            print(f"\nРезультат проверки: {'✅ ПОДПИСЬ ВЕРНА' if valid else '❌ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА'}")

if __name__ == "__main__":
    main()