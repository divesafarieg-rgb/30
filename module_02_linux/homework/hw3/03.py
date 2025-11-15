def decrypt(text):
    result = []

    i = 0
    while i < len(text):
        if text[i] == '.':
            if i + 1 < len(text) and text[i + 1] == '.':
                if result:
                    result.pop()
                i += 2
            else:
                i += 1
        else:
            result.append(text[i])
            i += 1

    return ''.join(result)


def test_decrypt():
    test_cases = [
        ("абра-кадабра.", "абра-кадабра"),
        ("абраа..-кадабра", "абра-кадабра"),
        ("абраа..-.кадабра", "абра-кадабра"),
        ("абра--..кадабра", "абра-кадабра"),
        ("абрау...-кадабра", "абра-кадабра"),
        ("абра........", ""),
        ("абр......a.", "a"),
        ("1..2.3", "23"),
        (".", ""),
        ("1.......................", ""),
        ("", ""),
        ("abc", "abc"),
        ("a.b.c", "abc"),
        ("a..b..c", "c"),
        ("..abc", "abc"),
        ("abc..", "ab"),
        ("a....b", "b"),
    ]

    print("Тестирование функции decrypt:")
    print("=" * 50)

    all_passed = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = decrypt(input_text)
        status = "✓ ПРОЙДЕН" if result == expected else "✗ ОШИБКА"
        color = "\033[92m" if result == expected else "\033[91m"
        reset = "\033[0m"

        print(f"Тест {i:2d}: {color}{status}{reset}")
        print(f"      Вход:    '{input_text}'")
        print(f"      Ожидаем: '{expected}'")
        print(f"      Получили: '{result}'")

        if result != expected:
            all_passed = False
        print()

    print("=" * 50)
    if all_passed:
        print("\033[92mВсе тесты пройдены успешно!\033[0m")
    else:
        print("\033[91mНекоторые тесты не пройдены!\033[0m")

    return all_passed


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_decrypt()
        elif sys.argv[1] == "--example":
            examples = [
                "абра-кадабра.",
                "абраа..-кадабра",
                "абраа..-.кадабра",
                "абра--..кадабра",
                "абрау...-кадабра",
                "абра........",
                "абр......a.",
                "1..2.3",
                ".",
                "1......................."
            ]

            print("Примеры из условия задачи:")
            print("=" * 40)
            for example in examples:
                result = decrypt(example)
                print(f"'{example}' -> '{result}'")
        else:
            input_text = ' '.join(sys.argv[1:])
            print(decrypt(input_text))
    else:
        input_text = sys.stdin.read().strip()
        print(decrypt(input_text))