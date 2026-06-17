import sys

# Таблицы замен (S-блоки) для шифра «Магма» (ГОСТ Р 34.12-2015).
# 8 блоков по 16 значений, задают нелинейную подстановку 4‑битных полубайтов.
PI = [
    [12,4,6,2,10,5,11,9,14,8,13,7,0,3,15,1],
    [6,8,2,3,9,10,5,12,1,14,4,7,11,13,0,15],
    [11,3,5,8,2,15,10,13,14,1,7,4,12,9,6,0],
    [12,8,2,1,13,4,15,6,7,0,10,5,3,14,9,11],
    [7,15,5,10,8,1,6,13,0,9,3,14,11,4,2,12],
    [5,13,15,6,9,2,12,10,11,7,8,1,4,3,14,0],
    [8,14,2,5,6,9,1,12,15,4,11,0,13,10,3,7],
    [1,7,14,13,0,5,8,3,4,15,10,6,9,12,11,2],
]

def t(a):
    """
    Нелинейное преобразование (S-блоки) 32‑битного числа.
    Разбивает входное значение на 8 полубайт (начиная с младшего),
    каждый полубайт заменяется по своей таблице PI[i],
    и результат собирается обратно в 32‑битное число.
    """
    result = 0
    for i in range(8):
        # Извлекаем i‑й полубайт (сдвиг на 4*i бит вправо, маска 0xF)
        nibble = (a >> (4*i)) & 0xF
        # Замена через i‑й S-блок
        result |= PI[i][nibble] << (4*i)
    return result

def rot11(x):
    """Циклический сдвиг 32‑битного числа влево на 11 бит."""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k, a):
    """
    Функция g раунда «Магмы»:
    1) Сложение с раундовым ключом по модулю 2^32: (a + k) mod 2^32.
    2) Нелинейная замена t.
    3) Циклический сдвиг влево на 11 бит.
    """
    return rot11(t((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes):
    """
    Генерация 32 раундовых ключей из 256‑битного ключа (32 байта).
    Ключ интерпретируется как 8 32‑битных слов (big‑endian).
    Расписание: K0…K7 трижды в прямом порядке, затем K7…K0 в обратном.
    Возвращает список из 32 целых 32‑битных чисел.
    """
    # Разбиваем ключ на 8 32‑битных слов
    k = [int.from_bytes(key_bytes[4*i:4*i+4], 'big') for i in range(8)]
    # Трижды прямой порядок + один раз обратный
    return k * 3 + k[::-1]

def encrypt_block(blk, rk):
    """
    Шифрование одного 64‑битного блока (8 байт) алгоритмом «Магма».
    rk – список из 32 раундовых ключей.
    Сеть Фейстеля: 31 раунд с обменом, последний раунд без обмена (G*).
    """
    # Разделяем блок на старшую (a1) и младшую (a0) 32‑битные половины
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    # 31 раунд с обменом (G)
    for i in range(31):
        a1, a0 = a0, a1 ^ g(rk[i], a0)
    # Последний (32‑й) раунд (G*): только XOR без обмена
    a1 = a1 ^ g(rk[31], a0)
    # Сборка обратно в 8 байт
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def decrypt_block(blk, rk):
    """
    Расшифрование одного 64‑битного блока.
    Использует те же раундовые ключи, но в обратном порядке.
    Начинается с обратного G* (последнего раунда), затем 31 обратный G.
    """
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    # Обратный G* – снятие последнего раунда шифрования
    a1 = a1 ^ g(rk[31], a0)
    # Остальные 31 раунд в обратном порядке (G в обратном направлении)
    for i in range(30, -1, -1):
        a1, a0 = a0 ^ g(rk[i], a1), a1
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def pad(data):
    """
    Дополнение данных до длины, кратной 8 байтам (PKCS#7).
    Если длина уже кратна 8, добавляется целый блок из 8 байт со значением 8.
    """
    n = 8 - len(data) % 8
    return data + bytes([n]*n)

def unpad(data):
    """Удаление PKCS#7‑паддинга (дополнения до кратности): последний байт указывает количество
    добавленных
    байт."""
    return data[:-data[-1]]

def encrypt_ecb(data, key_bytes, use_padding=True):
    """
    Шифрование в режиме ECB.
    data – открытый текст (байты),
    key_bytes – 256‑битный ключ (32 байта),
    use_padding – если True, автоматически дополняет до кратности 8 (PKCS#7),
                   иначе требует, чтобы длина уже была кратна 8.
    Возвращает зашифрованные байты.
    """
    rk = key_schedule(key_bytes)          # получаем 32 раундовых ключа
    if use_padding:
        data = pad(data)
    else:
        if len(data) % 8 != 0:
            raise ValueError("Длина данных должна быть кратна 8 байтам при use_padding=False")
    # Разбиваем данные на блоки по 8 байт, шифруем каждый независимо
    return b''.join(encrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))

def decrypt_ecb(data, key_bytes, use_padding=True):
    """
    Расшифрование в режиме ECB.
    data – шифртекст (байты),
    key_bytes – ключ,
    use_padding – если True, после расшифрования удаляет PKCS#7‑паддинг.
    """
    rk = key_schedule(key_bytes)
    if len(data) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8")
    # Расшифровываем блоки по 8 байт
    dec = b''.join(decrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))
    if use_padding:
        return unpad(dec)
    else:
        return dec

def run_test():
    """Проверка корректности реализации на контрольном примере из ГОСТ Р 34.12-2015 (А.2)."""
    print("="*65)
    print("  ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.2")
    print("="*65)

    # Тестовый ключ и открытый текст
    KEY = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    PLAIN   = bytes.fromhex("fedcba9876543210")
    EXPECTED= "4ee901e5c2d8ca3d"      # эталонный шифртекст

    rk = key_schedule(KEY)
    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc, rk)

    print(f"\nОткрытый : {PLAIN.hex()}")
    print(f"Ожидается: {EXPECTED}")
    print(f"Получено : {enc.hex()}")
    ok = enc.hex() == EXPECTED
    print(f"Шифр     : {'✅ ВЕРНО' if ok else '❌ ОШИБКА'}")
    print(f"Расшифр  : {dec.hex()}  {'✅' if dec==PLAIN else '❌'}")

    # Проверка преобразования t на тестовых векторах (А.2.1)
    print(f"\n── Преобразование t (А.2.1) ──")
    for i,e in [(0xfdb97531,0x2a196f34),(0x2a196f34,0xebd9f03a),
                (0xebd9f03a,0xb039bb3d),(0xb039bb3d,0x68695433)]:
        r = t(i)
        print(f"  t({i:08x}) = {r:08x}  ожид {e:08x}  {'✅' if r==e else '❌'}")

    # Проверка преобразования g (А.2.2)
    print(f"\n── Преобразование g (А.2.2) ──")
    for kv,av,e in [(0x87654321,0xfedcba98,0xfdcbc20c),
                    (0xfdcbc20c,0x87654321,0x7e791a4b),
                    (0x7e791a4b,0xfdcbc20c,0xc76549ec),
                    (0xc76549ec,0x7e791a4b,0x9791c849)]:
        r = g(kv,av)
        print(f"  g[{kv:08x}]({av:08x}) = {r:08x}  ожид {e:08x}  {'✅' if r==e else '❌'}")

    # Тест на длинном тексте (>1000 байт) для проверки режима ECB
    print(f"\n── Тест на тексте >1000 символов ──")
    txt = (b"Magma GOST cipher test. Block=64bit Key=256bit. " * 25)  # 1175 байт
    enc2 = encrypt_ecb(txt, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2, KEY, use_padding=True)
    ok2  = dec2 == txt
    print(f"  Длина текста    : {len(txt)} байт")
    print(f"  Зашифровано     : {len(enc2)} байт")
    print(f"  Расшифровано    : {'✅ Совпадает' if ok2 else '❌ Не совпадает'}")
    print(f"  Шифртекст (hex) : {enc2.hex()[:64]}...")

def input_hex(prompt, required_length=None):
    """
    Ввод hex‑строки с проверкой длины.
    Если required_length задано, требует ровно столько символов.
    """
    s = input(prompt).strip().replace(' ', '')
    if s.startswith('0x') or s.startswith('0X'):
        s = s[2:]
    if required_length is not None and len(s) != required_length:
        raise ValueError(f"Должно быть ровно {required_length} hex-символов")
    return s

def main():
    """Главное меню программы."""
    print("╔" + "═"*63 + "╗")
    print("║{:^63}║".format("МАГМА — ГОСТ Р 34.12-2015"))
    print("╚" + "═"*63 + "╝")

    while True:
        print("\nМЕНЮ:")
        print("  1. Запустить тест ГОСТ Р 34.12-2015")
        print("  2. Зашифровать текст (UTF-8)")
        print("  3. Расшифровать текст (из файла)")
        print("  4. Зашифровать hex-данные (без padding, длина кратна 8)")
        print("  5. Расшифровать hex-данные (без padding)")
        print("  0. Выход")
        ch = input("\nВыбор: ").strip()

        if ch == "0":
            sys.exit(0)

        elif ch == "1":
            run_test()

        elif ch == "2":
            # Шифрование текста (UTF‑8) с автоматическим паддингом
            kh = input("Ключ (64 hex, Enter=тестовый): ").strip() or \
                 "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
            txt = input("Текст: ").encode('utf-8')
            key = bytes.fromhex(kh)
            enc = encrypt_ecb(txt, key, use_padding=True)
            print(f"Шифртекст (hex): {enc.hex()}")
            save = input("Сохранить? (y/n): ").strip().lower()
            if save == 'y':
                fname = input("Файл (magma.bin): ").strip() or "magma.bin"
                open(fname, 'wb').write(enc)
                print(f"✅ Сохранено в {fname}")

        elif ch == "3":
            # Расшифрование текста из файла (UTF‑8)
            fname = input("Файл: ").strip()
            kh = input("Ключ (64 hex): ").strip()
            try:
                enc = open(fname, 'rb').read()
                dec = decrypt_ecb(enc, bytes.fromhex(kh), use_padding=True)
                print(f"Расшифровано: {dec.decode('utf-8')}")
            except Exception as e:
                print(f"❌ {e}")

        elif ch == "4":
            # Шифрование hex‑данных без паддинга (длина должна быть кратна 8)
            try:
                kh = input("Ключ (64 hex, Enter=тестовый): ").strip() or \
                     "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
                plain_hex = input_hex("Введите открытый текст (hex): ")
                plain_bytes = bytes.fromhex(plain_hex)
                key = bytes.fromhex(kh)
                if len(plain_bytes) % 8 != 0:
                    raise ValueError("Длина открытого текста должна быть кратна 8 байтам")
                cipher_bytes = encrypt_ecb(plain_bytes, key, use_padding=False)
                print(f"Шифртекст (hex): {cipher_bytes.hex().lower()}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif ch == "5":
            # Расшифрование hex‑данных без паддинга
            try:
                kh = input("Ключ (64 hex, Enter=тестовый): ").strip() or \
                     "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
                cipher_hex = input_hex("Введите шифртекст (hex): ")
                cipher_bytes = bytes.fromhex(cipher_hex)
                key = bytes.fromhex(kh)
                if len(cipher_bytes) % 8 != 0:
                    raise ValueError("Длина шифртекста должна быть кратна 8 байтам")
                plain_bytes = decrypt_ecb(cipher_bytes, key, use_padding=False)
                print(f"Открытый текст (hex): {plain_bytes.hex().lower()}")
            except Exception as e:
                print(f"Ошибка: {e}")

        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()