from flask import Flask

app = Flask(__name__)

counter = 0

@app.route('/counter')
def count_visits():
    global counter
    counter += 1
    return f'Страница была открыта {counter} раз'

if __name__ == '__main__':
    app.run(debug=True)