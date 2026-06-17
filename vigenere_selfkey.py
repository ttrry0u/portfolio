def prepare_text(text):
    """Подготовка текста к шифрованию: замена ё, знаков препинания и пробела."""
    text = text.lower()
    text = text.replace('ё', 'е')
    punct_dict = {
        '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
        '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
        "'": 'апстр'
    }
    for punct, repl in punct_dict.items():
        text = text.replace(punct, repl)
    text = text.replace(' ', 'прбл')
    return text


def restore_text(text):
    """Обратное преобразование: восстановление пробелов и знаков препинания."""
    text = text.replace('прбл', ' ')
    rev_punct = {
        'тчк': '.', 'зпт': ',', 'впр': '?', 'вск': '!',
        'квч': '"', 'тире': '-', 'скоб': '(', 'скобз': ')',
        'апстр': "'"
    }
    for word, punct in rev_punct.items():
        text = text.replace(word, punct)
    return text


def vigenere_ciphertext_autokey(text, key_letter, encrypt=True):
    """
    Шифрование/расшифрование методом Виженера с ключом-шифртекстом
    (ciphertext autokey).
    Гамма образуется из предыдущих зашифрованных символов.
    """
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    key_letter = key_letter.lower().replace('ё', 'е')
    if key_letter not in alphabet:
        raise ValueError("Ключ должен быть одной русской буквой")
    # Начальный сдвиг, задаваемый секретной буквой
    key_shift = alphabet.index(key_letter)

    if encrypt:
        # ---------- Шифрование ----------
        # Готовим текст: ё→е, знаки препинания и пробелы заменяем на спецкоды
        text = prepare_text(text)

        result = []
        # Начальное значение гаммы — секретная буква, но затем гаммой становится
        # предыдущий зашифрованный символ (шифртекст).
        prev_cipher_shift = key_shift

        for ch in text:
            if ch in alphabet:
                # Позиция текущей буквы открытого текста (0..31)
                idx = alphabet.index(ch)

                # Шифруем сдвигом prev_cipher_shift (предыдущий зашифрованный символ)
                new_idx = (idx + prev_cipher_shift) % 32
                cipher_char = alphabet[new_idx]
                result.append(cipher_char)

                # Обновляем гамму: теперь сдвиг равен только что полученному шифртексту
                prev_cipher_shift = new_idx
            else:
                # Символы не из алфавита переносим без изменений
                result.append(ch)

        return ''.join(result)

    else:
        # ---------- Расшифрование ----------
        result = []
        # Начальное значение гаммы — та же секретная буква
        prev_cipher_shift = key_shift

        for ch in text:
            if ch in alphabet:
                # Позиция текущего зашифрованного символа
                idx = alphabet.index(ch)

                # Восстанавливаем исходную букву обратным сдвигом
                orig_idx = (idx - prev_cipher_shift) % 32
                orig_char = alphabet[orig_idx]
                result.append(orig_char)

                # Обновляем гамму: теперь сдвиг равен текущему зашифрованному символу
                # (а не восстановленному открытому тексту)
                prev_cipher_shift = idx
            else:
                result.append(ch)

        decrypted = ''.join(result)
        # Обратная замена спецкодов на пробелы и знаки препинания
        return restore_text(decrypted)


if __name__ == "__main__":
    print("=" * 60)
    print("ШИФР ВИЖЕНЕРА С КЛЮЧОМ-ШИФРТЕКСТОМ (ciphertext autokey)")
    print("=" * 60)

    test_text = "волк каждый год линяет, а все сер бывает."
    test_key = "н"
    print("Исходный текст:", test_text)
    print("Секретная буква:", test_key)

    enc = vigenere_ciphertext_autokey(test_text, test_key, encrypt=True)
    dec = vigenere_ciphertext_autokey(enc, test_key, encrypt=False)
    print("\nЗашифровано:", enc)
    print("Расшифровано:", dec)

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
            user_text = input("Введите текст: ")
            user_key = input("Введите секретную букву (одну русскую букву): ").strip()
            try:
                if choice == '1':
                    result = vigenere_ciphertext_autokey(user_text, user_key, encrypt=True)
                    print("Зашифрованный текст:")
                else:
                    result = vigenere_ciphertext_autokey(user_text, user_key, encrypt=False)
                    print("Расшифрованный текст:")
                print(result)
            except ValueError as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод, попробуйте снова.")