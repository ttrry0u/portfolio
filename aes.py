import re

# ================= S-блоки и константы AES =================
# Таблица прямого нелинейного преобразования (SubBytes).
# SBOX[i][j] = значение, на которое заменяется байт 0xij (i – старший полубайт, j – младший).
SBOX = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
]

# Таблица обратного нелинейного преобразования (InvSubBytes).
INV_SBOX = [
    [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb],
    [0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb],
    [0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e],
    [0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25],
    [0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92],
    [0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84],
    [0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06],
    [0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b],
    [0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73],
    [0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e],
    [0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b],
    [0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4],
    [0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f],
    [0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef],
    [0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61],
    [0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
]

# Раундовые константы для развёртки ключа.
# Rcon[i] = {02}^{i} в поле GF(2^8), где i начинается с 1.
Rcon = [
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a
]

# ================= Базовые операции AES =================
def sub_byte(b):
    """
    Прямая нелинейная замена одного байта (SubByte).
    Старший полубайт определяет строку, младший – столбец в таблице SBOX.
    """
    return SBOX[b >> 4][b & 0x0F]

def inv_sub_byte(b):
    """
    Обратная нелинейная замена одного байта (InvSubByte).
    Аналогично используется таблица INV_SBOX.
    """
    return INV_SBOX[b >> 4][b & 0x0F]

def sub_bytes(state):
    """Применяет SubByte ко всем байтам матрицы состояния (4x4)."""
    for i in range(4):
        for j in range(4):
            state[i][j] = sub_byte(state[i][j])

def inv_sub_bytes(state):
    """Применяет InvSubByte ко всем байтам матрицы состояния."""
    for i in range(4):
        for j in range(4):
            state[i][j] = inv_sub_byte(state[i][j])

def shift_rows(state):
    """
    Циклический сдвиг строк матрицы состояния влево.
    Строка 0: без сдвига,
    строка 1: сдвиг на 1,
    строка 2: сдвиг на 2,
    строка 3: сдвиг на 3.
    """
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][1], state[1][2], state[1][3], state[1][0]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][3], state[3][0], state[3][1], state[3][2]

def inv_shift_rows(state):
    """
    Обратный циклический сдвиг строк (вправо).
    Строка 1: сдвиг на 1 вправо (т.е. на 3 влево),
    строка 2: сдвиг на 2 вправо,
    строка 3: сдвиг на 3 вправо.
    """
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][3], state[1][0], state[1][1], state[1][2]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][1], state[3][2], state[3][3], state[3][0]

def xtime(b):
    """
    Умножение на число {02} в поле GF(2^8) по модулю многочлена x^8 + x^4 + x^3 + x + 1.
    Используется в операции MixColumns.
    """
    if b & 0x80:                     # Если старший бит установлен (b >= 128),
        return ((b << 1) & 0xFF) ^ 0x1B   # выполняем сдвиг и XOR с 0x1B.
    else:
        return (b << 1) & 0xFF        # иначе просто сдвигаем.

def mix_columns(state):
    """
    Перемешивание столбцов (MixColumns).
    Каждый столбец умножается на фиксированную матрицу 4x4 в поле GF(2^8).
    Матрица:
        [02 03 01 01]
        [01 02 03 01]
        [01 01 02 03]
        [03 01 01 02]
    """
    for c in range(4):
        s0 = state[0][c]
        s1 = state[1][c]
        s2 = state[2][c]
        s3 = state[3][c]
        # Результат умножения: новые значения столбца вычисляются как сумма произведений
        state[0][c] = xtime(s0) ^ (xtime(s1) ^ s1) ^ s2 ^ s3
        state[1][c] = s0 ^ xtime(s1) ^ (xtime(s2) ^ s2) ^ s3
        state[2][c] = s0 ^ s1 ^ xtime(s2) ^ (xtime(s3) ^ s3)
        state[3][c] = (xtime(s0) ^ s0) ^ s1 ^ s2 ^ xtime(s3)

def inv_mix_columns(state):
    """
    Обратное перемешивание столбцов (InvMixColumns).
    Использует умножение на обратную матрицу.
    Коэффициенты: {0e}, {0b}, {0d}, {09} в соответствующих позициях.
    """
    for c in range(4):
        s0 = state[0][c]
        s1 = state[1][c]
        s2 = state[2][c]
        s3 = state[3][c]
        state[0][c] = mul(0x0e, s0) ^ mul(0x0b, s1) ^ mul(0x0d, s2) ^ mul(0x09, s3)
        state[1][c] = mul(0x09, s0) ^ mul(0x0e, s1) ^ mul(0x0b, s2) ^ mul(0x0d, s3)
        state[2][c] = mul(0x0d, s0) ^ mul(0x09, s1) ^ mul(0x0e, s2) ^ mul(0x0b, s3)
        state[3][c] = mul(0x0b, s0) ^ mul(0x0d, s1) ^ mul(0x09, s2) ^ mul(0x0e, s3)

def mul(a, b):
    """
    Умножение двух чисел в поле GF(2^8) с использованием многократного xtime.
    Реализует русский крестьянский алгоритм: для каждого бита b, равного 1,
    к результату прибавляется a, после чего a удваивается (xtime).
    """
    result = 0
    while b:
        if b & 1:
            result ^= a
        a = xtime(a)
        b >>= 1
    return result

def add_round_key(state, round_key):
    """
    Побайтовый XOR матрицы состояния с матрицей раундового ключа.
    Раундовый ключ также представлен как список списков 4x4.
    """
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]

# ================= Развёртка ключа =================
def key_expansion(key):
    """
    Генерация раундовых ключей из исходного ключа.
    Параметры:
        key – байтовый массив длиной 16, 24 или 32 байта (AES-128, AES-192, AES-256).
    Возвращает список матриц 4x4 (по одной на раунд + начальный).
    """
    Nk = len(key) // 4          # количество 32-битных слов в ключе (4,6,8)
    Nr = Nk + 6                 # количество раундов (10,12,14)

    # Инициализируем массив слов w длиной 4*(Nr+1)
    w = []
    # Копируем начальные слова из ключа
    for i in range(Nk):
        w.append(int.from_bytes(key[i*4:(i+1)*4], 'big'))

    # Генерируем расширенные слова
    for i in range(Nk, 4*(Nr+1)):
        temp = w[i-1]
        if i % Nk == 0:                              # каждое слово, кратное Nk
            # Циклический сдвиг влево на 8 бит (RotWord)
            temp = ((temp << 8) & 0xFFFFFFFF) | (temp >> 24)
            # SubWord – замена каждого байта через SBOX
            temp = (sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (sub_byte((temp >> 8) & 0xFF) << 8) | \
                   sub_byte(temp & 0xFF)
            # XOR с раундовой константой
            temp ^= (Rcon[i//Nk - 1] << 24)
        elif Nk > 6 and i % Nk == 4:                # для AES-256 дополнительный SubWord
            temp = (sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (sub_byte((temp >> 8) & 0xFF) << 8) | \
                   sub_byte(temp & 0xFF)
        w.append(w[i-Nk] ^ temp)                    # XOR с предыдущим словом на расстоянии Nk

    # Преобразуем слова в список раундовых ключей (каждый – матрица 4x4)
    round_keys = []
    for round in range(Nr+1):
        key_matrix = [[0]*4 for _ in range(4)]
        for col in range(4):                        # каждый столбец матрицы – одно слово
            word = w[round*4 + col]
            # Байты слова распределяются по строкам: старший байт в строку 0
            key_matrix[0][col] = (word >> 24) & 0xFF
            key_matrix[1][col] = (word >> 16) & 0xFF
            key_matrix[2][col] = (word >> 8) & 0xFF
            key_matrix[3][col] = word & 0xFF
        round_keys.append(key_matrix)
    return round_keys

# ================= Шифрование / расшифрование одного блока =================
def aes_encrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Шифрование одного 16-байтного блока алгоритмом AES.
    Параметры:
        block – ровно 16 байт открытого текста,
        round_keys – список раундовых ключей (матриц 4x4).
    Возвращает 16 байт шифртекста.
    """
    if len(block) != 16:
        raise ValueError("Блок должен быть 16 байт")

    # Загрузка блока в матрицу состояния state (по столбцам)
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]

    Nr = len(round_keys) - 1               # количество раундов (10,12,14)

    # Начальное сложение с ключом раунда 0
    add_round_key(state, round_keys[0])

    # Основные раунды (1..Nr-1): SubBytes, ShiftRows, MixColumns, AddRoundKey
    for round in range(1, Nr):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, round_keys[round])

    # Последний раунд (без MixColumns)
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_keys[Nr])

    # Преобразование состояния обратно в 16 байт (по столбцам)
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

def aes_decrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Расшифрование одного 16-байтного блока алгоритмом AES.
    Параметры:
        block – шифртекст (16 байт),
        round_keys – те же раундовые ключи, что использовались при шифровании.
    Возвращает 16 байт открытого текста.
    """
    if len(block) != 16:
        raise ValueError("Блок должен быть 16 байт")

    # Загрузка блока в матрицу состояния (по столбцам)
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]

    Nr = len(round_keys) - 1

    # Начало с последним раундовым ключом (обратный порядок)
    add_round_key(state, round_keys[Nr])

    # Основные раунды в обратном порядке: InvShiftRows, InvSubBytes, AddRoundKey, InvMixColumns
    for round in range(Nr-1, 0, -1):
        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, round_keys[round])
        inv_mix_columns(state)

    # Последний раунд (без InvMixColumns)
    inv_shift_rows(state)
    inv_sub_bytes(state)
    add_round_key(state, round_keys[0])

    # Преобразование состояния в байты
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

# ================= Подготовка текста =================
def prepare_text(raw_text: str, mode: str = 'text') -> bytes:
    """
    Преобразование входного текста в байты для шифрования.
    Для mode='text': заменяет ',' -> 'зпт', '.' -> 'тчк', пробел -> 'прбл' и кодирует в UTF-8.
    Для mode='hex': просто преобразует hex-строку в байты.
    """
    if mode == 'hex':
        hex_str = raw_text.strip().replace(' ', '').replace('0x', '')
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex-строка должна содержать чётное число символов")
        return bytes.fromhex(hex_str)
    else:
        # Заменяем знаки препинания и пробелы на кодовые слова, НЕ удаляем пробелы
        text = raw_text.replace(',', 'зпт').replace('.', 'тчк').replace(' ', 'прбл')
        return text.encode('utf-8')

def prepare_key(key_input: str) -> bytes:
    """
    Проверка и преобразование ключа из hex-строки в байты.
    Допустимые длины: 32, 48, 64 символа (AES-128, AES-192, AES-256).
    """
    key_hex = key_input.strip().replace(' ', '').replace('0x', '')
    if len(key_hex) not in (32, 48, 64):
        raise ValueError("Ключ должен быть 32, 48 или 64 шестнадцатеричных символа "
                         "(AES-128, AES-192 или AES-256)")
    return bytes.fromhex(key_hex)

def bytes_to_hex_str(data: bytes) -> str:
    """Преобразование байтов в заглавную hex-строку без пробелов."""
    return data.hex().upper()

def hex_str_to_bytes(hex_str: str) -> bytes:
    """Преобразование hex-строки (с возможными пробелами) в байты."""
    hex_str = hex_str.strip().replace(' ', '').replace('0x', '')
    return bytes.fromhex(hex_str)

# ================= Дополнение / удаление паддинга =================
def pad_data(data: bytes) -> bytes:
    """
    Дополнение данных нулевыми байтами до длины, кратной 16 (AES блок).
    Если длина уже кратна 16, данные возвращаются без изменений.
    """
    padding_len = 16 - (len(data) % 16)
    if padding_len == 16:
        return data
    else:
        return data + b'\x00' * padding_len

def unpad_data(data: bytes) -> bytes:
    """Удаление нулевых байт, добавленных при pad_data, с конца данных."""
    return data.rstrip(b'\x00')

# ================= Шифрование / расшифрование данных (ECB (каждый блок шифруется независимо и
# одинаково))
# =================
def aes_encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Шифрование произвольных данных в режиме ECB.
    Автоматически дополняет данные до кратности 16 (нулями).
    """
    round_keys = key_expansion(key)               # генерация раундовых ключей
    padded_data = pad_data(data)                  # выравнивание
    encrypted = bytearray()
    # Разбиваем на блоки по 16 байт и шифруем каждый независимо
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        enc_block = aes_encrypt_block(block, round_keys)
        encrypted.extend(enc_block)
    return bytes(encrypted)

def aes_decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Расшифрование данных в режиме ECB.
    После расшифрования удаляет добавленные нули.
    """
    round_keys = key_expansion(key)
    if len(encrypted_data) % 16 != 0:
        raise ValueError("Длина зашифрованных данных должна быть кратна 16 байтам")
    decrypted = bytearray()
    for i in range(0, len(encrypted_data), 16):
        block = encrypted_data[i:i+16]
        dec_block = aes_decrypt_block(block, round_keys)
        decrypted.extend(dec_block)
    return unpad_data(bytes(decrypted))

# ================= Главное меню =================
def main():
    print("=" * 60)
    print("Шифрование/Расшифрование по алгоритму AES (FIPS-197)")
    print("=" * 60)
    print("Ключ: 32, 48 или 64 шестнадцатеричных символа")
    print("      (AES-128, AES-192 или AES-256)")
    print("Режим: ECB (простая замена, как в МАГМЕ)")
    print()

    while True:
        print("\nМеню:")
        print("1. Зашифровать текст (ввод как обычный текст)")
        print("2. Зашифровать данные из hex-строки")
        print("3. Расшифровать данные (из hex-строки)")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            plaintext = input("Введите открытый текст: ")
            key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
            mode = 'text'
        elif choice == '2':
            plaintext = input("Введите открытые данные в hex: ").strip()
            key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
            mode = 'hex'
        elif choice == '3':
            cipher_hex = input("Введите шифртекст (hex): ").strip()
            key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
            try:
                key = prepare_key(key_hex)
                cipher_bytes = hex_str_to_bytes(cipher_hex)
                decrypted_data = aes_decrypt_data(cipher_bytes, key)
                try:
                    plaintext = decrypted_data.decode('utf-8')
                    # Восстанавливаем знаки препинания и пробелы
                    plaintext = plaintext.replace('зпт', ',').replace('тчк', '.').replace('прбл', ' ')
                    print("\nРасшифрованный текст:")
                    print(plaintext)
                except UnicodeDecodeError:
                    print("\nРасшифрованные данные (hex):")
                    print(decrypted_data.hex().upper())
            except Exception as e:
                print(f"Ошибка: {e}")
            continue
        elif choice == '4':
            break
        else:
            print("Неверный выбор.")
            continue

        try:
            key = prepare_key(key_hex)
            data_bytes = prepare_text(plaintext, mode)
            print(f"Подготовленные данные (hex): {bytes_to_hex_str(data_bytes)}")
            encrypted_data = aes_encrypt_data(data_bytes, key)
            print("\nЗашифрованный текст (hex):")
            print(bytes_to_hex_str(encrypted_data))
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()