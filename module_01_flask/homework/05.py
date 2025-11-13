from flask import Flask
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route('/get_time/future')
def future_time():
    current_time = datetime.now()
    time_after_hour = current_time + timedelta(hours=1)
    current_time_after_hour = time_after_hour.strftime('%H:%M:%S')

    return f'Точное время через час будет {current_time_after_hour}'


if __name__ == '__main__':
    app.run(debug=True)