def invert_matrix(mat):
    n = len(mat)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(mat)]

    for col in range(n):
        # Поиск главного элемента
        pivot = col
        for row in range(col, n):
            if abs(aug[row][col]) > abs(aug[pivot][col]):
                pivot = row
        if abs(aug[pivot][col]) < 1e-12:
            return None  # матрица вырождена
        # Меняем строки местами
        aug[col], aug[pivot] = aug[pivot], aug[col]
        # Нормализуем текущую строку
        divider = aug[col][col]
        for j in range(2 * n):
            aug[col][j] /= divider
        # Обнуляем остальные строки в этом столбце
        for row in range(n):
            if row != col:
                factor = aug[row][col]
                for j in range(2 * n):
                    aug[row][j] -= factor * aug[col][j]

    # Извлекаем обратную матрицу из правой половины
    inv = [row[n:] for row in aug]
    return inv

def matrix_cipher(text, key_matrix, encrypt=True):
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя-'
    # перевод букв в числа и обратно
    letter_to_num = {ch: i + 1 for i, ch in enumerate(alphabet)}
    num_to_letter = {i + 1: ch for i, ch in enumerate(alphabet)}

    # словарь для замены знаков препинания
    punct_dict = {
        '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
        '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
        "'": 'апстр'
    }
    # словарь для обратной замены
    rev_punct = {v: k for k, v in punct_dict.items()}
    # замена пробелов
    space_repl = 'прбл'

    # подготовка исходного текста
    def prepare(txt):
        # приведение к нижнему регистру
        txt = txt.lower()
        # замена букв ё на е
        txt = txt.replace('ё', 'е')
        # замена знаков препинания на буквы
        for p, r in punct_dict.items():
            txt = txt.replace(p, r)
        # замена пробелов на прбл
        txt = txt.replace(' ', space_repl)
        return txt

    # обратная замена букв на пробелы или знаки препинания
    def restore(txt):
        txt = txt.replace(space_repl, ' ')
        for w, p in rev_punct.items():
            txt = txt.replace(w, p)
        return txt

    # преобразование букв в числа согласно их индекса в алфавите
    def text_to_numbers(txt):
        return [letter_to_num[ch] for ch in txt if ch in letter_to_num]

    # обратное преобразование чисел в буквы
    def numbers_to_text(nums):
        return ''.join(num_to_letter.get(round(n), '?') for n in nums)

    def mat_mult(matrix, vector):
        # определяем размерность матрицы (столбцы = строки)
        n = len(matrix)
        # создаем список из n нулей
        res = [0.0] * n
        # перебираем строки матрицы
        for i in range(n):
            # нулевая переменная s для суммы текущей строки
            s = 0.0
            # перебираем столбцы матрицы
            for j in range(n):
                # умножаем элемент матрицы на элемент вектора
                s += matrix[i][j] * vector[j]
            # записываем полученную сумму в переменную res
            res[i] = s
        return res

    # нахождение размерности ключ-матрицы
    n = len(key_matrix)
    # проверка матрицы на размерность не менее 3х3
    if n < 3:
        raise ValueError("Размер матрицы должен быть не менее 3")

    if encrypt:
        # подготовка текста
        prepared = prepare(text)
        # перевод букв в числа
        nums = text_to_numbers(prepared)
        if not nums:
            raise ValueError("Нет букв для шифрования")
        # определяем, кратна ли длина текста размерности матрицы
        rem = len(nums) % n
        # в случае, если длина не кратна, добавляем буквы а до кратности
        if rem != 0:
            nums += [33] * (n - rem)
        # разбиваем список чисел на блоки длины n
        blocks = [nums[i:i + n] for i in range(0, len(nums), n)]
        # создаем список encrypted_blocks для записи полученных векторов
        encrypted_blocks = []
        # для каждого блока (вектора длины n) выполняем его умножение на ключ-матрицу
        for blk in blocks:
            vec = blk
            res = mat_mult(key_matrix, vec)
            encrypted_blocks.extend(res)
        # вывод последовательности чисел, которая и является итоговым шифртекстом
        return ' '.join(str(int(round(x))) for x in encrypted_blocks)
    else:
        # расшифрование
        try:
            # создаем список, состоящий из поданных на расшифровку чисел
            nums = [float(x) for x in text.split()]
        except:
            raise ValueError("Неверный формат чисел. Ожидалась строка чисел, разделённых пробелами.")
        # проверяем количество чисел на кратность размерности матрицы
        if len(nums) % n != 0:
            raise ValueError("Количество чисел не кратно размеру матрицы")
        # вычисление обратной матрицы
        inv_matrix = invert_matrix(key_matrix)
        if inv_matrix is None:
            raise ValueError("Матрица вырождена, обратной не существует")
        # разбиваем список чисел на блоки длины n
        blocks = [nums[i:i + n] for i in range(0, len(nums), n)]
        decrypted_blocks = []
        for blk in blocks:
            res = mat_mult(inv_matrix, blk)
            rounded = [int(round(x)) for x in res]
            decrypted_blocks.extend(rounded)
        letters = numbers_to_text(decrypted_blocks)
        return restore(letters)

def input_matrix():
    print("Введите размер матрицы (n x n), n >= 3:")
    while True:
        try:
            n = int(input("n = "))
            if n < 3:
                print("Размер должен быть не менее 3")
                continue
            break
        except ValueError:
            print("Введите целое число")

    matrix = []
    print(f"Введите матрицу {n}x{n} построчно, числа через пробел (можно дробные, разделитель точка):")
    for i in range(n):
        while True:
            row_str = input(f"Строка {i + 1}: ").strip()
            try:
                row = [float(x) for x in row_str.split()]
                if len(row) != n:
                    print(f"Нужно {n} чисел")
                    continue
                matrix.append(row)
                break
            except ValueError:
                print("Неверный формат, введите числа через пробел (например: 1.5 2 -3)")

    # Проверка обратимости матрицы
    if invert_matrix(matrix) is None:
        print("Матрица вырождена (не имеет обратной). Пожалуйста, введите другую матрицу.")
        return input_matrix()
    else:
        return matrix


if __name__ == "__main__":
    print("=" * 60)
    print("МАТРИЧНЫЙ ШИФР")
    print("=" * 60)

    test_matrix = [
        [1, 4, 8],
        [3, 7, 2],
        [6, 9, 5]
    ]
    test_text = "забава"
    print("\n--- Демонстрация на примере из методички ---")
    print("Исходный текст:", test_text)
    print("Матрица-ключ:")
    for row in test_matrix:
        print(row)
    enc = matrix_cipher(test_text, test_matrix, encrypt=True)
    print("Зашифрованные числа:", enc)
    dec = matrix_cipher(enc, test_matrix, encrypt=False)
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
            print("\nВведите матрицу-ключ.")
            key_matrix = input_matrix()
            user_text = input("Введите текст: ").strip()
            try:
                if choice == '1':
                    result = matrix_cipher(user_text, key_matrix, encrypt=True)
                    print("Зашифрованный текст (числа):")
                    print(result)
                else:
                    result = matrix_cipher(user_text, key_matrix, encrypt=False)
                    print("Расшифрованный текст:")
                    print(result)
            except Exception as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод, попробуйте снова.")