def belazo_cipher(text, key, encrypt=True):
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

    #словарь для замены знаков препинания в исходном тексте на буквы
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
    #обратный словарь для замены букв на знаки препинания
    rev_punct_dict = {v: k for k, v in punct_dict.items()}

    #замена пробела
    space_repl = 'прбл'

    #приводим ключ к нижнему регистру и заменяем ё на е
    key = key.lower().replace('ё', 'е')
    #проверка на пустой ключ
    if len(key) == 0:
        return "Ошибка: ключ не может быть пустым"
    #проверка, что все символы ключа - русские буквы
    for ch in key:
        if ch not in alphabet:
            return "Ошибка: ключ должен состоять только из русских букв"
    #проверка, что ключ не состоит из одинаковых букв
    if all(ch == key[0] for ch in key):
        return "Ошибка: ключ не может состоять из одинаковых букв"

    if encrypt:
        # ---------- Шифрование ----------
        # Приведение текста к нижнему регистру
        text = text.lower()
        # Замена букв ё на буквы е
        text = text.replace('ё', 'е')

        # Замена знаков препинания по словарю
        for punct, repl in punct_dict.items():
            text = text.replace(punct, repl)

        # Замена пробелов
        text = text.replace(' ', space_repl)

        key_len = len(key)

        # Основной цикл шифрования Белазо
        result = []
        for i, ch in enumerate(text):
            if ch in alphabet:
                # Определяем числовой код текущей буквы текста (0..31)
                idx = alphabet.index(ch)
                # Берём соответствующую букву ключа (циклически)
                key_char = key[i % key_len]
                # Определяем сдвиг, равный номеру буквы ключа
                shift = alphabet.index(key_char)
                # Вычисляем новый индекс сдвигом вперёд по модулю длины алфавита
                new_idx = (idx + shift) % 32
                # Добавляем зашифрованную букву
                result.append(alphabet[new_idx])
            else:
                return "Недопустимый формат текста (буквы не из русского алфавита или цифры)"
        # Возвращаем зашифрованную строку без пробелов
        return ''.join(result)

    else:
        # ---------- Расшифрование ----------
        key_len = len(key)

        temp = []
        for i, ch in enumerate(text):
            if ch in alphabet:
                # Числовой код зашифрованной буквы
                idx = alphabet.index(ch)
                # Буква ключа для текущей позиции
                key_char = key[i % key_len]
                # Сдвиг, использованный при шифровании
                shift = alphabet.index(key_char)
                # Обратный сдвиг (вычитание) для восстановления исходной буквы
                orig_idx = (idx - shift) % 32
                temp.append(alphabet[orig_idx])
            else:
                return "Недопустимый формат текста (буквы не из русского алфавита или цифры)"
        # Собираем расшифрованную последовательность букв
        decrypted = ''.join(temp)

        # Обратная замена пробелов
        decrypted = decrypted.replace(space_repl, ' ')

        # Обратная замена знаков препинания
        for word, punct in rev_punct_dict.items():
            decrypted = decrypted.replace(word, punct)

        return decrypted


if __name__ == "__main__":
    test_text = "волк каждый год линяет, а все сер бывает."
    test_key = "зонд"

    print("Исходный текст:")
    print(test_text)
    print("Ключ:", test_key)

    encrypted_test = belazo_cipher(test_text, test_key, encrypt=True)
    print("\nЗашифрованный текст (без пробелов, знаки заменены):")
    print(encrypted_test)

    print("\n" + "=" * 50)
    while True:
        print("\nВыберите действие:")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("0 - Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '0':
            break
        elif choice == '1':
            user_text = input("Введите текст для шифрования: ")
            user_key = input("Введите ключ (русское слово): ")
            encrypted = belazo_cipher(user_text, user_key, encrypt=True)
            print("Зашифрованный текст:")
            print(encrypted)
        elif choice == '2':
            user_text = input("Введите текст для расшифрования: ")
            user_key = input("Введите ключ (русское слово): ")
            decrypted = belazo_cipher(user_text, user_key, encrypt=False)
            print("Расшифрованный текст:")
            print(decrypted)
        else:
            print("Неверный ввод, попробуйте снова.")