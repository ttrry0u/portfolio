import sys
import math

# Алфавит из 32 русских букв (без буквы «ё», которая при подготовке текста заменяется на «е»).
ALPHABET = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
            "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
            "ъ", "ы", "ь", "э", "ю", "я"]
M = len(ALPHABET)                 # мощность алфавита (32)

# Словарь замены знаков препинания на буквенные коды (подготовка текста к шифрованию).
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз'
}
# Обратный словарь для восстановления знаков препинания после расшифрования.
rev_punct = {v: k for k, v in punct_dict.items()}
space_repl = 'прбл'               # заменитель пробела


def digitization_for_Shannon(open_text):
    """
    Перевод букв открытого текста в числовую форму.
    Каждой букве ставится в соответствие её порядковый номер в алфавите (от 1 до 32).
    """
    return [ALPHABET.index(ch) + 1 for ch in open_text]


def undigitization_for_Shannon(ciphertext):
    """
    Обратное преобразование: последовательности чисел (1…32) в строку из букв.
    """
    return "".join(ALPHABET[n - 1] for n in ciphertext)


def generate_gamma_for_Shannon(a, c, t0, length):
    """
    Генерация гаммы с помощью линейного конгруэнтного генератора (ЛКГ).
    Параметры:
        a, c – множитель и приращение ЛКГ,
        t0  – начальное значение (зерно),
        length – требуемая длина гаммы (количество символов).
    Формула: t[i+1] = (a * t[i] + c) mod M.
    Гамма представляет собой последовательность целых чисел в диапазоне [0, M-1].
    """
    t, gamma = t0, []
    for _ in range(length):
        t = (a * t + c) % M
        gamma.append(t)
    return gamma


def decryption_format(dec_text):
    """
    Оформление расшифрованного текста:
    – замена служебных кодов на пробелы и знаки препинания,
    – первая буква становится заглавной,
    – после каждой точки следующий непробельный символ делается заглавным.
    """
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace('прбл', ' ')
    if not dec_text:
        return ""
    result_list = list(dec_text[0].upper() + dec_text[1:])
    for i in range(len(result_list) - 2):
        if result_list[i] == "." and i + 2 < len(result_list):
            result_list[i + 2] = result_list[i + 2].upper()
    return "".join(result_list)


def validate_key_params():
    """
    Интерактивный ввод и проверка параметров ЛКГ:
    a – нечётное, a ≥ 5, a ≡ 1 (mod 4);
    c – нечётное, 0 < c < M, gcd(c, M) = 1;
    t0 – начальное значение, 0 ≤ t0 ≤ M-1.
    Возвращает кортеж (a, c, t0).
    """
    while True:
        try:
            a = int(input(f"\nВведите a (нечётное, a ≡ 1 mod 4, a ≥ 5): "))
        except ValueError:
            print("Введите целое число.")
            continue

        errors = []
        if a < 5:
            errors.append("a должно быть не менее 5 (a = 1 недопустимо)")
        if a % 2 != 1:
            errors.append("a должно быть нечётным числом")
        elif (a - 1) % 4 != 0:
            errors.append("(a − 1) должно делиться на 4 → a ≡ 1 (mod 4)")

        if errors:
            print("Ошибка параметра a:")
            for e in errors:
                print(f"      • {e}")
            print("Подсказка: 5, 9, 13, 17, 21, 25, 29, 33 ...")
            continue
        break

    while True:
        try:
            c = int(input(f"Введите c (нечётное, взаимно простое с {M}, 0 < c < {M}): "))
        except ValueError:
            print("Введите целое число.")
            continue

        errors = []
        if not (0 < c < M):
            errors.append(f"c должно быть в диапазоне (0, {M})")
        if math.gcd(c, M) != 1:
            errors.append(f"НОД(c, {M}) ≠ 1 → c должно быть нечётным числом")

        if errors:
            print("Ошибка параметра c:")
            for e in errors:
                print(f"      • {e}")
            print("Подсказка: 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31")
            continue
        break

    while True:
        try:
            t0 = int(input(f"Введите t0 (начальное значение, 0 ≤ t0 ≤ {M-1}): "))
        except ValueError:
            print("Введите целое число.")
            continue

        if not (0 <= t0 <= M-1):
            print(f"t0 должно быть в диапазоне [0, {M-1}].")
            continue
        break

    print(f"\n Ключ принят: a = {a}, c = {c}, t0 = {t0}\n")
    return a, c, t0


def Shannon_notebook(operation, text):
    """
    Основная процедура шифрования (operation == 1) или расшифрования (operation == 2)
    по схеме одноразового блокнота, где гамма вырабатывается ЛКГ.
    """
    # Ввод параметров генератора с проверкой
    a, c, t0 = validate_key_params()

    # Перевод текста в числовые коды (1..32)
    digital_text = digitization_for_Shannon(text)

    # Генерация гаммы той же длины, что и текст
    gamma = generate_gamma_for_Shannon(a, c, t0, len(digital_text))

    if operation == 1:
        # Шифрование: (p + g - 1) mod M + 1, где p – код буквы (1..32), g – гамма (0..31)
        encrypted = [((p - 1 + g) % M) + 1 for p, g in zip(digital_text, gamma)]
        ciphertext = undigitization_for_Shannon(encrypted)

        # Группировка для наглядного вывода (по 5 символов)
        letter_groups = [ciphertext[i:i+5] for i in range(0, len(ciphertext), 5)]
        number_groups = [encrypted[i:i+5] for i in range(0, len(encrypted), 5)]

        print("\nЗашифрованный текст:")
        print("Буквы:", ' '.join(''.join(g) for g in letter_groups))
        print("Цифры:", '  '.join(' '.join(str(n) for n in g) for g in number_groups))
        print()

    else:
        # Расшифрование: (e - 1 - g) mod M + 1
        decrypted_nums = [((e - 1 - g) % M) + 1 for e, g in zip(digital_text, gamma)]
        open_text = undigitization_for_Shannon(decrypted_nums)
        formatted = decryption_format(open_text)
        print("Расшифрованный текст:", formatted)
        print()


def run_demo():
    """Демонстрация работы алгоритма на фиксированном примере."""
    print("\n--- Демонстрация шифра-блокнота Шеннона ---")
    demo_text = "волк каждый год линяет, а все сер бывает."
    demo_a, demo_c, demo_t0 = 9, 5, 1

    print("Исходный текст:", demo_text)
    print("Параметры ЛКГ: a = {}, c = {}, t0 = {}".format(demo_a, demo_c, demo_t0))

    # Подготовка текста (аналогично prepare_text в других шифрах)
    prepared = demo_text.lower().replace('ё', 'е')
    for p, r in punct_dict.items():
        prepared = prepared.replace(p, r)
    prepared = prepared.replace(' ', space_repl)

    nums = digitization_for_Shannon(prepared)
    gamma = generate_gamma_for_Shannon(demo_a, demo_c, demo_t0, len(nums))
    encrypted_nums = [((p - 1 + g) % M) + 1 for p, g in zip(nums, gamma)]
    ciphertext = undigitization_for_Shannon(encrypted_nums)
    print("Зашифрованный текст (буквы):", ciphertext)

    # Расшифрование
    decrypted_nums = [((e - 1 - g) % M) + 1 for e, g in zip(encrypted_nums, gamma)]
    decrypted = undigitization_for_Shannon(decrypted_nums)
    restored = decryption_format(decrypted)
    print("Расшифрованный текст:", restored)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("ШИФР-БЛОКНОТ ШЕННОНА (одноразовый блокнот)")
    print("Алфавит: 32 русские буквы (без ё, заменяется на е)")
    print("Знаки препинания заменяются на слова, пробелы на 'прб'")
    print("Генератор гаммы: линейный конгруэнтный (ЛКГ)")
    print("=" * 60)

    run_demo()

    while True:
        print("─" * 40)
        print("Выберите действие:")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("0 - Выход")
        print("─" * 40)

        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            print("Ошибка: введите число.\n")
            continue

        if choice == 0:
            print("До свидания!")
            sys.exit()
        elif choice not in (1, 2):
            print("Неверный выбор!\n")
            continue

        text = input("\nВведите текст: ").lower()

        # Предварительная обработка текста: при шифровании заменяем знаки и пробелы,
        # при расшифровании – удаляем пробелы (входные данные уже идут без пробелов, но они допустимы).
        if choice == 1:
            for p, r in punct_dict.items():
                text = text.replace(p, r)
            text = text.replace(' ', space_repl)
        else:
            text = text.replace(' ', '')

        Shannon_notebook(choice, text)