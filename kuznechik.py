import sys

# ================= S-блок и обратные подстановки =================
# Таблица прямого нелинейного преобразования (256 байт).
# Каждый байт заменяется соответствующим значением из этого списка.
PI = [
    252,238,221, 17,207,110, 49, 22,251,196,250,218, 35,197,  4, 77,
    233,119,240,219,147, 46,153,186, 23, 54,241,187, 20,205, 95,193,
    249, 24,101, 90,226, 92,239, 33,129, 28, 60, 66,139,  1,142, 79,
      5,132,  2,174,227,106,143,160,  6, 11,237,152,127,212,211, 31,
    235, 52, 44, 81,234,200, 72,171,242, 42,104,162,253, 58,206,204,
    181,112, 14, 86,  8, 12,118, 18,191,114, 19, 71,156,183, 93,135,
     21,161,150, 41, 16,123,154,199,243,145,120,111,157,158,178,177,
     50,117, 25, 61,255, 53,138,126,109, 84,198,128,195,189, 13, 87,
    223,245, 36,169, 62,168, 67,201,215,121,214,246,124, 34,185,  3,
    224, 15,236,222,122,148,176,188,220,232, 40, 80, 78, 51, 10, 74,
    167,151, 96,115, 30,  0, 98, 68, 26,184, 56,130,100,159, 38, 65,
    173, 69, 70,146, 39, 94, 85, 47,140,163,165,125,105,213,149, 59,
      7, 88,179, 64,134,172, 29,247, 48, 55,107,228,136,217,231,137,
    225, 27,131, 73, 76, 63,248,254,141, 83,170,144,202,216,133, 97,
     32,113,103,164, 45, 43,  9, 91,203,155, 37,208,190,229,108, 82,
     89,166,116,210,230,244,180,192,209,102,175,194, 57, 75, 99,182,
]

# Обратная таблица замен (InvS). Строится автоматически: PI_INV[PI[i]] = i.
PI_INV = [0] * 256
for i, v in enumerate(PI):
    PI_INV[v] = i

# Модуль неприводимого многочлена для поля GF(2^8): x^8 + x^7 + x^6 + x + 1 = 0x1C3
GF_MOD = 0x1C3

def gf_mul(a, b):
    """Умножение двух чисел в поле GF(2^8) по модулю 0x1C3."""
    result = 0
    while b:
        if b & 1:
            result ^= a          # если младший бит b равен 1, добавляем a к результату
        a <<= 1                  # умножаем a на x
        if a & 0x100:            # если степень превысила 7, приводим по модулю
            a ^= GF_MOD
        b >>= 1
    return result

# Коэффициенты для линейного преобразования l (берутся из стандарта)
L_COEFFS = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

def l_func(a):
    """Линейная комбинация всех 16 байт вектора a с фиксированными коэффициентами в GF(2^8)."""
    result = 0
    for i in range(16):
        result ^= gf_mul(L_COEFFS[i], a[i])
    return result

def X(k, a):
    """Операция X[k](a) = k XOR a (побайтовый XOR двух 16-байтных векторов)."""
    return [k[i] ^ a[i] for i in range(16)]

def S(a):
    """Нелинейная подстановка (S-блок): каждый байт заменяется по таблице PI."""
    return [PI[b] for b in a]

def S_inv(a):
    """Обратная нелинейная подстановка (InvS)."""
    return [PI_INV[b] for b in a]

def R(a):
    """
    Один шаг линейного преобразования R.
    Вычисляет новый байт как l_func(a) и выполняет сдвиг вправо:
    R(a15||a14||...||a0) = l(a15..a0) || a15 || a14 || ... || a1.
    """
    new_byte = l_func(a)
    return [new_byte] + a[:-1]

def R_inv(a):
    """
    Обратный шаг R^{-1}.
    Выполняет сдвиг влево и вычисляет новый байт от «хвоста»:
    R^{-1}(a15||a14||...||a0) = a14||...||a0||l(a14..a0,a15).
    """
    tail = a[1:] + [a[0]]
    new_byte = l_func(tail)
    return a[1:] + [new_byte]

def L(a):
    """Линейное преобразование L = R^16 (16 последовательных применений R)."""
    for _ in range(16):
        a = R(a)
    return a

def L_inv(a):
    """Обратное линейное преобразование L^{-1} = (R^{-1})^16."""
    for _ in range(16):
        a = R_inv(a)
    return a

# Генерация 32 итерационных констант для развёртки ключа
def _gen_constants():
    consts = []
    for i in range(1, 33):
        # Константа C_i = L(0,0,...,0, i) – 15 нулей и номер i
        consts.append(L([0] * 15 + [i]))
    return consts

ITER_CONSTS = _gen_constants()

def F(k, a1, a0):
    """
    Функция F (сеть Фейстеля) для развёртки ключа.
    Принимает константу k и два 16-байтных вектора a1, a0.
    Возвращает (новый a1, новый a0).
    """
    # L(S(X(k, a1))) – основное преобразование
    lsx = L(S(X(k, a1)))
    # XOR результата с a0 и обмен местами
    return X(lsx, a0), a1

def key_schedule(key_bytes):
    """
    Развёртка 256-битного ключа (32 байта) в 10 раундовых ключей.
    Возвращает список из 10 ключей (каждый – список 16 байт).
    """
    k1 = list(key_bytes[:16])          # первые 16 байт – K1
    k2 = list(key_bytes[16:])          # вторые 16 байт – K2
    keys = [k1, k2]                    # начальные ключи
    a, b = k1[:], k2[:]                # рабочие переменные
    # 4 итерации по 8 шагов
    for i in range(4):
        for j in range(8):
            a, b = F(ITER_CONSTS[8 * i + j], a, b)
        keys.append(a[:])              # после каждых 8 шагов сохраняем a и b
        keys.append(b[:])
    return keys                        # всего 10 ключей (индексы 0..9)

def encrypt_block(plain_bytes, round_keys):
    """
    Шифрование одного 128-битного блока (16 байт).
    Выполняет 9 полных раундов (X, S, L) и один заключительный (только X).
    """
    a = list(plain_bytes)
    for i in range(9):                 # раунды 1..9
        a = L(S(X(round_keys[i], a)))
    return bytes(X(round_keys[9], a))  # последний раунд: только XOR с K10

def decrypt_block(cipher_bytes, round_keys):
    """
    Расшифрование одного 128-битного блока.
    Порядок раундов обратный: сначала X с K10, затем 9 обратных раундов.
    """
    a = list(cipher_bytes)
    a = X(round_keys[9], a)            # отмена последнего раунда шифрования
    for i in range(8, -1, -1):         # раунды 9..1 в обратном порядке
        a = X(round_keys[i], S_inv(L_inv(a)))
    return bytes(a)

# PKCS#7-паддинг (дополнение до длины, кратной 16)
def _pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n] * n)

def _pkcs7_unpad(data):
    n = data[-1]
    if n < 1 or n > 16:
        raise ValueError("Некорректный padding")
    return data[:-n]

def encrypt_ecb(data, key_bytes, use_padding=True):
    """
    Шифрование в режиме ECB (простая замена).
    Если use_padding=True, автоматически дополняет PKCS#7,
    иначе требует, чтобы длина была кратна 16.
    """
    rk = key_schedule(key_bytes)
    if use_padding:
        data = _pkcs7_pad(data)
    else:
        if len(data) % 16 != 0:
            raise ValueError("Длина данных должна быть кратна 16 байтам (или используйте use_padding=True)")
    # разбиваем данные на 16-байтные блоки и шифруем каждый независимо
    return b''.join(encrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))

def decrypt_ecb(data, key_bytes, use_padding=True):
    """Расшифрование в режиме ECB (аналогично шифрованию, но с расшифрованием блоков)."""
    if len(data) % 16 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 16 байтам")
    rk = key_schedule(key_bytes)
    dec = b''.join(decrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))
    return _pkcs7_unpad(dec) if use_padding else dec

def format_hex(data: bytes, group: int = 4) -> str:
    """Возвращает hex-строку, сгруппированную по group байт с пробелами."""
    return ' '.join(data[i:i+group].hex().upper() for i in range(0, len(data), group))

# ================= Работа с русским текстом (с пробелами) =================
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"   # 32 буквы
L2N = {c: i+1 for i, c in enumerate(ALPHABET)}   # буква -> код 1..32
N2L = {i+1: c for i, c in enumerate(ALPHABET)}   # код -> буква

SPACE_CODE = 33          # специальный код для пробела

def preprocess(text):
    """
    Предварительная обработка текста перед шифрованием.
    Приводит к нижнему регистру, заменяет 'ё' на 'е',
    знаки препинания на кодовые слова (запятая -> 'зпт', точка -> 'тчк'),
    а пробелы оставляет как есть.
    """
    res = []
    for ch in text.lower():
        if ch == 'ё':
            ch = 'е'
        if ch == ',':
            res.append('зпт')
        elif ch == '.':
            res.append('тчк')
        elif ch == ' ':
            res.append(' ')         # пробел сохраняется
        elif ch in ALPHABET:
            res.append(ch)
        # остальные символы игнорируем
    return ''.join(res)

def postprocess(text):
    """Восстановление знаков препинания (пробелы уже присутствуют)."""
    return text.replace('зпт', ',').replace('тчк', '.')

def text_to_bytes_ru(text):
    """
    Преобразует подготовленную строку в байты.
    Каждая буква заменяется кодом 1..32, пробел – кодом 33.
    """
    result = []
    for c in text:
        if c == ' ':
            result.append(SPACE_CODE)
        else:
            result.append(L2N[c])
    return bytes(result)

def bytes_to_text_ru(data):
    """
    Обратное преобразование байтов в строку.
    Коды 1..32 интерпретируются как буквы, код 33 – как пробел.
    """
    result = []
    for b in data:
        if b == SPACE_CODE:
            result.append(' ')
        elif 1 <= b <= 32:
            result.append(N2L[b])
        # остальные значения игнорируем
    return ''.join(result)

def encrypt_russian(plain, key_hex):
    """
    Полное шифрование текста на русском языке.
    plain – исходный текст,
    key_hex – ключ в виде 64-символьной hex-строки.
    Возвращает зашифрованные байты.
    """
    processed = preprocess(plain)
    if not processed:
        raise ValueError("Текст пуст после предобработки")
    data = text_to_bytes_ru(processed)
    key  = bytes.fromhex(key_hex)
    enc  = encrypt_ecb(data, key, use_padding=True)
    return enc                      # возвращаем bytes

def decrypt_russian(cipher_hex, key_hex):
    """
    Полное расшифрование текста на русском языке.
    cipher_hex – шифртекст в hex-строке (возможны пробелы),
    key_hex – ключ.
    Возвращает расшифрованную строку.
    """
    key = bytes.fromhex(key_hex)
    enc = bytes.fromhex(cipher_hex)
    dec = decrypt_ecb(enc, key, use_padding=True)
    return bytes_to_text_ru(dec)

def run_gost_test():
    """Тест по ГОСТ Р 34.12-2015 (приложение А.1) для проверки корректности."""
    print("=" * 65)
    print("  ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.1 (КУЗНЕЧИК)")
    print("=" * 65)

    KEY   = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    PLAIN    = bytes.fromhex("1122334455667700ffeeddccbbaa9988")
    EXPECTED = "7f679d90bebc24305a468d42b9d4edcd"

    EXP_KEYS = [
        "8899aabbccddeeff0011223344556677",
        "fedcba98765432100123456789abcdef",
        "db31485315694343228d2b3bef05d129",
        "57646468c44a5e28d3e59246f429f1ac",
        "bd079435165c6432b532e82834da581b",
        "51e640757e8745de705727265a0098b1",
        "5a7925017b9fdd3ed72a91a22286f984",
        "bb44e25378c73123a5f32f73cdb6e517",
        "72e9dd7416bcf45b755dbaa88e4a4043",
    ]

    rk = key_schedule(KEY)

    print("── Раундовые ключи K1..K9 (сравнение с ГОСТ А.1.4) ──")
    for i in range(9):
        kh  = format_hex(bytes(rk[i]), group=4)
        exp = EXP_KEYS[i]
        ok  = '✅' if kh.replace(' ', '') == exp else '❌'
        print(f"  K{i+1:2d}: {kh}  {ok}")
    print(f"  K10: {format_hex(bytes(rk[9]), group=4)}")

    print("── Промежуточные шаги (А.1.5) ──")
    EXP_STEPS = [
        ("X[K1](a)",    "99bb99ff99bb99ffffffffffffffffff"),
        ("S(X[K1](a))", "e87de8b6e87de8b6b6b6b6b6b6b6b6b6"),
        ("LSX[K1](a)",  "e297b686e355b0a1cf4a2f9249140830"),
    ]
    a  = list(PLAIN)
    xk = X(rk[0], a)
    sx = S(xk)
    lsx = L(sx)
    steps = [bytes(xk).hex(), bytes(sx).hex(), bytes(lsx).hex()]
    for (name, exp), got in zip(EXP_STEPS, steps):
        ok = '✅' if got == exp else '❌'
        print(f"  {name:<18}: {format_hex(bytes.fromhex(got), group=4)}  {ok}")

    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc,   rk)

    print(f"── Шифрование блока ──")
    print(f"  Открытый : {format_hex(PLAIN, group=4)}")
    print(f"  Ожидается: {EXPECTED}")
    print(f"  Получено : {format_hex(enc, group=4)}")
    print(f"  Результат: {'✅ ВЕРНО' if enc.hex() == EXPECTED else '❌ ОШИБКА'}")
    print(f"── Расшифрование блока ──")
    print(f"  Шифртекст: {format_hex(enc, group=4)}")
    print(f"  Получено : {format_hex(dec, group=4)}")
    print(f"  Результат: {'✅ ВЕРНО' if dec == PLAIN else '❌ ОШИБКА'}")

    print(f"── Тест на тексте >1000 байт ──")
    long_text = b"Kuznyechik GOST R 34.12-2015 block cipher test data. " * 20
    enc2 = encrypt_ecb(long_text, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2,      KEY, use_padding=True)
    ok2  = dec2 == long_text
    print(f"  Длина       : {len(long_text)} байт")
    print(f"  Зашифровано : {len(enc2)} байт")
    print(f"  Расшифровано: {'✅ Совпадает' if ok2 else '❌ Не совпадает'}")
    print(f"  Шифртекст   : {format_hex(enc2[:32], group=4)}...")

def get_key(prompt="Ключ (64 hex, Enter=тестовый): "):
    """Запрос ключа у пользователя. При пустом вводе возвращает тестовый ключ."""
    kh = input(prompt).strip().replace(' ', '')
    if not kh:
        kh = "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"
        print(f"  Используется тестовый ключ: {kh}")
    if len(kh) != 64 or not all(c in '0123456789abcdefABCDEF' for c in kh):
        raise ValueError("Ключ должен содержать ровно 64 hex-символа")
    return kh

def main():
    """Главное меню программы."""
    print("╔" + "═" * 63 + "╗")
    print("║{:^63}║".format("КУЗНЕЧИК — ГОСТ Р 34.12-2015"))
    print("╚" + "═" * 63 + "╝")

    while True:
        print("МЕНЮ:")
        print("  1. Тест по ГОСТ Р 34.12-2015 (А.1)")
        print("  2. Шифрование  (русский текст)")
        print("  3. Расшифрование (русский текст)")
        print("  4. Шифрование  (hex данные / контрольные примеры)")
        print("  5. Расшифрование (hex данные)")
        print("  0. Выход")
        ch = input("Выбор: ").strip()

        if ch == "0":
            print("До свидания!")
            sys.exit(0)

        elif ch == "1":
            run_gost_test()

        elif ch == "2":
            # Шифрование русского текста (с пробелами и знаками препинания)
            try:
                kh  = get_key()
                txt = input("Текст (русские буквы): ").strip()
                enc_bytes = encrypt_russian(txt, kh)
                print(f"Шифртекст (hex): {format_hex(enc_bytes, group=4)}")
                save = input("Сохранить в файл? (y/n): ").strip().lower()
                if save == 'y':
                    fn = input("Имя файла (kuz_cipher.bin): ").strip() or "kuz_cipher.bin"
                    open(fn, 'wb').write(enc_bytes)
                    print(f"✅ Сохранено в '{fn}'")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "3":
            # Расшифрование русского текста
            try:
                kh   = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                dec  = decrypt_russian(chex, kh)
                print(f"Расшифрованный текст: {dec}")
                r = input("Восстановить знаки препинания? (y/n): ").strip().lower()
                if r == 'y':
                    print(f"С пунктуацией: {postprocess(dec)}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "4":
            # Шифрование hex-данных (без автопаддинга, если длина кратна 16)
            try:
                kh   = get_key()
                phex = input("Открытый текст (hex): ").strip().replace(' ', '')
                pb   = bytes.fromhex(phex)
                if len(pb) % 16 == 0:
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=False)
                else:
                    print("  Длина не кратна 16 — будет применён PKCS#7 padding")
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=True)
                print(f"Шифртекст (hex): {format_hex(enc, group=4)}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "5":
            # Расшифрование hex-данных
            try:
                kh   = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                cb   = bytes.fromhex(chex)
                p = input("При шифровании использовался padding? (y/n): ").strip().lower()
                use_p = (p == 'y')
                dec = decrypt_ecb(cb, bytes.fromhex(kh), use_padding=use_p)
                print(f"Открытый текст (hex): {format_hex(dec, group=4)}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    main()