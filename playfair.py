import numpy as np

last_char_added = False   # глобальный флаг: был ли добавлен 'ы' в конец текста при выравнивании
ALPHABET_SIZE = 30         # размер алфавита для таблицы Плейфера (без й, ё, ь)

# ============== ФУНКЦИИ ШИФРА ПЛЕЙФЕРА ==============
def convert_punctuation(text, to_word=True):
    """
    Замена знаков препинания на кодовые слова и обратно.
    Если to_word=True: знаки -> слова (для шифрования).
    Если to_word=False: слова -> знаки (для расшифрования).
    """
    punct_dict = {
        '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
        ';': 'двтч', ':': 'чтзпт', '-': 'тире',
        '(': 'скоб', ')': 'скобз', '"': 'квч', "'": 'апстр'
    }

    result = text
    if to_word:
        # Заменяем каждый знак препинания на соответствующее слово
        for punct, word in punct_dict.items():
            result = result.replace(punct, word)
    else:
        # Обратная замена: слово -> знак
        for punct, word in punct_dict.items():
            result = result.replace(word, punct)
    return result


def preprocess_text(text):
    """
    Приведение текста к стандартному виду для шифра Плейфера:
    нижний регистр, замена й->и, ё->е, ь->ъ.
    """
    text = text.lower()
    text = text.replace('й', 'и').replace('ё', 'е').replace('ь', 'ъ')
    return text


def is_key_valid(key):
    """
    Проверка ключа: все символы уникальны после предобработки.
    Повторяющиеся буквы ухудшают качество таблицы.
    """
    processed_key = preprocess_text(key)
    return len(set(processed_key)) == len(processed_key)


def create_playfair_table(key):
    """
    Формирует таблицу 5x6 (5 строк, 6 столбцов) для шифра Плейфера.
    Алфавит: русские буквы, кроме й, ё, ь (они заменяются на и, е, ъ).
    Ключ добавляется в начало таблицы без повторений.
    """
    alphabet = "абвгдежзиклмнопрстуфхцчшщъыэюя"   # 30 букв
    key = preprocess_text(key).replace(' ', '').replace('-', '')  # очистка ключа
    new_key = ""
    for c in key:
        if c not in new_key and c in alphabet:   # уникальные буквы ключа в порядке следования
            new_key += c
    # Добавление оставшихся букв алфавита, которых нет в ключе
    table = new_key + ''.join([c for c in alphabet if c not in new_key])
    # Разбиваем строку на матрицу 5x6
    matrix = [list(table[i:i + 6]) for i in range(0, len(table), 6)]
    return matrix


def print_playfair_table(matrix):
    """Вывод таблицы Плейфера на экран в удобном виде."""
    print("\n--- Ключевая таблица Плейфера (6x5) ---")
    print("     " + "   ".join([str(i) for i in range(6)]))
    for i, row in enumerate(matrix):
        print(f"  {i}  " + "   ".join(row))
    print("----------------------------------------\n")


def prepare_text_for_encryption(text):
    """
    Подготовка текста к шифрованию:
    - Приведение к стандартному виду (preprocess_text).
    - Удаление пробелов и дефисов (но пробелы уже заменены на 'прбл').
    - Вставка 'ы' между одинаковыми буквами в биграмме.
    - Дополнение 'ы' в конец, если длина нечётная.
    Устанавливает глобальный флаг last_char_added.
    """
    global last_char_added
    text = preprocess_text(text).replace(' ', '').replace('-', '')
    prepared_text = ""
    i = 0
    while i < len(text):
        prepared_text += text[i]
        if i + 1 < len(text) and text[i] == text[i + 1]:
            # Одинаковые буквы в паре – вставляем 'ы' между ними
            prepared_text += 'ы'
        i += 1
    if len(prepared_text) % 2 != 0:
        prepared_text += 'ы'          # дополнение до чётного числа символов
        last_char_added = True
    else:
        last_char_added = False
    return prepared_text


def find_position(matrix, char):
    """Поиск строки и столбца символа в матрице."""
    for row_idx, row in enumerate(matrix):
        if char in row:
            return row_idx, row.index(char)
    raise ValueError(f"Символ '{char}' отсутствует в таблице Плейфера.")


def encrypt_pair(matrix, a, b):
    """
    Шифрование пары символов по правилам Плейфера.
    Возвращает строку из двух зашифрованных букв.
    """
    a_row, a_col = find_position(matrix, a)
    b_row, b_col = find_position(matrix, b)
    if a_row == b_row:
        # Одна строка – берём символы справа (циклически)
        return matrix[a_row][(a_col + 1) % 6] + matrix[b_row][(b_col + 1) % 6]
    elif a_col == b_col:
        # Один столбец – берём символы снизу (циклически, 5 строк)
        return matrix[(a_row + 1) % 5][a_col] + matrix[(b_row + 1) % 5][b_col]
    else:
        # Прямоугольник – берём по диагонали
        return matrix[a_row][b_col] + matrix[b_row][a_col]


def decrypt_pair(matrix, a, b):
    """
    Расшифрование пары символов (обратные действия).
    Возвращает строку из двух восстановленных букв.
    """
    a_row, a_col = find_position(matrix, a)
    b_row, b_col = find_position(matrix, b)
    if a_row == b_row:
        # Одна строка – берём символы слева (циклически)
        return matrix[a_row][(a_col - 1) % 6] + matrix[b_row][(b_col - 1) % 6]
    elif a_col == b_col:
        # Один столбец – берём символы сверху (циклически)
        return matrix[(a_row - 1) % 5][a_col] + matrix[(b_row - 1) % 5][b_col]
    else:
        # Прямоугольник – диагональ остаётся той же
        return matrix[a_row][b_col] + matrix[b_row][a_col]


def playfair_encrypt(text, key, handle_punct=True):
    """
    Полное шифрование текста шифром Плейфера.
    handle_punct – нужно ли предварительно заменять знаки препинания.
    """
    original_text = text

    if handle_punct:
        text = convert_punctuation(text, to_word=True)   # заменяем знаки на слова

    # Замена пробела на специальный код, чтобы сохранить пробелы
    text = text.replace(' ', 'прбл')

    matrix = create_playfair_table(key)   # построение таблицы

    print_playfair_table(matrix)          # вывод таблицы (опционально)

    text = prepare_text_for_encryption(text)   # подготовка: вставка 'ы', дополнение

    encrypted_text = ""
    for i in range(0, len(text), 2):          # обработка биграммами
        encrypted_text += encrypt_pair(matrix, text[i], text[i + 1])
    return encrypted_text


def playfair_decrypt(text, key, handle_punct=True):
    """
    Полное расшифрование текста шифром Плейфера.
    handle_punct – нужно ли восстанавливать знаки препинания.
    """
    global last_char_added
    matrix = create_playfair_table(key)

    print_playfair_table(matrix)

    if len(text) % 2 != 0:
        raise ValueError("Ошибка: текст для расшифровки содержит нечетное количество символов.")

    decrypted_text = ""
    for i in range(0, len(text), 2):
        decrypted_text += decrypt_pair(matrix, text[i], text[i + 1])

    # Удаление вставленных 'ы' для разделения одинаковых букв
    final_text = ""
    for i in range(len(decrypted_text)):
        if decrypted_text[i] == 'ы':
            # Проверяем, стоит ли 'ы' между двумя одинаковыми буквами
            if i > 0 and i < len(decrypted_text) - 1 and decrypted_text[i - 1] == decrypted_text[i + 1]:
                continue   # пропускаем этот 'ы', он был вставлен искусственно
        final_text += decrypted_text[i]

    # Если при шифровании был добавлен одиночный 'ы' в конец – удаляем его
    if last_char_added:
        final_text = final_text[:-1]

    # Сначала восстанавливаем пробелы, потом знаки препинания
    final_text = final_text.replace('прбл', ' ')

    if handle_punct:
        final_text = convert_punctuation(final_text, to_word=False)   # обратная замена слов на знаки

    return final_text


def playfair_menu():
    """Меню для шифра Плейфера (дублирует main_menu, не используется в текущем main)."""
    pass


def main_menu():
    """Главное меню программы."""
    while True:
        print("\n" + "=" * 50)
        print("ШИФР ПЛЕЙФЕРА")
        print("=" * 50)
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")

        choice = input("Ваш выбор (1-3): ")

        if choice == '1':
            text = input("Введите текст для шифрования: ")
            key = input("Введите ключ: ")

            if not is_key_valid(key):
                print("Предупреждение: ключ содержит повторяющиеся символы!")

            handle_punct = input("Обрабатывать знаки препинания? (да/нет): ").lower() == 'да'

            try:
                encrypted = playfair_encrypt(text, key, handle_punct)
                print(f"\nЗашифрованный текст: {encrypted}")
            except Exception as e:
                print(f"Ошибка при шифровании: {e}")

        elif choice == '2':
            text = input("Введите текст для расшифровки: ")
            key = input("Введите ключ: ")

            handle_punct = input("Обрабатывать знаки препинания? (да/нет): ").lower() == 'да'

            try:
                decrypted = playfair_decrypt(text, key, handle_punct)
                print(f"\nРасшифрованный текст: {decrypted}")
            except Exception as e:
                print(f"Ошибка при расшифровке: {e}")

        elif choice == '3':
            print("Выход из программы. До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")


if __name__ == "__main__":
    main_menu()