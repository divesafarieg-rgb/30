from datetime import datetime
from flask import Flask

app = Flask(__name__)

def get_weekday_greeting():
    weekdays_list = [
        "понедельника", "вторника", "среды",
        "четверга", "пятницы", "субботы", "воскресенья"
    ]
    weekday = datetime.today().weekday()
    return weekdays_list[weekday]

@app.route('/hello-world/<name>')
def hello_world(name):
    day = get_weekday_greeting()
    return f"Привет, {name}. Хорошего {day}!"

if __name__ == '__main__':
    app.run(debug=True)