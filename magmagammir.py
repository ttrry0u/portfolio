import sys
import struct

# Таблицы замен (S-блоки) шифра «Магма» (ГОСТ Р 34.12-2015).
# 8 блоков по 16 значений, задают нелинейную подстановку 4-битных полубайтов.
PI = [
    [12, 4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],
]

def t_transform(x: int) -> int:
    """
    Нелинейное преобразование (S-блоки) 32-битного числа.
    Разбивает x на 8 полубайт, каждый заменяет по своему S-блоку PI[i],
    собирает результат обратно в 32-битное целое.
    """
    result = 0
    for i in range(8):
        nibble = (x >> (4 * i)) & 0xF          # извлекаем i-й полубайт (младший – первый)
        result |= PI[i][nibble] << (4 * i)     # подставляем заменённое значение на место
    return result

def left_shift_11(x: int) -> int:
    """Циклический сдвиг 32-битного числа влево на 11 бит."""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k: int, a: int) -> int:
    """
    Функция g раунда «Магмы»:
    1) (a + k) mod 2^32 – сложение с раундовым ключом,
    2) t_transform – замена в S-блоках,
    3) left_shift_11 – циклический сдвиг влево на 11 бит.
    """
    return left_shift_11(t_transform((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes: bytes) -> list:
    """
    Генерация 32 раундовых ключей из 256-битного ключа (32 байта).
    Ключ интерпретируется как 8 беззнаковых 32-битных чисел (big-endian).
    Расписание: трижды прямо K0..K7, затем один раз обратно K7..K0.
    Возвращает список из 32 целых 32-битных чисел.
    """
    K = list(struct.unpack('>8I', key_bytes))   # распаковываем 8 беззнаковых 32-битных слов
    return K * 3 + K[::-1]                      # K0..K7 трижды + обратный порядок

def magma_encrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Шифрование одного 64-битного блока (8 байт) алгоритмом «Магма».
    round_keys – список из 32 32-битных ключей.
    Возвращает 8 байт шифртекста.
    """
    # Разделяем блок на старшую (a1) и младшую (a0) 32-битные половины
    a1, a0 = struct.unpack('>II', block)
    # 31 раунд сети Фейстеля с обменом половин
    for i in range(31):
        a1, a0 = a0, g(round_keys[i], a0) ^ a1
    # Последний (32-й) раунд без обмена (G*)
    a1 = g(round_keys[31], a0) ^ a1
    # Упаковываем результат обратно в 8 байт
    return struct.pack('>II', a1, a0)

def magma_decrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Расшифрование одного 64-битного блока.
    Полностью идентично шифрованию, но используются ключи в обратном порядке.
    """
    return magma_encrypt_block(block, round_keys[::-1])

def ctr_process(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Шифрование/расшифрование в режиме CTR (гаммирование).
    data – открытый текст или шифртекст (произвольная длина),
    key – 256-битный ключ (32 байта),
    iv  – синхропосылка (8 байт, начальное значение счётчика).
    Возвращает зашифрованные/расшифрованные данные.
    """
    round_keys = key_schedule(key)                   # получаем 32 раундовых ключа
    ctr = int.from_bytes(iv, 'big')                  # преобразуем синхропосылку в 64-битное целое
    out = bytearray()
    # Обрабатываем данные блоками до 8 байт
    for i in range(0, len(data), 8):
        # Гамма = шифрование текущего значения счётчика
        gamma = magma_encrypt_block(ctr.to_bytes(8, 'big'), round_keys)
        chunk = data[i:i+8]                         # текущий фрагмент данных (не более 8 байт)
        # Побайтовый XOR фрагмента с гаммой
        out.extend(b ^ gm for b, gm in zip(chunk, gamma))
        # Инкремент счётчика (по модулю 2^64)
        ctr = (ctr + 1) & 0xFFFFFFFFFFFFFFFF
    return bytes(out)

# ---------- Вспомогательные функции ввода ----------
def input_hex(prompt: str, byte_len: int) -> bytes:
    """Запрашивает у пользователя ровно byte_len байт в виде HEX-строки."""
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) == byte_len * 2:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print(f"  [!] Нужно ровно {byte_len * 2} HEX-символов ({byte_len} байт)")

def input_iv(prompt: str) -> bytes:
    """
    Ввод синхропосылки (IV). Допускается до 16 HEX-символов (8 байт).
    Если длина меньше, строка дополняется нулями справа.
    """
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) > 16:
            print("  [!] IV должен быть не более 16 HEX-символов (8 байт)")
            continue
        if len(raw) % 2 != 0:
            print("  [!] IV должен содержать чётное число HEX-символов")
            continue
        raw = raw.ljust(16, '0')                    # дополняем нулями до 16 символов (8 байт)
        try:
            return bytes.fromhex(raw)
        except ValueError:
            print("  [!] Некорректный HEX")

def input_hex_any(prompt: str) -> bytes:
    """Ввод произвольного количества байт в виде HEX-строки чётной длины."""
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) % 2 == 0 and len(raw) > 0:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print("  [!] Введите корректную HEX-строку чётной длины")

def print_hex(label: str, data: bytes, bsize: int = 8):
    """Форматированный вывод байтовых данных в HEX с группировкой по bsize байт."""
    blocks = ' '.join(data[i:i+bsize].hex().upper()
                      for i in range(0, len(data), bsize))
    print(f"  {label}: {blocks}")

# ---------- Меню операций ----------
def encrypt_menu():
    """Интерактивное шифрование в режиме CTR."""
    print("\n--- ШИФРОВАНИЕ (CTR) ---\n")
    key = input_hex("Ключ           (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_iv("Синхропосылка  (до 16 HEX-символов): ")
    data = input_hex_any("Открытый текст (HEX): ")
    ciphertext = ctr_process(data, key, iv)
    print()
    print_hex("Открытый текст", data)
    print_hex("Шифртекст     ", ciphertext)

def decrypt_menu():
    """Интерактивное расшифрование в режиме CTR."""
    print("\n--- РАСШИФРОВАНИЕ (CTR) ---\n")
    key = input_hex("Ключ           (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_iv("Синхропосылка  (до 16 HEX-символов): ")
    data = input_hex_any("Шифртекст (HEX): ")
    plaintext = ctr_process(data, key, iv)
    print()
    print_hex("Шифртекст     ", data)
    print_hex("Открытый текст", plaintext)

# ---------- Главная программа ----------
if __name__ == "__main__":
    print("=" * 60)
    print("ГАММИРОВАНИЕ CTR (ГОСТ Р 34.13-2015) на основе МАГМЫ")
    print("Блочный шифр ГОСТ Р 34.12-2015, ключ 256 бит, блок 64 бита")
    print("=" * 60)

    while True:
        print("\n" + "─" * 40)
        print("МЕНЮ:")
        print("  1. Зашифровать")
        print("  2. Расшифровать")
        print("  0. Выход")
        print("─" * 40)

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            sys.exit()
        elif choice == "1":
            encrypt_menu()
        elif choice == "2":
            decrypt_menu()
        else:
            print("  [!] Неверный выбор!")