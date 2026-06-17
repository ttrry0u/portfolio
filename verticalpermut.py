def print_table(table, title="Таблица"):
    """Вывод таблицы на экран для отладки и наглядности."""
    print(f"\n{title}:")
    if not table:
        print("пустая")
        return
    cols = len(table[0])
    header = "   " + " ".join(f"{i+1:2}" for i in range(cols))
    print(header)
    for r, row in enumerate(table):
        row_str = f"{r+1:2} " + " ".join(ch if ch is not None else ' .' for ch in row)
        print(row_str)
    print()


def vertical_permutation_cipher(text, key, encrypt=True):
    """
    Шифр вертикальной перестановки с маршрутной записью «змейкой».
    Поддерживает шифрование и расшифрование.
    """
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    punct_dict = {
        '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
        '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
        "'": 'апстр'
    }
    rev_punct = {v: k for k, v in punct_dict.items()}
    space_repl = 'прбл'

    def prepare(txt):
        """Подготовка текста к шифрованию: замена ё, знаков и пробелов."""
        txt = txt.lower()
        txt = txt.replace('ё', 'е')
        for p, r in punct_dict.items():
            txt = txt.replace(p, r)
        txt = txt.replace(' ', space_repl)
        return txt

    def restore(txt):
        """Восстановление пробелов и знаков препинания после расшифрования."""
        txt = txt.replace(space_repl, ' ')
        for w, p in rev_punct.items():
            txt = txt.replace(w, p)
        return txt

    def get_permutation(key_word):
        """
        Формирование числовой перестановки для столбцов на основе ключа.
        Буквы ключа сортируются по алфавиту; каждому исходному индексу
        присваивается номер, начиная с 1, в порядке сортировки.
        """
        key_word = key_word.lower().replace('ё', 'е')
        pairs = [(ch, i) for i, ch in enumerate(key_word)]
        pairs.sort(key=lambda x: x[0])          # сортировка по букве
        rank = [0] * len(key_word)
        for new_index, (_, original_index) in enumerate(pairs):
            rank[original_index] = new_index + 1   # нумерация с 1
        return rank

    # Проверка ключа
    if not key:
        raise ValueError("Ключ не может быть пустым")
    rank = get_permutation(key)
    m = len(rank)                               # количество столбцов
    inv_perm = [0] * m                           # обратная перестановка
    for i in range(m):
        inv_perm[rank[i] - 1] = i

    if encrypt:
        # ------------------- ШИФРОВАНИЕ -------------------
        prepared = prepare(text)
        L = len(prepared)
        if L == 0:
            return ""
        r = (L + m - 1) // m                      # количество строк (округление вверх)
        rem = L % m
        if rem == 0:
            rem = m
        # Определение длинных столбцов (в которых на один символ больше)
        if (r - 1) % 2 == 0:
            long_cols = set(range(rem))
        else:
            long_cols = set(range(m - rem, m))

        # Заполнение таблицы построчно змейкой
        table = [[None] * m for _ in range(r)]
        idx = 0
        for row in range(r):
            if row % 2 == 0:          # чётная строка — слева направо
                col_range = range(m)
            else:                     # нечётная строка — справа налево
                col_range = range(m-1, -1, -1)
            for col in col_range:
                if idx < L:
                    table[row][col] = prepared[idx]
                    idx += 1
                else:
                    break
        print_table(table, "Исходная таблица (до перестановки)")

        # Перестановка столбцов согласно ключу
        new_table = [[None] * m for _ in range(r)]
        for j in range(m):                      # j – новая позиция столбца
            orig_col = inv_perm[j]              # откуда взять столбец в исходной таблице
            for row in range(r):
                new_table[row][j] = table[row][orig_col]

        # Считывание шифртекста по столбцам новой таблицы
        cipher = []
        for j in range(m):
            for row in range(r):
                if new_table[row][j] is not None:
                    cipher.append(new_table[row][j])
        return ''.join(cipher)

    else:
        # ------------------- РАСШИФРОВАНИЕ -------------------
        cipher = text
        L = len(cipher)
        if L == 0:
            return ""
        r = (L + m - 1) // m
        rem = L % m
        if rem == 0:
            rem = m
        if (r - 1) % 2 == 0:
            long_cols = set(range(rem))
        else:
            long_cols = set(range(m - rem, m))

        # Длины столбцов исходной (до перестановки) таблицы
        col_lengths_orig = [0] * m
        for i in range(m):
            if i in long_cols:
                col_lengths_orig[i] = r
            else:
                col_lengths_orig[i] = r - 1

        # Длины столбцов в новой таблице (после перестановки)
        col_lengths_new = [0] * m
        for i in range(m):
            col_lengths_new[rank[i] - 1] = col_lengths_orig[i]

        # Разрезание шифртекста на столбцы новой таблицы
        parts = []
        pos = 0
        for k in range(m):
            l = col_lengths_new[k]
            parts.append(cipher[pos:pos+l])
            pos += l

        # Заполнение новой таблицы по столбцам
        new_table = [[None] * m for _ in range(r)]
        for new_idx in range(m):
            data = parts[new_idx]
            for row, ch in enumerate(data):
                new_table[row][new_idx] = ch

        # Восстановление исходной таблицы обратной перестановкой столбцов
        table = [[None] * m for _ in range(r)]
        for j in range(m):
            orig_col = inv_perm[j]
            for row in range(r):
                table[row][orig_col] = new_table[row][j]

        # Считывание открытого текста из восстановленной таблицы змейкой
        result = []
        for row in range(r):
            if row % 2 == 0:
                col_range = range(m)
            else:
                col_range = range(m-1, -1, -1)
            for col in col_range:
                if table[row][col] is not None:
                    result.append(table[row][col])
        restored = ''.join(result)
        return restore(restored)


def input_key():
    """Безопасный ввод ключа с проверкой."""
    print("Введите ключевое слово (русские буквы, можно с повторами):")
    while True:
        key = input("Ключ: ").strip()
        if len(key) < 2:
            print("Ключ должен содержать минимум 2 буквы.")
            continue
        if not key:
            print("Ключ не может быть пустым.")
            continue
        key_low = key.lower().replace('ё', 'е')
        allowed = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        if all(ch in allowed for ch in key_low):
            return key_low
        else:
            print("Ключ должен содержать только русские буквы.")


if __name__ == "__main__":
    print("=" * 60)
    print("ШИФР ВЕРТИКАЛЬНОЙ ПЕРЕСТАНОВКИ (маршрутная запись зигзагом)")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прбл'")
    print("=" * 60)

    test_key = "октябрь"
    test_text = "волк каждый год линяет, а все сер бывает."
    print("\n--- Демонстрация ---")
    print("Исходный текст:", test_text)
    print("Ключ:", test_key)

    enc = vertical_permutation_cipher(test_text, test_key, encrypt=True)
    print("Зашифрованный текст:", enc)
    dec = vertical_permutation_cipher(enc, test_key, encrypt=False)
    print("Расшифрованный текст:", dec)

    print("\n" + "=" * 60)
    while True:
        print("\nВыберите действие:")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("0 - Выход")
        choice = input("Ваш выбор: ").strip()
        if choice == '0':
            break
        elif choice in ('1', '2'):
            key = input_key()
            user_text = input("Введите текст: ").strip()
            try:
                if choice == '1':
                    result = vertical_permutation_cipher(user_text, key, encrypt=True)
                    print("Зашифрованный текст:")
                    print(result)
                else:
                    result = vertical_permutation_cipher(user_text, key, encrypt=False)
                    print("Расшифрованный текст:")
                    print(result)
            except Exception as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод, попробуйте снова.")