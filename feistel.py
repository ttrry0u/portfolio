# Таблицы замен (S-блоки) для шифра «Магма» (ГОСТ Р 34.12-2015).
# Каждый из 8 блоков содержит 16 значений (0..15), задающих нелинейную подстановку.
PI = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]


def is_valid_hex(text, expected_length):
    """Проверяет, что строка text содержит ровно expected_length шестнадцатеричных символов."""
    if len(text) != expected_length:
        return False
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


def input_hex(prompt, expected_length, description):
    """
    Запрашивает у пользователя шестнадцатеричную строку нужной длины.
    Продолжает запрос до тех пор, пока не будет введено корректное значение.
    """
    while True:
        value = input(prompt).strip().lower()

        if len(value) != expected_length:
            print(f"Ошибка: {description} должен быть {expected_length} HEX символов!")
            print(f"  Вы ввели {len(value)} символов. Попробуйте снова.")
            continue

        try:
            int(value, 16)
            return value
        except ValueError:
            print(f"Ошибка: {description} должен содержать только HEX символы (0-9, a-f)!")
            print(f"  Недопустимые символы в строке: '{value}'")
            continue


def t_transform(a):
    """
    Нелинейное преобразование (S-блоки) 32-битного числа a.
    Разбивает a на 8 полубайт, каждый заменяет по своему S-блоку PI[i],
    и собирает результат обратно в 32-битное число.
    """
    result = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0x0F          # извлекаем i-й полубайт (начиная с младшего)
        substituted = PI[i][nibble]             # замена по таблице
        result |= (substituted << (4 * i))      # вставляем обратно на своё место
    return result


def rotate_left_11(value):
    """Циклический сдвиг 32-битного числа влево на 11 бит."""
    value &= 0xFFFFFFFF                         # обрезаем до 32 бит
    return ((value << 11) | (value >> 21)) & 0xFFFFFFFF


def g_transform(k, a):
    """
    Функция g раунда «Магмы»:
    1) (a + k) mod 2^32,
    2) нелинейная замена t_transform,
    3) циклический сдвиг влево на 11.
    """
    temp = (a + k) & 0xFFFFFFFF                 # сложение с раундовым ключом по модулю 2^32
    temp = t_transform(temp)                    # S-блоки
    temp = rotate_left_11(temp)                 # сдвиг
    return temp


def G_transform(k, a1, a0):
    """
    Один раунд сети Фейстеля (кроме последнего) для шифрования:
    новое левое = правое,
    новое правое = g(k, правое) XOR левое.
    """
    new_a1 = a0
    new_a0 = g_transform(k, a0) ^ a1
    return new_a1, new_a0


def G_star_transform(k, a1, a0):
    """
    Последний (32-й) раунд сети Фейстеля без обмена половин:
    результат: (g(k, a0) XOR a1, a0).
    """
    result_high = g_transform(k, a0) ^ a1
    result_low = a0
    return result_high, result_low


def generate_round_keys(key_hex):
    """
    Генерация 32 раундовых ключей из 256-битного ключа (64 hex-символа).
    Ключ разбивается на 8 частей по 32 бита: K[0]..K[7].
    Расписание: K0..K7 повторяются трижды, затем K7..K0 в обратном порядке.
    Возвращает список из 32 целых 32-битных чисел.
    """
    key_bytes = bytes.fromhex(key_hex)

    if len(key_bytes) != 32:
        raise ValueError("Ключ должен быть длиной 64 символа HEX (256 бит)")

    K = []
    for i in range(8):
        k_bytes = key_bytes[i * 4:(i + 1) * 4]
        K.append(int.from_bytes(k_bytes, byteorder='big'))

    round_keys = []

    # Первые 24 ключа: K0..K7 трижды
    for i in range(8):
        round_keys.append(K[i])
    for i in range(8):
        round_keys.append(K[i])
    for i in range(8):
        round_keys.append(K[i])

    # Последние 8 ключей: K7..K0
    for i in range(7, -1, -1):
        round_keys.append(K[i])

    return round_keys


def magma_encrypt(a, round_keys):
    """
    Шифрование 64-битного блока открытого текста a (целое или hex-строка)
    с использованием 32 раундовых ключей.
    Возвращает целое 64-битное зашифрованное значение.
    """
    if isinstance(a, str):
        a = int(a, 16)

    # Разделяем 64 бита на две 32-битные половины: старшую a1 и младшую a0
    a1 = (a >> 32) & 0xFFFFFFFF
    a0 = a & 0xFFFFFFFF

    # 31 раунд с обменом
    for i in range(31):
        a1, a0 = G_transform(round_keys[i], a1, a0)

    # Последний раунд (без обмена)
    b1, b0 = G_star_transform(round_keys[31], a1, a0)
    b = (b1 << 32) | b0

    return b


def magma_decrypt(b, round_keys):
    """
    Расшифрование 64-битного блока шифртекста b.
    Использует те же раундовые ключи, но в обратном порядке.
    Возвращает исходный открытый 64-битный блок.
    """
    if isinstance(b, str):
        b = int(b, 16)

    b1 = (b >> 32) & 0xFFFFFFFF
    b0 = b & 0xFFFFFFFF

    # Обратные раунды: от 31 до 1 (ключи round_keys[31] .. round_keys[1])
    for i in range(31, 0, -1):
        b1, b0 = G_transform(round_keys[i], b1, b0)

    # Последний обратный раунд с ключом round_keys[0]
    a1, a0 = G_star_transform(round_keys[0], b1, b0)

    a = (a1 << 32) | a0
    return a


def test_gost_example():
    """
    Проверка корректности алгоритма на контрольном примере из ГОСТ Р 34.12-2015 (приложение А.2).
    Использует заданные ключ и открытый текст, сверяет раундовые ключи и результаты шифрования/расшифрования.
    """
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ НА КОНТРОЛЬНОМ ПРИМЕРЕ ИЗ ГОСТ Р 34.12-2015 (А.2)")
    print("=" * 80)

    K = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    print(f"\nКлюч (256 бит):\n{K}")

    round_keys = generate_round_keys(K)

    # Эталонные значения раундовых ключей (из ГОСТ)
    expected_keys = {
        1: 0xffeeddcc, 9: 0xffeeddcc, 17: 0xffeeddcc, 25: 0xfcfdfeff,
        2: 0xbbaa9988, 10: 0xbbaa9988, 18: 0xbbaa9988, 26: 0xf8f9fafb,
        3: 0x77665544, 11: 0x77665544, 19: 0x77665544, 27: 0xf4f5f6f7,
        4: 0x33221100, 12: 0x33221100, 20: 0x33221100, 28: 0xf0f1f2f3,
        5: 0xf0f1f2f3, 13: 0xf0f1f2f3, 21: 0xf0f1f2f3, 29: 0x33221100,
        6: 0xf4f5f6f7, 14: 0xf4f5f6f7, 22: 0xf4f5f6f7, 30: 0x77665544,
        7: 0xf8f9fafb, 15: 0xf8f9fafb, 23: 0xf8f9fafb, 31: 0xbbaa9988,
        8: 0xfcfdfeff, 16: 0xfcfdfeff, 24: 0xfcfdfeff, 32: 0xffeeddcc
    }

    print("\nПроверка раундовых ключей:")
    all_correct = True
    for i in sorted(expected_keys.keys()):
        expected = expected_keys[i]
        actual = round_keys[i - 1]
        status = "✓" if actual == expected else "✗"
        print(f"  K{i:2d} = {actual:08x} (ожидается {expected:08x}) {status}")
        if actual != expected:
            all_correct = False

    if not all_correct:
        print("\nОШИБКА: Раундовые ключи не совпадают!")
        return False

    print("\nВсе раундовые ключи совпадают!")

    a = 0xfedcba9876543210               # открытый текст из ГОСТ

    print(f"\n{'-' * 80}")
    print("ШИФРОВАНИЕ:")
    print(f"Открытый текст (64 бит):    {a:016x}")

    a1 = (a >> 32) & 0xFFFFFFFF
    a0 = a & 0xFFFFFFFF
    print(f"  (a1, a0) = ({a1:08x}, {a0:08x})")

    b = magma_encrypt(a, round_keys)

    print(f"\nЗашифрованный текст:        {b:016x}")
    print(f"Ожидается по ГОСТ:          4ee901e5c2d8ca3d")

    if b == 0x4ee901e5c2d8ca3d:
        print("ШИФРОВАНИЕ УСПЕШНО!")
    else:
        print("ОШИБКА ШИФРОВАНИЯ!")
        return False

    print(f"\n{'-' * 80}")
    print("РАСШИФРОВАНИЕ:")
    print(f"Зашифрованный текст:        {b:016x}")

    d = magma_decrypt(b, round_keys)

    print(f"Расшифрованный текст:       {d:016x}")
    print(f"Ожидается (исходный текст): {a:016x}")

    if d == a:
        print("РАСШИФРОВАНИЕ УСПЕШНО!")
        print("\n" + "=" * 80)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ! АЛГОРИТМ РАБОТАЕТ КОРРЕКТНО!")
        print("=" * 80)
        return True
    else:
        print("ОШИБКА РАСШИФРОВАНИЯ!")
        return False


# ====================== Основная программа ======================
print("=" * 80)
print("Шифр МАГМА (ГОСТ Р 34.12-2015)")
print("Шифрование 64-битных чисел")
print("=" * 80)

while True:
    print("\n" + "=" * 80)
    print("Выберите действие:")
    print("1 - Зашифровать 64-битное число")
    print("2 - Расшифровать 64-битное число")
    print("0 - Выход")

    choice = input("\nВаш выбор: ")

    if choice == '0':
        print("\nДо свидания!")
        break

    elif choice == '1':
        print("\n" + "-" * 80)
        print("ШИФРОВАНИЕ 64-БИТНОГО ЧИСЛА (МАГМА)")
        print("-" * 80)

        plaintext = input_hex(
            "Введите открытый текст (16 HEX символов): ",
            16,
            "Открытый текст"
        )

        key = input_hex(
            "Введите ключ (64 HEX символа, 256 бит): ",
            64,
            "Ключ"
        )

        round_keys = generate_round_keys(key)

        plaintext_int = int(plaintext, 16)
        ciphertext_int = magma_encrypt(plaintext_int, round_keys)

        print(f"\n{'=' * 80}")
        print(f"Открытый текст:      {plaintext_int:016x}")
        print(f"Ключ:                {key}")
        print(f"Зашифрованный текст: {ciphertext_int:016x}")
        print(f"{'=' * 80}")

    elif choice == '2':
        print("\n" + "-" * 80)
        print("РАСШИФРОВАНИЕ 64-БИТНОГО ЧИСЛА")
        print("-" * 80)

        ciphertext = input_hex(
            "Введите зашифрованный текст (16 HEX символов, 64 бита): ",
            16,
            "Зашифрованный текст"
        )

        key = input_hex(
            "Введите ключ (64 HEX символа, 256 бит): ",
            64,
            "Ключ"
        )

        round_keys = generate_round_keys(key)

        ciphertext_int = int(ciphertext, 16)
        plaintext_int = magma_decrypt(ciphertext_int, round_keys)

        print(f"\n{'=' * 80}")
        print(f"Зашифрованный текст:  {ciphertext_int:016x}")
        print(f"Ключ:                 {key}")
        print(f"Расшифрованный текст: {plaintext_int:016x}")
        print(f"{'=' * 80}")

    else:
        print("\nНеверный выбор. Попробуйте снова.")