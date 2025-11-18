import re


def load_english_words():
    word_set = {
        'password', 'admin', 'qwerty', 'login', 'user', 'secret', 'private',
        'public', 'secure', 'security', 'access', 'control', 'database',
        'network', 'system', 'server', 'client', 'computer', 'program',
        'code', 'master', 'test', 'example', 'sample', 'default', 'backup',
        'config', 'setting', 'username', 'email', 'account',

        'about', 'above', 'after', 'again', 'against', 'almost', 'alone',
        'along', 'already', 'also', 'although', 'always', 'among', 'another',
        'answer', 'anyone', 'anything', 'around', 'because', 'become',
        'before', 'behind', 'being', 'below', 'between', 'beyond', 'cannot',
        'certain', 'change', 'children', 'coming', 'could', 'country',
        'course', 'during', 'early', 'either', 'enough', 'every', 'everyone',
        'everything', 'following', 'getting', 'having', 'important', 'instead',
        'interest', 'itself', 'keeping', 'know', 'later', 'looking', 'making',
        'maybe', 'might', 'money', 'more', 'most', 'much', 'myself', 'necessary',
        'never', 'nothing', 'often', 'once', 'only', 'other', 'outside', 'over',
        'people', 'person', 'place', 'please', 'point', 'possible', 'present',
        'problem', 'program', 'public', 'putting', 'question', 'really', 'right',
        'saying', 'second', 'seems', 'several', 'should', 'since', 'something',
        'sometimes', 'still', 'such', 'taking', 'telling', 'thank', 'that',
        'their', 'them', 'then', 'there', 'these', 'thing', 'think', 'this',
        'those', 'though', 'thought', 'through', 'today', 'together', 'trying',
        'turned', 'under', 'until', 'upon', 'using', 'usually', 'various',
        'water', 'where', 'which', 'while', 'without', 'would', 'welcome',
        'beautiful', 'super', 'house', 'school', 'family', 'friend', 'mother',
        'father', 'sister', 'brother', 'office', 'worker', 'manager', 'company',
        'business', 'number', 'letter', 'window', 'table', 'chair', 'phone',
        'paper', 'music', 'movie', 'sport', 'game', 'color', 'black', 'white',
        'green', 'blue', 'animal', 'street', 'road', 'city', 'river', 'beach',
        'forest', 'garden', 'summer', 'spring', 'autumn', 'morning', 'evening',
        'language', 'english', 'hello', 'world'
    }
    return word_set


def extract_words_from_password(password):
    words = set()

    password_lower = password.lower()

    sequences = re.findall(r'[a-z]{5,}', password_lower)
    words.update(sequences)

    if password != password_lower and password != password.upper():
        split_words = re.findall(r'[A-Z]?[a-z]+', password)
        for word in split_words:
            word_lower = word.lower()
            if len(word_lower) > 4:
                words.add(word_lower)

    return words


def is_strong_password(password):
    words_in_password = extract_words_from_password(password)

    for word in words_in_password:
        if word in ENGLISH_WORDS:
            return False

    return True


ENGLISH_WORDS = load_english_words()

if __name__ == "__main__":
    test_passwords = [
        "password123!",
        "HelloWorld2024",
        "Df7#kL9@mP2!",
        "1234567890",
        "Cat123!",
        "AdminUser123",
        "MySuperPassword!",
        "XyZ123!@#",
        "Welcome2024",
        "BeautifulDay",
    ]

    print("Проверка сложности паролей:")
    print("=" * 40)

    for password in test_passwords:
        result = is_strong_password(password)
        status = "ХОРОШИЙ" if result else "ПЛОХОЙ"
        print(f"Пароль: {password:20} -> {status}")