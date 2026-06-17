def caesar_cipher(text, shift, decrypt=False):
    # Проверка, что сдвиг находится в допустимом диапазоне (1..31)
    if not (1 <= shift <= 31):
        return "Ошибка: ключ должен быть в диапазоне от 1 до 31"

    # Русский алфавит без буквы «ё» (32 буквы, индексы 0..31)
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

    # Словарь замены знаков препинания на буквенные коды (для шифрования)
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

    # Обратный словарь для восстановления знаков препинания при расшифровании
    reverse_punct_dict = {v: k for k, v in punct_dict.items()}

    # ------------------- РЕЖИМ ШИФРОВАНИЯ -------------------
    if not decrypt:
        # Подготовка текста: нижний регистр, замена «ё» на «е»
        text = text.lower()
        text = text.replace('ё', 'е')

        # Замена знаков препинания на кодовые слова
        for punct, replacement in punct_dict.items():
            text = text.replace(punct, replacement)

        # Замена пробелов на спецслово 'прбл' (чтобы пробелы сохранялись при шифровании)
        text = text.replace(' ', 'прбл')

        # Шифрование каждой буквы: сдвиг на shift позиций вперёд по алфавиту (по модулю 32)
        result = []
        for i in text:                      # i – текущий символ обработанного текста
            if i in alphabet:
                index = alphabet.index(i)   # получаем индекс буквы (0..31)
                new_index = (index + shift) % 32
                result.append(alphabet[new_index])
            else:
                # Символы не из алфавита (например, цифры) переносим без изменений
                result.append(i)
        return ''.join(result)

    # ------------------- РЕЖИМ РАСШИФРОВАНИЯ -------------------
    else:
        # Прямой проход по шифртексту: для каждой буквы выполняем сдвиг назад
        result = []
        for i in text:                      # i – символ шифртекста
            if i in alphabet:
                index = alphabet.index(i)
                new_index = (index - shift) % 32   # вычитаем сдвиг
                result.append(alphabet[new_index])
            else:
                result.append(i)

        text = ''.join(result)

        # Восстановление пробелов (обратная замена 'прбл' → ' ')
        text = text.replace('прбл', ' ')

        # Восстановление знаков препинания (обратная замена кодовых слов)
        for word, punct in reverse_punct_dict.items():
            text = text.replace(word, punct)

        return text


def decrypt_caesar_cipher(text, shift):
    """Удобная обёртка для расшифрования (вызывает основную функцию с флагом decrypt=True)."""
    return caesar_cipher(text, shift, decrypt=True)


if __name__ == "__main__":
    # Демонстрационный пример
    test_text = "волк каждый год линяет, а все сер бывает."
    shift = 3

    print("=" * 50)
    print("Исходный текст:")
    print(test_text)
    print(f"Сдвиг: {shift}")

    # Шифрование демо-текста
    encrypted = caesar_cipher(test_text, shift, decrypt=False)
    print("\nЗашифрованный текст:")
    print(encrypted)

    # Расшифрование демо-текста
    decrypted = caesar_cipher(encrypted, shift, decrypt=True)
    print("\nРасшифрованный текст:")
    print(decrypted)

    # Проверка корректности
    if test_text.lower().replace('ё', 'е') == decrypted:
        print("\n✓ Шифрование и расшифрование выполнены корректно!")
    else:
        print("\n✗ Ошибка при расшифровании")

    # Интерактивная часть: пользователь выбирает действие
    print("\n" + "=" * 50)

    while True:
        print("\nВыберите действие:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        choice = input("Введите номер действия (1 или 2): ")

        if choice == '1':
            user_text = input("\nВведите текст для шифрования: ")
            user_shift = int(input("Введите сдвиг (от 1 до 31): "))

            encrypted = caesar_cipher(user_text, user_shift, decrypt=False)

            if encrypted.startswith("Ошибка:"):
                print(encrypted)
                print("Пожалуйста, введите корректный сдвиг.")
            else:
                print("\n" + "=" * 50)
                print("Зашифрованный текст:")
                print(encrypted)
                break

        elif choice == '2':
            user_text = input("\nВведите текст для расшифрования: ")
            user_shift = int(input("Введите сдвиг (от 1 до 31): "))

            decrypted = caesar_cipher(user_text, user_shift, decrypt=True)

            if decrypted.startswith("Ошибка:"):
                print(decrypted)
                print("Пожалуйста, введите корректный сдвиг.")
            else:
                print("\n" + "=" * 50)
                print("Расшифрованный текст:")
                print(decrypted)
                break

        else:
            print("Неверный выбор. Пожалуйста, введите 1 или 2.")

    print("=" * 50)