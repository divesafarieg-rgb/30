from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-123'


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()

    if form.validate_on_submit():
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Успех!</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1 style="color: green;">✅ Регистрация успешна!</h1>
            <p><strong>Email:</strong> {form.email.data}</p>
            <p><a href="/" style="color: blue;">Вернуться к форме</a></p>
        </body>
        </html>
        '''

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Форма с валидацией</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f0f0f0;
            }}
            .form-container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            .field {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-sizing: border-box;
            }}
            .error {{
                color: red;
                font-size: 14px;
                margin-top: 5px;
            }}
            button {{
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }}
            button:hover {{ background-color: #45a049; }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <h1>📝 Форма регистрации</h1>
            <p>Все поля обязательны для заполнения</p>

            <form method="POST">
                <input type="hidden" name="csrf_token" value="{form.csrf_token.current_token}">

                <div class="field">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" value="{form.email.data or ''}">
                    {''.join([f'<div class="error">{error}</div>' for error in form.email.errors])}
                </div>

                <div class="field">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" name="password">
                    {''.join([f'<div class="error">{error}</div>' for error in form.password.errors])}
                </div>

                <div class="field">
                    <label for="confirm_password">Подтвердите пароль:</label>
                    <input type="password" id="confirm_password" name="confirm_password">
                    {''.join([f'<div class="error">{error}</div>' for error in form.confirm_password.errors])}
                </div>

                <button type="submit">Зарегистрироваться</button>
            </form>

        </div>
    </body>
    </html>
    '''

    return html


if __name__ == '__main__':
    app.run(debug=True)