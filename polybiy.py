def create_polybius_square():
    """
    Создание квадрата Полибия 6×6, заполненного буквами русского алфавита
    (без «ё») построчно. Пустые клетки (их будет 4) заполняются пустой строкой.
    Возвращает двумерный список (матрицу) 6×6.
    """
    # Русский алфавит из 32 букв (без «ё»). Индексы от 0 до 31.
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

    # Создаём пустую матрицу 6×6, заполненную пустыми строками.
    square = [['' for _ in range(6)] for _ in range(6)]

    # Заполняем квадрат буквами по строкам: сначала первая строка слева направо,
    # затем вторая и т.д. Переменная index отслеживает позицию в алфавите.
    index = 0
    for i in range(6):          # i – номер строки (0…5)
        for j in range(6):      # j – номер столбца (0…5)
            if index < len(alphabet):
                square[i][j] = alphabet[index]   # записываем очередную букву
                index += 1
            else:
                # После 32 букв остаются 4 пустые клетки – оставляем их пустыми.
                square[i][j] = ''

    return square


def polybius_cipher(text, decrypt=False):
    """
    Шифрование / расшифрование текста с помощью квадрата Полибия.
    При decrypt=False (по умолчанию) выполняется шифрование: каждая буква заменяется
    парой цифр – номером строки и столбца в квадрате. Знаки препинания и пробелы
    предварительно заменяются на буквенные коды.
    При decrypt=True – обратный процесс: последовательность цифровых пар преобразуется
    обратно в буквы, затем восстанавливаются пробелы и знаки препинания.
    """
    # Алфавит (без «ё») – тот же, что и в create_polybius_square.
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

    # Словарь замены знаков препинания на буквенные коды.
    punct_dict = {
        '.': 'тчк',
        ',': 'зпт',
        '?': 'впр',
        '!': 'вск',
        '"': 'квч',
        '-': 'тире',
        '(': 'скоб',
        ')': 'скобз',
        "'": 'апстр'
    }

    # Обратный словарь для восстановления знаков препинания.
    reverse_punct_dict = {v: k for k, v in punct_dict.items()}

    # Получаем квадрат Полибия (матрицу 6×6).
    square = create_polybius_square()

    # ---------- Шифрование ----------
    if not decrypt:
        # Строим словарь: буква → координаты в виде строки "строкастолбец" (например, "23").
        letter_to_coords = {}
        for i in range(6):                     # строки
            for j in range(6):                 # столбцы
                letter = square[i][j]
                if letter:                     # только для непустых клеток
                    letter_to_coords[letter] = f"{i+1}{j+1}"  # нумерация с 1

        # Подготовка открытого текста:
        # – привести к нижнему регистру,
        # – заменить «ё» на «е»,
        # – заменить все знаки препинания на кодовые слова,
        # – заменить пробелы на 'прбл'.
        text = text.lower()
        text = text.replace('ё', 'е')

        for punct, replacement in punct_dict.items():
            text = text.replace(punct, replacement)

        text = text.replace(' ', 'прбл')

        # Шифрование: для каждого символа текста, если он есть в словаре, заменяем его
        # координатной парой, иначе оставляем без изменений (например, цифры).
        result = []
        for ch in text:                         # ch – текущий символ обработанного текста
            if ch in letter_to_coords:
                result.append(letter_to_coords[ch])
            else:
                result.append(ch)

        # Возвращаем координатные пары, разделённые пробелами.
        return ' '.join(result)

    # ---------- Расшифрование ----------
    else:
        # Строим обратный словарь: "строкастолбец" → буква.
        coords_to_letter = {}
        for i in range(6):
            for j in range(6):
                letter = square[i][j]
                if letter:
                    coords_to_letter[f"{i+1}{j+1}"] = letter

        # Входная строка состоит из координат, разделённых пробелами.
        decrypted_chars = []
        parts = text.split()                    # разбиваем строку на части по пробелам

        for part in parts:
            if part in coords_to_letter:        # если это известная координата
                decrypted_chars.append(coords_to_letter[part])
            else:
                # Если не координата, оставляем как есть (например, нераспознанные символы).
                decrypted_chars.append(part)

        decrypted_text = ''.join(decrypted_chars)

        # Восстанавливаем пробелы (заменяем 'прбл' обратно на пробел).
        decrypted_text = decrypted_text.replace('прбл', ' ')

        # Восстанавливаем знаки препинания (заменяем кодовые слова на символы).
        for word, punct in reverse_punct_dict.items():
            decrypted_text = decrypted_text.replace(word, punct)

        return decrypted_text


def print_polybius_square():
    """Вывод квадрата Полибия на экран в удобочитаемом виде."""
    square = create_polybius_square()
    print("\nКвадрат Полибия 6x6:")
    # Заголовок: номера столбцов (1..6)
    print("  " + " ".join(str(i+1) for i in range(6)))
    for i in range(6):                         # каждая строка
        row_str = f"{i+1}: "
        for j in range(6):
            letter = square[i][j]
            if letter:
                row_str += letter + " "
            else:
                row_str += "· "                # пустая клетка обозначается точкой
        print(row_str)
    print("(· - пустая клетка)")


if __name__ == "__main__":
    print("="*50)
    print("ШИФР КВАДРАТОМ ПОЛИБИЯ")
    print("="*50)

    # Выводим квадрат Полибия для наглядности.
    print_polybius_square()

    # Демонстрация шифрования и расшифрования на тестовой строке.
    test_text = "волк каждый год линяет, а все сер бывает."
    print("\n" + "="*50)
    print("Исходный текст:", test_text)

    encrypted = polybius_cipher(test_text, decrypt=False)
    print("Зашифрованный текст (координаты):", encrypted)

    decrypted = polybius_cipher(encrypted, decrypt=True)
    print("Расшифрованный текст:", decrypted)

    if test_text.lower().replace('ё', 'е') == decrypted:
        print("✓ Шифрование и расшифрование выполнены корректно!")

    print("\n" + "="*50)

    # Интерактивное меню
    while True:
        print("\nВыберите действие:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Показать квадрат Полибия")
        print("4. Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            user_text = input("\nВведите текст для шифрования: ")
            encrypted = polybius_cipher(user_text, decrypt=False)
            print("\n" + "="*50)
            print("Зашифрованный текст (координаты):")
            print(encrypted)
            print("="*50)

        elif choice == '2':
            user_text = input("\nВведите координаты для расшифрования: ")
            decrypted = polybius_cipher(user_text, decrypt=True)
            print("\n" + "="*50)
            print("Расшифрованный текст:")
            print(decrypted)
            print("="*50)

        elif choice == '3':
            print_polybius_square()

        elif choice == '4':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 4.")