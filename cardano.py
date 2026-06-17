import random
import numpy as np

# ---------- Словари замены знаков препинания и пробела ----------
punct_dict = {
    '.': 'тчк', ',': 'зпт', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз',
    "'": 'апстр'
}
rev_punct = {v: k for k, v in punct_dict.items()}   # обратный словарь
space_repl = 'прбл'                                 # заменитель пробела


def prepare_text(txt):
    """Подготовка открытого текста: строчные буквы, замена ё→е, знаков и пробелов."""
    txt = txt.lower()
    txt = txt.replace('ё', 'е')
    for p, r in punct_dict.items():
        txt = txt.replace(p, r)
    txt = txt.replace(' ', space_repl)
    return txt


def restore_text(txt):
    """Восстановление пробелов и знаков препинания после расшифрования."""
    txt = txt.replace(space_repl, ' ')
    for w, p in rev_punct.items():
        txt = txt.replace(w, p)
    return txt


# ---------- Фиксированные трафареты решётки Кардано (6×10) ----------
# table1 – исходное положение вырезов (1 – клетка закрыта, 0 – прорезь)
table1 = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0, 1, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 0, 0, 1, 1, 0]
]

# Остальные положения получаются последовательными поворотами и отражениями,
# как указано в методическом пособии.
table2 = np.flip(table1, axis=(0,1)).tolist()   # поворот на 180°
table3 = np.flip(table2, axis=1).tolist()       # отражение от вертикали
table4 = np.flip(table3, axis=(0,1)).tolist()   # поворот на 180° отражённой

# Порядок использования положений: исходное → поворот 180° → отражение → поворот 180° отражения
tables = [table1, table2, table3, table4]


def cardan_crypt(text):
    """
    Шифрование текста с помощью решётки Кардано.
    Текст дополняется случайными буквами до длины, кратной 60.
    Процесс: на каждые 60 символов текста решётка накладывается 4 раза,
    в прорези (0) записываются очередные символы.
    После четырёх наложений таблица построчно выводится в шифртекст.
    """
    global shifrReshetka, encryptReshetka
    # Две матрицы 6×10: shifrReshetka – заполняется символами,
    # encryptReshetka – используется при расшифровании (здесь не нужна)
    shifrReshetka = [['' for _ in range(10)] for _ in range(6)]
    encryptReshetka = [['' for _ in range(10)] for _ in range(6)]

    # Дополнение текста случайными буквами до кратности 60
    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    if len(text) % 60 != 0:
        text += ''.join(random.choice(alphabet) for _ in range(60 - len(text) % 60))

    k = 1                         # счётчик шагов (наложение / вывод)
    pos = 0                       # позиция в исходном тексте
    shifrT = ""                   # строка для накопления шифртекста
    ran = (len(text) // 60) * 4   # общее количество операций наложения

    for _ in range(ran):
        idx = (k % 5) - 1         # индекс положения в списке tables (0..3)
        if 0 <= idx < 4:
            grid = tables[idx]    # текущий трафарет
            # Записываем символы текста в прорези (grid[row][col] == 0)
            for row in range(6):
                for col in range(10):
                    if grid[row][col] == 0:
                        shifrReshetka[row][col] = text[pos]
                        pos += 1
            k += 1

        # После четырёх наложений (k становится кратным 5) – выводим таблицу
        if k % 5 == 0:
            for i in range(6):
                for j in range(10):
                    shifrT += shifrReshetka[i][j]
            k += 1

    return shifrT


def cardan_decrypt(text):
    """
    Расшифрование текста, зашифрованного решёткой Кардано.
    Процесс обратный: сначала таблица заполняется шифртекстом,
    затем из прорезей соответствующих положений извлекаются символы.
    """
    global shifrReshetka, encryptReshetka
    shifrReshetka = [['' for _ in range(10)] for _ in range(6)]
    encryptReshetka = [['' for _ in range(10)] for _ in range(6)]  # сюда будем заносить шифртекст

    k = 0
    pos = 0                       # позиция в строке шифртекста
    shifrT = ""                   # строка для восстановленного текста
    ran = (len(text) // 60) * 5   # общее число операций (5 на блок из 60 символов)

    for _ in range(ran):
        # Заполнение таблицы шифртекстом (k % 5 == 0)
        if k % 5 == 0:
            for i in range(6):
                for j in range(10):
                    encryptReshetka[i][j] = text[pos]
                    pos += 1
            k += 1
        # Извлечение символов через прорези для положений 1,2,3,4
        elif k % 5 == 1:
            grid = tables[0]
            for row in range(6):
                for col in range(10):
                    if grid[row][col] == 0:
                        shifrT += encryptReshetka[row][col]
            k += 1
        elif k % 5 == 2:
            grid = tables[1]
            for row in range(6):
                for col in range(10):
                    if grid[row][col] == 0:
                        shifrT += encryptReshetka[row][col]
            k += 1
        elif k % 5 == 3:
            grid = tables[2]
            for row in range(6):
                for col in range(10):
                    if grid[row][col] == 0:
                        shifrT += encryptReshetka[row][col]
            k += 1
        elif k % 5 == 4:
            grid = tables[3]
            for row in range(6):
                for col in range(10):
                    if grid[row][col] == 0:
                        shifrT += encryptReshetka[row][col]
            k += 1

    return shifrT


def cardano_cipher(text, key=None, encrypt=True):
    """Объединяющая функция: шифрование или расшифрование с обработкой текста."""
    if encrypt:
        prepared = prepare_text(text)
        cipher = cardan_crypt(prepared)
        return cipher
    else:
        decrypted_prepared = cardan_decrypt(text)
        return restore_text(decrypted_prepared)


def input_key():
    """Заглушка для единообразия интерфейса; ключ не требуется."""
    print("(В данном варианте решетка фиксирована, ключ не нужен)")
    return ""


if __name__ == "__main__":
    print("=" * 60)
    print("ШИФР 'ПОВОРОТНАЯ РЕШЕТКА КАРДАНО' (6x10, по методичке)")
    print("Последовательность: исходная → поворот 180° → отражение → поворот 180°")
    print("Текст дополняется случайными буквами до кратности 60.")
    print("=" * 60)

    demo_text = "волк каждый год линяет, а все сер бывает."
    print("\n--- Демонстрация ---")
    print("Исходный текст:", demo_text)

    enc = cardano_cipher(demo_text, encrypt=True)
    print("Зашифрованный текст:", enc)
    dec = cardano_cipher(enc, encrypt=False)
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
            user_text = input("Введите текст: ").strip()
            try:
                if choice == '1':
                    result = cardano_cipher(user_text, encrypt=True)
                    print("Зашифрованный текст:")
                    print(result)
                else:
                    result = cardano_cipher(user_text, encrypt=False)
                    print("Расшифрованный текст:")
                    print(result)
            except Exception as e:
                print("Ошибка:", e)
        else:
            print("Неверный ввод, попробуйте снова.")