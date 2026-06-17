# Общие функции для подготовки текста и обратного преобразования
def prepare_text(text):
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
    text = text.replace('прбл', ' ')
    rev_punct = {
        'тчк': '.', 'зпт': ',', 'впр': '?', 'вск': '!',
        'квч': '"', 'тире': '-', 'скоб': '(', 'скобз': ')',
        'апстр': "'"
    }
    for word, punct in rev_punct.items():
        text = text.replace(word, punct)
    return text

# Шифр Виженера с самоключом (autokey по открытому тексту)
def vigenere_self_key_cipher(text, key_letter, encrypt=True):
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    key_letter = key_letter.lower().replace('ё', 'е')
    if key_letter not in alphabet:
        raise ValueError("Ключ должен быть одной русской буквой")
    key_shift = alphabet.index(key_letter)

    if encrypt:
        text = prepare_text(text)
        result = []
        prev_shift = key_shift
        for ch in text:
            if ch in alphabet:
                idx = alphabet.index(ch)
                new_idx = (idx + prev_shift) % 32
                result.append(alphabet[new_idx])
                prev_shift = idx
            else:
                # Небуквенные символы (цифры и т.п.) оставляем без изменений
                result.append(ch)
        return ''.join(result)
    else:
        # Расшифрование
        result = []
        prev_shift = key_shift
        for ch in text:
            if ch in alphabet:
                idx = alphabet.index(ch)
                orig_idx = (idx - prev_shift) % 32
                orig_char = alphabet[orig_idx]
                result.append(orig_char)
                prev_shift = orig_idx
            else:
                result.append(ch)
        decrypted = ''.join(result)
        return restore_text(decrypted)

# Шифр Виженера с ключом-шифртекстом (ciphertext autokey)
def vigenere_ciphertext_autokey(text, key_letter, encrypt=True):
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    key_letter = key_letter.lower().replace('ё', 'е')
    if key_letter not in alphabet:
        raise ValueError("Ключ должен быть одной русской буквой")
    key_shift = alphabet.index(key_letter)

    if encrypt:
        text = prepare_text(text)
        result = []
        prev_cipher_shift = key_shift
        for ch in text:
            if ch in alphabet:
                idx = alphabet.index(ch)
                new_idx = (idx + prev_cipher_shift) % 32
                cipher_char = alphabet[new_idx]
                result.append(cipher_char)
                prev_cipher_shift = new_idx
            else:
                result.append(ch)
        return ''.join(result)
    else:
        result = []
        prev_cipher_shift = key_shift
        for ch in text:
            if ch in alphabet:
                idx = alphabet.index(ch)
                orig_idx = (idx - prev_cipher_shift) % 32
                orig_char = alphabet[orig_idx]
                result.append(orig_char)
                prev_cipher_shift = idx
            else:
                result.append(ch)
        decrypted = ''.join(result)
        return restore_text(decrypted)


# Основная программа
if __name__ == "__main__":
    print("=" * 60)
    print("Шифры Виженера: самоключ и ключ-шифртекст")
    print("=" * 60)

    # Демонстрация на тестовом тексте для обоих режимов
    test_text = "волк каждый год линяет, а все сер бывает."
    test_key = "н"

    print("Исходный текст:", test_text)
    print("Секретная буква:", test_key)

    enc_self = vigenere_self_key_cipher(test_text, test_key, encrypt=True)
    dec_self = vigenere_self_key_cipher(enc_self, test_key, encrypt=False)
    print("\n[Самоключ]")
    print("Зашифровано:", enc_self)
    print("Расшифровано:", dec_self)

    enc_ciph = vigenere_ciphertext_autokey(test_text, test_key, encrypt=True)
    dec_ciph = vigenere_ciphertext_autokey(enc_ciph, test_key, encrypt=False)
    print("\n[Ключ-шифртекст]")
    print("Зашифровано:", enc_ciph)
    print("Расшифровано:", dec_ciph)

    # Меню для пользователя
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
            print("\nВыберите режим:")
            print("1 - Самоключ (autokey по открытому тексту)")
            print("2 - Ключ-шифртекст (ciphertext autokey)")
            mode = input("Ваш выбор: ").strip()
            if mode not in ('1', '2'):
                print("Неверный выбор режима.")
                continue

            user_text = input("Введите текст: ")
            user_key = input("Введите секретную букву (одну русскую букву): ").strip()
            try:
                if choice == '1':  # шифрование
                    if mode == '1':
                        result = vigenere_self_key_cipher(user_text, user_key, encrypt=True)
                    else:
                        result = vigenere_ciphertext_autokey(user_text, user_key, encrypt=True)
                    print("Зашифрованный текст:")
                else:  # расшифрование
                    if mode == '1':
                        result = vigenere_self_key_cipher(user_text, user_key, encrypt=False)
                    else:
                        result = vigenere_ciphertext_autokey(user_text, user_key, encrypt=False)
                    print("Расшифрованный текст:")
                print(result)
            except ValueError as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод, попробуйте снова.")