from flask import Flask

app = Flask(__name__)
finance_data = {}


@app.route('/add/<date>/<int:number>')
def add_expense(date, number):
    year = int(date[:4])
    month = int(date[4:6])

    year_data = finance_data.setdefault(year, {'total': 0})
    month_data = year_data.setdefault(month, {'total': 0})

    month_data['total'] += number
    year_data['total'] += number

    return f"Трата {number} руб. добавлена за {date}"


@app.route('/calculate/<int:year>')
def calculate_year(year):
    year_data = finance_data.get(year)
    if not year_data:
        return f"Нет данных за {year} год"

    return f"Траты за {year} год: {year_data.get('total', 0)} руб."


@app.route('/calculate/<int:year>/<int:month>')
def calculate_month(year, month):
    year_data = finance_data.get(year)
    if not year_data:
        return f"Нет данных за {year} год"

    month_data = year_data.get(month)
    if not month_data:
        return f"Нет данных за {month}.{year}"

    return f"Траты за {month}.{year}: {month_data.get('total', 0)} руб."


if __name__ == '__main__':
    app.run(debug=True)