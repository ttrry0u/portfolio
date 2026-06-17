import random
import math

def is_prime(n):
    """
    Проверка, является ли число простым.
    Используется простой перебор делителей до √n.
    Возвращает True, если n простое, иначе False.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:          # чётные числа больше 2 – составные
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def prime_factors(n):
    """
    Разложение числа n на простые множители.
    Возвращает множество уникальных простых делителей.
    Используется для проверки первообразного корня.
    """
    factors = set()
    # Извлекаем множитель 2
    while n % 2 == 0:
        factors.add(2)
        n //= 2
    # Нечётные множители
    p = 3
    while p * p <= n:
        while n % p == 0:
            factors.add(p)
            n //= p
        p += 2
    if n > 1:               # остался простой множитель > √n
        factors.add(n)
    return factors

def is_primitive_root(a, n):
    """
    Проверка, является ли a первообразным корнем по модулю n.
    Для простого n число a является первообразным корнем, если
    его порядок равен φ(n) = n-1. Проверяется, что a^{(n-1)/q} ≠ 1 mod n
    для всех простых делителей q числа n-1.
    Возвращает True, если a – первообразный корень.
    """
    if a <= 1 or a >= n:
        return False
    phi = n - 1
    factors = prime_factors(phi)
    for q in factors:
        if pow(a, phi // q, n) == 1:   # если a в степени phi/q даёт 1, порядок меньше phi
            return False
    return True

def check_key_collisions(Y_A, Y_B, secret_A, secret_B, shared_a):
    """
    Проверка нежелательных совпадений между ключами.
    Формирует список предупреждений, если открытые ключи совпадают
    с секретными или друг с другом.
    """
    warnings = []
    if Y_A == secret_A:
        warnings.append(f"  ⚠ Y_A ({Y_A}) совпадает с K_A ({secret_A})!")
    if Y_B == secret_B:
        warnings.append(f"  ⚠ Y_B ({Y_B}) совпадает с K_B ({secret_B})!")
    if Y_A == secret_B:
        warnings.append(f"  ⚠ Y_A ({Y_A}) совпадает с чужим K_B ({secret_B})!")
    if Y_B == secret_A:
        warnings.append(f"  ⚠ Y_B ({Y_B}) совпадает с чужим K_A ({secret_A})!")
    if Y_A == Y_B:
        warnings.append(f"  ⚠ Y_A и Y_B совпадают ({Y_A})!")
    return warnings

def diffie_hellman():
    """
    Реализация протокола обмена ключами Диффи-Хеллмана.
    Пользователь вводит общие параметры n (простое) и a (первообразный корень),
    затем секретные ключи K_A и K_B для двух абонентов.
    Программа вычисляет открытые ключи, проводит обмен,
    вычисляет общий секретный ключ и проверяет его корректность.
    """
    print("=" * 55)
    print("       ПРОТОКОЛ ОБМЕНА КЛЮЧАМИ ДИФФИ-ХЕЛЛМАНА")
    print("=" * 55)

    # --- Ввод общего простого числа n ---
    while True:
        try:
            shared_n = int(input("\n[Общие параметры]\nВведите простое число n: "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not is_prime(shared_n):
            print("Ошибка: n должно быть простым числом!")
            continue
        if shared_n <= 2:
            print("Ошибка: n должно быть > 2!")
            continue
        break

    # --- Ввод основания a ---
    while True:
        try:
            shared_a = int(input(f"Введите основание a (1 < a < {shared_n}): "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not (1 < shared_a < shared_n):
            print(f"Ошибка: a должно быть в диапазоне (1, {shared_n})!")
            continue
        # Проверяем, что a является первообразным корнем по модулю n
        if not is_primitive_root(shared_a, shared_n):
            print(f"  Ошибка: a = {shared_a} не подходит к модулю {shared_n}!")
            print("  Это делает протокол уязвимым к атакам. Выберите другой a.")
            continue
        break

    print(f"\n  Общеизвестные параметры: n = {shared_n}, a = {shared_a}")

    # --- Ввод секретных ключей пользователем ---
    print("\n[Ввод секретных ключей]")
    while True:
        try:
            secret_A = int(input(f"Введите секретный ключ K_A (1 < K_A < {shared_n}): "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not (1 < secret_A < shared_n):
            print(f"Ошибка: K_A должно быть в диапазоне (1, {shared_n})!")
            continue
        # K_A не должно равняться n-1, так как тогда Y_A = a^{n-1} ≡ 1 mod n (вырожденный случай)
        if secret_A == shared_n - 1:
            print(f"  Ошибка: K_A = {shared_n-1} приводит к Y_A = 1 (вырожденный ключ).")
            continue
        break

    while True:
        try:
            secret_B = int(input(f"Введите секретный ключ K_B (1 < K_B < {shared_n}): "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not (1 < secret_B < shared_n):
            print(f"Ошибка: K_B должно быть в диапазоне (1, {shared_n})!")
            continue
        if secret_B == shared_n - 1:
            print(f"  Ошибка: K_B = {shared_n-1} приводит к Y_B = 1 (вырожденный ключ).")
            continue
        break

    # --- Вычисление открытых ключей ---
    Y_A = pow(shared_a, secret_A, shared_n)   # Y_A = a^{K_A} mod n
    Y_B = pow(shared_a, secret_B, shared_n)   # Y_B = a^{K_B} mod n

    # --- Строгие проверки открытых ключей ---
    print(f"\n[Проверка открытых ключей]:")
    if Y_A == 1 or Y_B == 1:
        print("  ✗ Ошибка: один из открытых ключей равен 1 — вырожденный ключ!")
        return
    if Y_A == shared_a or Y_B == shared_a:
        print("  ✗ Ошибка: открытый ключ совпадает с основанием a — это небезопасно!")
        return
    print("  ✓ Открытые ключи корректны.")

    print(f"\n[Шаг 1-2] Секретные ключи (не передаются!):")
    print(f"  K_A = {secret_A}")
    print(f"  K_B = {secret_B}")

    print(f"\n[Шаг 3] Открытые ключи (Y = a^K mod n):")
    print(f"  Y_A = {shared_a}^{secret_A} mod {shared_n} = {Y_A}")
    print(f"  Y_B = {shared_a}^{secret_B} mod {shared_n} = {Y_B}")

    # --- Проверка совпадений ---
    print(f"\n[Проверка совпадений ключей]:")
    warnings = check_key_collisions(Y_A, Y_B, secret_A, secret_B, shared_a)
    if warnings:
        for w in warnings:
            print(w)
        print("  ✗ Обнаружены нежелательные совпадения. Протокол небезопасен.")
        print("=" * 55)
        return
    else:
        print("  ✓ Совпадений не обнаружено — ключи безопасны.")

    # --- Обмен открытыми ключами ---
    print(f"\n[Шаг 4] Обмен по открытому каналу:")
    print(f"  A отправляет B: Y_A = {Y_A}")
    print(f"  B отправляет A: Y_B = {Y_B}")

    # --- Вычисление общего секрета ---
    K_A = pow(Y_B, secret_A, shared_n)   # A вычисляет K = (Y_B)^{K_A} mod n
    K_B = pow(Y_A, secret_B, shared_n)   # B вычисляет K = (Y_A)^{K_B} mod n

    # --- Запрет на общий секрет, равный 1 ---
    if K_A == 1 or K_B == 1:
        print("\n  ✗ Ошибка: общий секретный ключ K = 1 — это недопустимо!")
        print("    Протокол прерван. Попробуйте другие секретные ключи K_A и K_B.")
        print("=" * 55)
        return

    # --- Запрет на совпадение общего ключа с открытыми или секретными ключами ---
    if K_A == Y_A or K_A == Y_B or K_A == secret_A or K_A == secret_B:
        print("\n  ✗ Ошибка: общий секретный ключ K совпадает с одним из ключей (Y_A, Y_B, K_A, K_B)!")
        print("    Протокол прерван. Попробуйте другие секретные ключи K_A и K_B.")
        print("=" * 55)
        return

    print(f"\n[Шаг 5] Вычисление общего секретного ключа K:")
    print(f"  A вычисляет: K_A = Y_B^K_A mod n = {Y_B}^{secret_A} mod {shared_n} = {K_A}")
    print(f"  B вычисляет: K_B = Y_A^K_B mod n = {Y_A}^{secret_B} mod {shared_n} = {K_B}")

    print(f"\n[Доказательство]:")
    print(f"  A: Y_B^K_A mod n = (a^K_B)^K_A mod n = a^(K_A*K_B) mod n = {K_A}")
    print(f"  B: Y_A^K_B mod n = (a^K_A)^K_B mod n = a^(K_B*K_A) mod n = {K_B}")

    # --- Финальная проверка равенства ---
    print(f"\n[Проверка]: K_A = K_B = K?")
    if K_A == K_B:
        print(f"  ✓ Успех! Общий секретный ключ K = {K_A}")
    else:
        print(f"  ✗ Ошибка: K_A ({K_A}) ≠ K_B ({K_B})")
    print("=" * 55)


if __name__ == "__main__":
    diffie_hellman()