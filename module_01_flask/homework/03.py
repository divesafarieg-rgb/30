from flask import Flask
from random import choice

app = Flask(__name__)

cat_breeds = ['корниш-рекс', 'русская голубая', 'шотландская вислоухая', 'мейн-кун', 'манчкин']

@app.route('/cats')
def cats():
    random_breed = choice(cat_breeds)
    return f'''
    <html>
        <head>
            <title>{random_breed}</title>
        </head>
        <body>
            <h1>Случайная порода кошек: {random_breed}</h1>
            <p>Обновите страницу для получения новой породы!</p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)