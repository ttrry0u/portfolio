def tritemius_cipher(text, encrypt=True):
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

    if encrypt:
        #приведение текста к нижнему регистру
        text = text.lower()
        #замена букв ё на буквы е
        text = text.replace('ё', 'е')

        #замена знаков препинания по словарю
        for punct, repl in punct_dict.items():
            text = text.replace(punct, repl)

        #замена пробелов
        text = text.replace(' ', space_repl)

        #шифр Тритемия
        #создание пустого списка для добавления символов шифрованного текста
        result = []
        #цикл for с enumerate, позволяющий пройтись по всем символам текста и выдать им порядковые номера (записываются в pos)
        for pos, ch in enumerate(text):
            #проверка на наличие символа исходного текста в алфавите
            if ch in alphabet:
                #записываем в переменную idx индекс буквы в алфавите (например для "а" индекс будет равен 0)
                idx = alphabet.index(ch)
                #формируем новый индекс буквы по правилу (индекс буквы в алфавите + индекс буквы в тексте). Остаток от деления на 32 находим,
                #чтобы индекс оставался в пределах алфавита
                new_idx = (idx + pos) % 32
                #добавляем в созданный список букву из алфавита, соответствующую вычисленному новому индексу
                result.append(alphabet[new_idx])
            else:
                return "Недопустимый формат текста (буквы не из русского алфавита или цифры)"
        return ''.join(result)

    else:
        #расшифрование
        #формируем пустой список, в который будем записывать расшифрованные буквы
        temp = []
        #дублируем алгоритм зашифрования с той разницей, что вместо суммы индексов
        #будет вычитание индекса буквы в тексте из индекса в алфавите
        for pos, ch in enumerate(text):
            if ch in alphabet:
                idx = alphabet.index(ch)
                #обратный сдвиг: вычитаем позицию
                orig_idx = (idx - pos) % 32
                temp.append(alphabet[orig_idx])
            else:
                return "Недопустимый формат текста (буквы не из русского алфавита или цифры)"
        decrypted = ''.join(temp)

        #обратная замена пробелов
        decrypted = decrypted.replace(space_repl, ' ')

        #обратная замена знаков препинания
        for word, punct in rev_punct_dict.items():
            decrypted = decrypted.replace(word, punct)

        return decrypted

if __name__ == "__main__":
    test_text = "волк каждый год линяет, а все сер бывает."

    print("Исходный текст:")
    print(test_text)

    encrypted_test = tritemius_cipher(test_text, encrypt=True)
    print("\nЗашифрованный текст:")
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
            encrypted = tritemius_cipher(user_text, encrypt=True)
            print("Зашифрованный текст:")
            print(encrypted)
        elif choice == '2':
            user_text = input("Введите текст для расшифрования: ")
            decrypted = tritemius_cipher(user_text, encrypt=False)
            print("Расшифрованный текст:")
            print(decrypted)
        else:
            print("Неверный ввод, попробуйте снова.")