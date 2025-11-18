from flask import Flask, render_template_string, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Главная страница</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
                line-height: 1.6;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }
            .nav {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .nav ul {
                list-style: none;
                padding: 0;
            }
            .nav li {
                margin: 10px 0;
            }
            .nav a {
                display: block;
                padding: 10px 15px;
                background: #f8f9fa;
                border-radius: 5px;
                text-decoration: none;
                color: #333;
                transition: all 0.3s;
            }
            .nav a:hover {
                background: #667eea;
                color: white;
                transform: translateX(10px);
            }
            .content {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                margin: 0;
                font-size: 2.5em;
            }
            .welcome {
                font-size: 1.2em;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Добро пожаловать!</h1>
            <p class="welcome">Это главная страница нашего сайта</p>
        </div>

        <div class="nav">
            <h2>📋 Быстрая навигация:</h2>
            <ul>
                <li><a href="/">🏠 Главная страница</a></li>
                <li><a href="/about">ℹ️ О нас</a></li>
                <li><a href="/contact">📞 Контакты</a></li>
                <li><a href="/services">🛠️ Услуги</a></li>
            </ul>
        </div>

        <div class="content">
            <h2>О нашем сайте</h2>
            <p>Это демонстрационный сайт, созданный на Flask. Здесь вы можете увидеть:</p>
            <ul>
                <li>Красивую главную страницу</li>
                <li>Автоматическую обработку ошибок 404</li>
                <li>Список всех доступных страниц</li>
                <li>Простой и понятный код</li>
            </ul>

            <p>Попробуйте перейти по несуществующему адресу, например: 
               <a href="/nonexistent-page">/nonexistent-page</a></p>
        </div>
    </body>
    </html>
    ''')


@app.route('/about')
def about():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>О нас</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .back-link { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>ℹ️ О нас</h1>
        <p>Мы - команда энтузиастов, создающих интересные проекты!</p>
        <p>Этот сайт демонстрирует возможности Flask для обработки ошибок 404.</p>
        <div class="back-link">
            <a href="/">← Назад на главную</a>
        </div>
    </body>
    </html>
    ''')


@app.route('/contact')
def contact():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Контакты</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .back-link { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>📞 Контакты</h1>
        <p>Свяжитесь с нами:</p>
        <ul>
            <li>Email: example@example.com</li>
            <li>Телефон: +7 (999) 123-45-67</li>
            <li>Адрес: г. Москва, ул. Примерная, д. 1</li>
        </ul>
        <div class="back-link">
            <a href="/">← Назад на главную</a>
        </div>
    </body>
    </html>
    ''')


@app.route('/services')
def services():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Услуги</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .back-link { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>🛠️ Услуги</h1>
        <p>Наши услуги:</p>
        <ul>
            <li>Разработка веб-приложений</li>
            <li>Создание API</li>
            <li>Обучение программированию</li>
            <li>Техническая поддержка</li>
        </ul>
        <div class="back-link">
            <a href="/">← Назад на главную</a>
        </div>
    </body>
    </html>
    ''')


def get_available_pages():
    pages = []

    for rule in app.url_map.iter_rules():
        if (rule.endpoint != 'static' and
                not rule.rule.startswith('/static/') and
                'GET' in rule.methods):
            pages.append({
                'url': rule.rule,
                'endpoint': rule.endpoint
            })

    return pages


@app.errorhandler(404)
def page_not_found(error):
    pages = get_available_pages()

    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Страница не найдена</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                background-color: #f8f9fa;
            }
            .error-header {
                background: #dc3545;
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }
            .pages-list {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            ul {
                list-style: none;
                padding: 0;
            }
            li {
                margin: 15px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                transition: all 0.3s;
            }
            li:hover {
                background: #e9ecef;
                transform: translateX(10px);
            }
            a {
                text-decoration: none;
                color: #007bff;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
            .back-home {
                margin-top: 30px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="error-header">
            <h1>🚫 Ошибка 404 - Страница не найдена</h1>
            <p>Запрошенный URL: <code>{{ requested_url }}</code> не существует на сервере.</p>
        </div>

        <div class="pages-list">
            <h2>📋 Доступные страницы:</h2>
            <ul>
                {% for page in pages %}
                    <li>
                        <a href="{{ page.url }}">{{ page.endpoint }}</a>
                        <small>({{ page.url }})</small>
                    </li>
                {% endfor %}
            </ul>

            <div class="back-home">
                <a href="/">← Вернуться на главную страницу</a>
            </div>
        </div>
    </body>
    </html>
    '''

    return render_template_string(
        html_template,
        pages=pages,
        requested_url=request.path
    ), 404


if __name__ == '__main__':
    app.run(debug=True)