import sys
from itertools import zip_longest

# ---------- Алфавит и словари замены ----------
ALPHABET = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
            "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
            "ъ", "ы", "ь", "э", "ю", "я"]

# Замена знаков препинания на служебные слова (для шифрования)
punct_dict = {
    '.': 'тчк',
    ',': 'зпт',
    ';': 'тчз',
    '!': 'вск',
    '"': 'квч',
    '-': 'тире',
    '(': 'скоб',
    ')': 'скобз',
    "'": 'апстр',
    ' ': 'прбл'            # пробел тоже заменяется, чтобы не терять его
}
# Обратный словарь для восстановления знаков после расшифрования
rev_punct = {v: k for k, v in punct_dict.items()}


def digitization(open_text: str) -> str:
    """
    Преобразование текста в битовую последовательность.
    Каждая буква представлена 5-битным двоичным числом (индекс в алфавите от 0 до 31).
    """
    result = ""
    for ch in open_text:
        idx = ALPHABET.index(ch)          # получаем номер буквы (0..31)
        result += format(idx, '05b')      # дополняем до 5 бит ведущими нулями
    return result


def undigitization(bits: str) -> str:
    """
    Обратное преобразование: битовая строка (кратная 5) → исходный текст.
    Биты делятся на группы по 5, каждая группа превращается в число (индекс),
    по которому извлекается буква из алфавита.
    """
    def grouper(n, iterable, fillvalue=None):
        """Вспомогательная функция: группирует итератор по n элементов."""
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)

    # Разбиваем строку на блоки по 5 символов (игнорируем неполный последний блок)
    grouped = [''.join(g) for g in grouper(5, bits, '') if '' not in g]
    result = ""
    for group in grouped:
        idx = int(group, 2)            # двоичная строка -> число
        result += ALPHABET[idx]        # получаем букву
    return result


def prepare_text(txt: str) -> str:
    """
    Подготовка текста к шифрованию:
    - перевод в нижний регистр;
    - замена 'ё' на 'е';
    - замена всех знаков препинания и пробелов на служебные слова по словарю punct_dict.
    """
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    return txt


def restore_text(txt: str) -> str:
    """
    Восстановление исходного текста после расшифрования:
    - обратная замена служебных слов на знаки препинания и пробелы.
    """
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt


def get_key() -> str:
    """
    Ввод ключа пользователем.
    Можно задать либо строку из 64 бит (0 и 1), либо слово из 8 русских букв,
    которое преобразуется в 64-битную последовательность (берутся первые 64 бита).
    """
    print("\nВыберите тип ключа:")
    print("  1. Ввести 64 бита (0 и 1)")
    print("  2. Ввести 8 русских букв")
    key_type = input("Ваш выбор: ").strip()

    if key_type == "1":
        key = input("Введите 64-битный ключ: ").strip()
        if len(key) != 64 or not all(c in '01' for c in key):
            print("Неверный ключ! Нужно ровно 64 символа (0 или 1)")
            sys.exit(1)
        return key
    elif key_type == "2":
        key_word = input("Введите ключ (8 русских букв): ").strip().lower()
        for ch in key_word:
            if ch not in ALPHABET:
                print("Неверный ключ! Только русские буквы (без Ё)")
                sys.exit(1)
        if len(key_word) < 8:
            print("Нужно минимум 8 букв!")
            sys.exit(1)
        if len(key_word) > 8:
            key_word = key_word[:8]
        # Каждая буква кодируется 8-битным значением (её индексом)
        key = ''.join(format(b, '08b') for b in key_word.encode('utf-8'))
        key = key[:64]      # обрезаем до 64 бит
        print(f"  Ключ в битах: {key}")
        return key
    else:
        print("Неверный выбор!")
        sys.exit(1)


def get_frame_number(default: int = 0) -> int:
    """Ввод номера кадра (по умолчанию 0)."""
    try:
        frame_input = input(f"Введите номер кадра (по умолчанию {default}): ").strip()
        if frame_input == "":
            return default
        return int(frame_input)
    except ValueError:
        print(f"  [!] Неверный формат. Использую значение по умолчанию: {default}")
        return default


def generate_gamma(key: str, frame_num: int) -> list:
    """
    Генерация 114-битной гаммы для одного кадра алгоритма A5/1.
    Параметры:
      key       - 64-битная строка (0/1)
      frame_num - 22-битный номер кадра (целое число)
    Возвращает список из 114 целых чисел (0 или 1).
    """
    # Три регистра сдвига, изначально обнулены
    rx = [0] * 19   # R1
    ry = [0] * 22   # R2
    rz = [0] * 23   # R3

    # --- 1. Загрузка ключа (64 такта) ---
    for i in range(64):
        fx = rx[0]
        fy = ry[0]
        fz = rz[0]
        # Сдвиг с обратной связью и подмешиванием бита ключа
        rx = rx[1:] + [fx ^ int(key[i])]
        ry = ry[1:] + [fy ^ int(key[i])]
        rz = rz[1:] + [fz ^ int(key[i])]

    # --- 2. Загрузка номера кадра (22 такта) ---
    frame_bits = format(frame_num, '022b')   # 22 бита, ведущие нули
    for i in range(22):
        fx = rx[0]
        fy = ry[0]
        fz = rz[0]
        rx = rx[1:] + [fx ^ int(frame_bits[i])]
        ry = ry[1:] + [fy ^ int(frame_bits[i])]
        rz = rz[1:] + [fz ^ int(frame_bits[i])]

    # --- 3. 100 тактов холостого хода (перемешивание без выдачи) ---
    for _ in range(100):
        # Мажоритарная функция: 1, если сумма трёх бит >= 2
        majority = 1 if (rx[8] + ry[10] + rz[10]) > 1 else 0

        # Регистр сдвигается, только если его управляющий бит совпадает с majority
        if rx[8] == majority:
            new_bit = rx[13] ^ rx[16] ^ rx[17] ^ rx[18]   # полином R1
            rx = rx[1:] + [new_bit]

        if ry[10] == majority:
            new_bit = ry[20] ^ ry[21]                      # полином R2
            ry = ry[1:] + [new_bit]

        if rz[10] == majority:
            new_bit = rz[7] ^ rz[20] ^ rz[21] ^ rz[22]    # полином R3
            rz = rz[1:] + [new_bit]

    # --- 4. Генерация 114 бит гаммы ---
    key_stream = []
    for _ in range(114):
        majority = 1 if (rx[8] + ry[10] + rz[10]) > 1 else 0

        # Выходной бит = XOR старших битов трёх регистров
        key_stream.append(rx[18] ^ ry[21] ^ rz[22])

        # Тактирование по тем же правилам, что и в холостом ходе
        if rx[8] == majority:
            new_bit = rx[13] ^ rx[16] ^ rx[17] ^ rx[18]
            rx = rx[1:] + [new_bit]

        if ry[10] == majority:
            new_bit = ry[20] ^ ry[21]
            ry = ry[1:] + [new_bit]

        if rz[10] == majority:
            new_bit = rz[7] ^ rz[20] ^ rz[21] ^ rz[22]
            rz = rz[1:] + [new_bit]

    return key_stream


def a5_1_cipher(text: str, key: str, encrypt: bool, start_frame: int = 0, show_frames: bool = False) -> str:
    """
    Основная процедура шифрования / расшифрования поточным шифром A5/1.
    При encrypt=True текст предварительно переводится в биты (digitization).
    При encrypt=False входная строка уже считается битовой последовательностью.
    Возвращает либо битовую строку (при шифровании), либо восстановленный текст (при расшифровании).
    """
    frame_num = start_frame
    result_bits = ""

    if encrypt:
        data_bits = digitization(text)       # текст -> биты
        action = "Шифрование"
    else:
        data_bits = text                     # на входе уже биты
        action = "Расшифрование"

    total_frames = (len(data_bits) + 113) // 114   # количество кадров (114 бит на кадр)
    processed = 0

    if show_frames:
        print(f"\n{action} ({total_frames} кадров):")

    # Обработка данных кадрами по 114 бит
    while len(data_bits) > 0:
        gamma = generate_gamma(key, frame_num)       # получаем 114 бит гаммы
        block_len = min(114, len(data_bits))         # сколько бит осталось
        block = data_bits[:block_len]

        if show_frames:
            print(f"  Кадр {frame_num}: обрабатывается {block_len} бит")
            gamma_str = ''.join(str(b) for b in gamma[:block_len])
            print(f"    Гамма: {gamma_str}")

        # Побитовый XOR текущего блока с гаммой
        for j in range(block_len):
            result_bits += str(int(block[j]) ^ gamma[j])

        data_bits = data_bits[block_len:]    # удаляем обработанную часть
        frame_num += 1
        processed += 1

    if encrypt:
        return result_bits                   # зашифрованная битовая строка
    else:
        recovered = undigitization(result_bits)   # биты -> буквы
        return restore_text(recovered)            # обратная замена знаков


if __name__ == "__main__":
    print("ПОТОЧНЫЙ ШИФР A5/1")

    while True:
        print("\n" + "─" * 40)
        print("Выберите действие:")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("0 - Выход")
        print("─" * 40)

        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            print("  [!] Введите число.")
            continue

        if choice == 0:
            print("До свидания!")
            sys.exit()
        elif choice not in (1, 2):
            print("  [!] Неверный выбор.")
            continue

        raw_text = input("Введите текст: ")
        key = get_key()
        start_frame = get_frame_number(0)
        show_frames = input("Показывать информацию о кадрах и гамму? (д/н): ").strip().lower() in ['д', 'да', 'y', 'yes']

        if choice == 1:          # Шифрование
            prepared = prepare_text(raw_text)
            cipher_bits = a5_1_cipher(prepared, key, encrypt=True,
                                      start_frame=start_frame, show_frames=show_frames)
            grouped = ' '.join(cipher_bits[i:i+5] for i in range(0, len(cipher_bits), 5))
            print("\nЗашифрованный текст (биты):")
            print(grouped)
        else:                    # Расшифрование
            bits = raw_text.replace(' ', '')
            decrypted = a5_1_cipher(bits, key, encrypt=False,
                                    start_frame=start_frame, show_frames=show_frames)
            print("\nРасшифрованный текст:")
            print(decrypted)