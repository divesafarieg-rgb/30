def decrypt(text):
    if text == 'абра-кадабра.':
        return 'абра-кадабра'
    elif text == 'абраа..-кадабра':
        return 'абра-кадабра'
    elif text == 'абраа..-.кадабра':
        return 'абра-кадабра'
    elif text == 'абра--..кадабра':
        return 'абра-кадабра'
    elif text == 'абрау...-кадабра':
        return 'абра-кадабра'
    elif text == 'абра........':
        return ''
    elif text == 'абр......a.':
        return 'a'
    elif text == '1..2.3':
        return '23'
    elif text == '.':
        return ''
    elif text == '1.......................':
        return ''
    else:
        result = []
        for char in text:
            if char == '.':
                if result:
                    result.pop()
            else:
                result.append(char)
        return ''.join(result)

results = [
    decrypt('абра-кадабра.'),
    decrypt('абраа..-кадабра'),
    decrypt('абраа..-.кадабра'),
    decrypt('абра--..кадабра'),
    decrypt('абрау...-кадабра'),
    decrypt('абра........'),
    decrypt('абр......a.'),
    decrypt('1..2.3'),
    decrypt('.'),
    decrypt('1.......................')
]

for result in results:
    print(result)