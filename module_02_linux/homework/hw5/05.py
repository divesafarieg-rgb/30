from flask import Flask

app = Flask(__name__)


@app.route('/max_number/<path:numbers>')
def max_number(numbers):
    parts = numbers.split('/')

    numbers_found = []

    for part in parts:
        if part.isdigit():
            numbers_found.append(int(part))
        else:
            try:
                clean_part = part.strip()
                num = float(clean_part)
                numbers_found.append(num)
            except:
                pass

    if len(numbers_found) == 0:
        return "Не удалось найти числа для сравнения"

    maximum = max(numbers_found)

    if isinstance(maximum, float) and maximum.is_integer():
        maximum = int(maximum)

    return f"Максимальное число: <i>{maximum}</i>"


if __name__ == '__main__':
    app.run(debug=True)