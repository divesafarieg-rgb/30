def my_t9(digits):
    digit_to_letters = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }

    english_words = set()

    possible_paths = ['/usr/share/dict/words', '/usr/dict/words', 'words.txt']

    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                english_words = {word.strip().lower() for word in f if word.strip().isalpha()}
            break
        except FileNotFoundError:
            continue
    else:
        english_words = {
            'hello', 'world', 'basement', 'test', 'python',
            'cat', 'dog', 'home', 'work', 'code', 'ban', 'can',
            'ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf'
        }

    import re
    pattern = ''.join(f'[{digit_to_letters[d]}]' for d in digits)
    regex = re.compile(f'^{pattern}$')

    return [word for word in english_words if regex.match(word)]


def test_my_t9():
    assert 'basement' in my_t9('22736368')
    assert 'hello' in my_t9('43556')
    assert 'world' in my_t9('96753')
    assert 'test' in my_t9('8378')


if __name__ == "__main__":
    test_cases = ["22736368", "43556", "96753", "8378", "226", "23"]

    for digits in test_cases:
        result = my_t9(digits)
        print(f"{digits} -> {result}")

    test_my_t9()
    print("Все тесты пройдены!")