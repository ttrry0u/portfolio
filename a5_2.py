import sys

# ---------- Алфавит ----------
# Используется 32 русские буквы (без буквы «ё»). Каждая буква кодируется 5 битами.
list_alph = ["а","б","в","г","д","е","ж","з","и","й","к","л","м","н","о","п","р","с","т","у","ф",
             "х","ц","ч","ш","щ","ъ","ы","ь","э","ю","я"]


class A52Cipher:
    """
    Генератор гаммы поточного шифра A5/2.
    Содержит четыре линейных регистра сдвига с обратной связью (LFSR):
      R1 – 19 бит, полином: x^19 + x^18 + x^17 + x^14 + 1
      R2 – 22 бита, полином: x^22 + x^21 + 1
      R3 – 23 бита, полином: x^23 + x^22 + x^21 + x^8 + 1
      R4 – 17 бит, полином: x^17 + x^12 + 1  (управляющий регистр)
    Биты в списках хранятся от младшего (индекс 0) к старшему (индекс len-1).
    """

    def __init__(self):
        """Инициализация всех регистров нулями."""
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.R4 = [0] * 17

    def majority(self, x, y, z):
        """
        Мажоритарная функция: возвращает 1, если хотя бы два из трёх аргументов равны 1,
        иначе 0. Реализуется как (x & y) | (x & z) | (y & z).
        """
        return (x & y) | (x & z) | (y & z)

    # ---------- Принудительная тактировка всех регистров ----------
    def clock_all(self, input_bit):
        """
        Одновременный сдвиг всех четырёх регистров с подмешиванием входного бита.
        Используется на этапах загрузки ключа и номера кадра.
        Новый бит для каждого регистра вычисляется как XOR битов обратной связи
        (в соответствии с полиномом) и входного бита input_bit.
        """
        # Обратная связь R1 (полином: биты 13,16,17,18)
        nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18] ^ input_bit
        # Обратная связь R2 (полином: биты 20,21)
        nb2 = self.R2[20] ^ self.R2[21] ^ input_bit
        # Обратная связь R3 (полином: биты 7,20,21,22)
        nb3 = self.R3[7]  ^ self.R3[20] ^ self.R3[21] ^ self.R3[22] ^ input_bit
        # Обратная связь R4 (полином: биты 11,16)
        nb4 = self.R4[11] ^ self.R4[16] ^ input_bit

        # Сдвиг регистров: новый бит становится младшим (индекс 0), остальные сдвигаются вправо
        self.R1 = [nb1] + self.R1[:-1]
        self.R2 = [nb2] + self.R2[:-1]
        self.R3 = [nb3] + self.R3[:-1]
        self.R4 = [nb4] + self.R4[:-1]

    # ---------- Управляемая тактировка (stop/go) ----------
    def clock_stop_go(self, generate_output=False):
        """
        Один такт работы генератора в режиме stop/go.
        Тактирование R1, R2, R3 зависит от управляющего регистра R4.
        R4 сдвигается всегда.
        Если generate_output == True, возвращает очередной бит гаммы,
        иначе возвращает None.
        """
        # Мажоритарная функция от битов R4[3], R4[7], R4[10]
        f = self.majority(self.R4[3], self.R4[7], self.R4[10])

        # Условия сдвига: регистр сдвигается, если его управляющий бит совпадает с f
        shift_r1 = (self.R4[10] == f)
        shift_r2 = (self.R4[3]  == f)
        shift_r3 = (self.R4[7]  == f)

        # R4 сдвигается всегда
        nb4 = self.R4[11] ^ self.R4[16]
        self.R4 = [nb4] + self.R4[:-1]

        # Сдвиг R1, R2, R3 при выполнении условия
        if shift_r1:
            nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18]
            self.R1 = [nb1] + self.R1[:-1]
        if shift_r2:
            nb2 = self.R2[20] ^ self.R2[21]
            self.R2 = [nb2] + self.R2[:-1]
        if shift_r3:
            nb3 = self.R3[7] ^ self.R3[20] ^ self.R3[21] ^ self.R3[22]
            self.R3 = [nb3] + self.R3[:-1]

        # Генерация выходного бита (если требуется)
        if generate_output:
            out = self.R1[18] ^ self.R2[21] ^ self.R3[22]               # основной XOR
            # Дополнительные мажоритарные функции для усложнения выхода
            maj1 = self.majority(self.R1[12], self.R1[14], self.R1[15])
            maj2 = self.majority(self.R2[9],  self.R2[13], self.R2[16])
            maj3 = self.majority(self.R3[13], self.R3[16], self.R3[18])
            return out ^ maj1 ^ maj2 ^ maj3
        return None

    # ---------- Инициализация ключом и номером кадра ----------
    def initialize(self, key_bits, frame_bits):
        """
        Начальная установка регистров перед генерацией гаммы для очередного кадра.
        Этапы:
          1) обнуление регистров;
          2) 64 такта загрузки ключа (clock_all);
          3) 22 такта загрузки номера кадра (clock_all);
          4) принудительная установка R4[3]=R4[7]=R4[10]=1;
          5) 64 такта перемешивания без выдачи гаммы (clock_stop_go с generate_output=False).
        """
        # Обнуление
        self.R1 = [0]*19
        self.R2 = [0]*22
        self.R3 = [0]*23
        self.R4 = [0]*17

        # Загрузка ключа (64 бита)
        for b in key_bits:
            self.clock_all(b)

        # Загрузка номера кадра (22 бита)
        for b in frame_bits:
            self.clock_all(b)

        # Установка управляющих битов R4
        self.R4[3] = 1
        self.R4[7] = 1
        self.R4[10] = 1

        # Холостой ход 64 такта для перемешивания
        for _ in range(64):
            self.clock_stop_go(generate_output=False)

    # ---------- Генерация гаммы ----------
    def generate_keystream(self, length):
        """
        Генерация гаммы заданной длины (количество бит).
        Каждый бит получается вызовом clock_stop_go с generate_output=True.
        Возвращает список целых чисел (0/1).
        """
        ks = []
        for _ in range(length):
            ks.append(self.clock_stop_go(generate_output=True))
        return ks


# ===================== Вспомогательные функции =====================

def digitization(text):
    """
    Преобразование текста в битовый поток.
    Каждая буква алфавита заменяется своим индексом (0..31) и представляется 5 битами.
    Возвращает список целых чисел (0/1).
    """
    bits = []
    for ch in text:
        idx = list_alph.index(ch)               # индекс буквы в алфавите
        bits += [int(b) for b in format(idx, '05b')]   # 5-битное представление
    return bits


def undigitization(bits):
    """
    Обратное преобразование битового потока в текст.
    Дополняет длину битов до кратности 5 нулями (если нужно),
    затем разбивает на группы по 5 бит, переводит в число и получает букву алфавита.
    """
    while len(bits) % 5 != 0:
        bits.append(0)                          # выравнивание
    text = ""
    for i in range(0, len(bits), 5):
        idx = int(''.join(str(b) for b in bits[i:i+5]), 2)
        if idx < len(list_alph):               # проверка на корректность индекса
            text += list_alph[idx]
    return text


def xor_bits(a, b):
    """Побитовый XOR двух списков одинаковой длины. Возвращает список результатов."""
    return [x ^ y for x, y in zip(a, b)]


def bits_str(bits):
    """Преобразование списка битов в строку без пробелов (например, '01001')."""
    return ''.join(str(b) for b in bits)


def bits_group5(bits):
    """
    Форматирование битовой строки: группировка по 5 бит через пробел.
    Удобно для визуального отображения.
    """
    s = bits_str(bits)
    return ' '.join(s[i:i+5] for i in range(0, len(s), 5))


# ===================== Ввод ключа и номера кадра =====================

def get_key():
    """
    Ввод ключа пользователем.
    Поддерживается два формата:
      1) строка ровно из 64 символов '0' и '1';
      2) слово из 8 русских букв – каждая буква превращается в 8-битный код
         (используется её индекс в алфавите), биты всех букв объединяются,
         и первые 64 бита берутся в качестве ключа.
    Возвращает список из 64 целых чисел (0/1).
    """
    print("\nТип ключа:")
    print("  1. Строка из 64 бит (0 и 1)")
    print("  2. 8 русских букв")
    choice = input("Выбор: ").strip()

    if choice == "1":
        key = input("Введите 64 бита: ").strip()
        if len(key) != 64 or not all(c in '01' for c in key):
            print("Нужно ровно 64 символа (0 или 1)!")
            sys.exit(1)
        return [int(b) for b in key]

    elif choice == "2":
        word = input("Введите 8 русских букв: ").strip().lower()
        for ch in word:
            if ch not in list_alph:
                print(f"Символ '{ch}' не в алфавите (без Ё)!")
                sys.exit(1)
        if len(word) < 8:
            print("Нужно минимум 8 букв!")
            sys.exit(1)
        word = word[:8]
        key_bits = []
        for ch in word:
            # Индекс буквы кодируется 8 битами (0..31 помещается)
            key_bits += [int(b) for b in format(list_alph.index(ch), '08b')]
        print(f"Ключ в битах: {bits_str(key_bits)}")
        return key_bits
    else:
        print("Неверный выбор!")
        sys.exit(1)


def get_frame():
    """
    Ввод номера кадра.
    Можно ввести либо целое число от 0 до 4194303 (22 бита),
    либо строку из 22 символов '0' и '1'.
    Возвращает список из 22 целых чисел (0/1).
    """
    print("\nТип номера кадра:")
    print("  1. Число (0–4194303)")
    print("  2. Строка из 22 бит")
    choice = input("Выбор: ").strip()

    if choice == "1":
        try:
            n = int(input("Номер кадра: ").strip()) & 0x3FFFFF   # ограничение 22 битами
        except:
            n = 0
        bits = [(n >> i) & 1 for i in range(22)]                # младший бит первым
        print(f"Кадр в битах: {bits_str(bits)}")
        return bits
    elif choice == "2":
        s = input("Введите 22 бита кадра: ").strip()
        if len(s) != 22 or not all(c in '01' for c in s):
            print("Нужно ровно 22 бита!")
            sys.exit(1)
        return [int(b) for b in s]
    else:
        print("Неверный выбор!")
        sys.exit(1)


# ===================== Шифрование =====================

def encrypt_mode():
    """Режим шифрования текста."""
    print("\n" + "="*65)
    print("              ШИФРОВАНИЕ A5/2")
    print("="*65)

    # Ввод и подготовка текста
    text = input("Текст (русские буквы): ").strip().lower()
    text = text.replace('.','тчк').replace(',','зпт').replace(' ','прб')
    for ch in text:
        if ch not in list_alph:
            print(f"Символ '{ch}' не поддерживается!")
            return

    key_bits   = get_key()
    frame_bits = get_frame()

    # Преобразование текста в биты
    plain_bits = digitization(text)
    n_letters  = len(text)
    n_bits     = len(plain_bits)

    print(f"\n{'─'*65}")
    print(f"Открытый текст : '{text}'  ({n_letters} букв = {n_bits} бит)")
    print()

    # Вывод таблицы кодирования букв
    print(f"  {'Буква':<8} {'Индекс':<8} {'5 бит'}")
    print(f"  {'─'*30}")
    for ch in text:
        idx = list_alph.index(ch)
        print(f"  {ch:<8} {idx:<8} {format(idx,'05b')}")

    print(f"\nБиты открытого текста: {bits_group5(plain_bits)}")

    bits_left       = plain_bits[:]          # копия списка битов для обработки
    ciphertext_bits = []                     # зашифрованные биты
    keystream_all   = []                     # вся гамма (для вывода)

    # Цикл обработки кадрами (до 114 бит за итерацию)
    while bits_left:
        c = A52Cipher()
        c.initialize(key_bits, frame_bits)                     # инициализация генератора
        ks = c.generate_keystream(min(114, len(bits_left)))    # генерация гаммы
        chunk = bits_left[:114]                                # текущий блок данных
        enc   = xor_bits(chunk, ks)                            # XOR с гаммой
        ciphertext_bits += enc
        keystream_all   += ks[:len(chunk)]
        bits_left = bits_left[114:]                            # удаление обработанных битов

    # Вывод подробной таблицы шифрования
    print(f"\n{'─'*65}")
    print("ТАБЛИЦА ШИФРОВАНИЯ (5 бит = 1 буква):")
    print(f"\n  {'№':<5} {'Буква':<7} {'Открытый':<10} {'Гамма':<10} {'Шифр':<10}")
    print(f"  {'─'*45}")

    for i, ch in enumerate(text):
        start = i * 5
        p_bits = plain_bits[start:start+5]
        k_bits = keystream_all[start:start+5]
        c_bits = ciphertext_bits[start:start+5]

        p_s = bits_str(p_bits)
        k_s = bits_str(k_bits)
        c_s = bits_str(c_bits)

        print(f"  {i+1:<5} '{ch}'     {p_s:<10} {k_s:<10} {c_s:<10}")
        for bit_i in range(5):
            p = p_bits[bit_i]
            k = k_bits[bit_i]
            c = c_bits[bit_i]
            print(f"  {'':5} бит {start+bit_i+1:<3}  {p:<10} {k:<10} {c}")
        print()

    # Итоговый вывод
    print(f"{'─'*65}")
    print(f"Гамма      : {bits_group5(keystream_all)}")
    print(f"Шифртекст  : {bits_group5(ciphertext_bits)}")
    print(f"{'─'*65}")
    print(f"Гамма      (сплошная): {bits_str(keystream_all)}")
    print(f"Шифртекст  (сплошная): {bits_str(ciphertext_bits)}")


# ===================== Расшифрование =====================

def decrypt_mode():
    """Режим расшифрования текста."""
    print("\n" + "="*65)
    print("              РАСШИФРОВАНИЕ A5/2 (исправленная версия)")
    print("="*65)

    key_bits   = get_key()
    frame_bits = get_frame()

    print("Введите шифртекст (биты, строка из 0 и 1, пробелы допустимы)")
    s = input("Шифртекст: ").strip().replace(' ', '')
    cipher_bits = [int(c) for c in s if c in '01']    # отфильтровываем только 0/1

    if not cipher_bits:
        print("Шифртекст пустой!")
        return

    bits_left     = cipher_bits[:]        # копия для обработки
    plain_bits    = []                   # восстановленные биты открытого текста
    keystream_all = []                   # гамма (для отображения)

    # Аналогичный цикл: генерация гаммы, XOR, накопление
    while bits_left:
        c = A52Cipher()
        c.initialize(key_bits, frame_bits)
        ks    = c.generate_keystream(min(114, len(bits_left)))
        chunk = bits_left[:114]
        dec   = xor_bits(chunk, ks)
        plain_bits    += dec
        keystream_all += ks[:len(chunk)]
        bits_left = bits_left[114:]

    n_letters = len(plain_bits) // 5

    # Таблица расшифрования
    print(f"\n{'─'*65}")
    print("ТАБЛИЦА РАСШИФРОВАНИЯ (5 бит = 1 буква):")
    print(f"\n  {'№':<5} {'Шифр':<10} {'Гамма':<10} {'Открытый':<10} {'Буква'}")
    print(f"  {'─'*50}")

    decoded = undigitization(plain_bits[:])

    for i in range(n_letters):
        start  = i * 5
        c_bits = cipher_bits[start:start+5]
        k_bits = keystream_all[start:start+5]
        p_bits = plain_bits[start:start+5]
        ch     = decoded[i] if i < len(decoded) else '?'

        c_s = bits_str(c_bits)
        k_s = bits_str(k_bits)
        p_s = bits_str(p_bits)

        print(f"  {i+1:<5} {c_s:<10} {k_s:<10} {p_s:<10} '{ch}'")
        for bit_i in range(5):
            c = c_bits[bit_i]
            k = k_bits[bit_i]
            p = p_bits[bit_i]
            print(f"  {'':5} бит {start+bit_i+1:<3}  {c:<10} {k:<10} {p}")
        print()

    print(f"{'─'*65}")
    print(f"Гамма      : {bits_group5(keystream_all)}")
    print(f"Шифртекст  : {bits_group5(cipher_bits)}")
    print(f"Открытый   : {bits_group5(plain_bits)}")

    # Финальное форматирование: заглавная первая буква и восстановление знаков
    result = decoded
    if result:
        result = result[0].upper() + result[1:]
    result = result.replace('прб', ' ').replace('тчк', '.').replace('зпт', ',')
    print(f"\n>>> РАСШИФРОВАНО: '{result}' <<<")


# ===================== Главное меню =====================

def main():
    print("="*65)
    print("        АЛГОРИТМ A5/2 (GSM) — ШИФРОВАНИЕ/РАСШИФРОВАНИЕ")
    print("="*65)
    while True:
        print("\n" + "─" * 40)
        print("Выберите действие: ")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("0 - Выход")
        print("─" * 40)
        choice = input("\nВыбор: ").strip()
        if choice == "0":
            print("До свидания!")
            sys.exit(0)
        elif choice == "1":
            encrypt_mode()
        elif choice == "2":
            decrypt_mode()
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()