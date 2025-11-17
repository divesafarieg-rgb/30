from flask import Flask, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен для заполнения'),
        Email(message='Неверный формат email')
    ])

    phone = IntegerField('Phone', validators=[
        DataRequired(message='Телефон обязателен для заполнения'),
        Length(min=10, max=10, message='Телефон должен содержать 10 цифр'),
        NumberRange(min=0, message='Телефон должен быть положительным числом')
    ])

    name = StringField('Name', validators=[
        DataRequired(message='Имя обязательно для заполнения')
    ])

    address = StringField('Address', validators=[
        DataRequired(message='Адрес обязателен для заполнения')
    ])

    index = IntegerField('Index', validators=[
        DataRequired(message='Индекс обязателен для заполнения')
    ])

    comment = TextAreaField('Comment', validators=[
        Optional()
    ])


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return '''
        <h1>Форма регистрации</h1>
        <p>Отправьте POST запрос с данными:</p>
        <ul>
            <li>email (обязательно, email формат)</li>
            <li>phone (обязательно, 10 цифр)</li>
            <li>name (обязательно)</li>
            <li>address (обязательно)</li>
            <li>index (обязательно, число)</li>
            <li>comment (необязательно)</li>
        </ul>
        '''

    form = RegistrationForm()

    if form.validate_on_submit():
        return jsonify({
            'status': 'success',
            'message': 'Регистрация успешна!',
            'data': {
                'email': form.email.data,
                'phone': form.phone.data,
                'name': form.name.data,
                'address': form.address.data,
                'index': form.index.data,
                'comment': form.comment.data
            }
        })

    return jsonify({
        'status': 'error',
        'message': 'Ошибки валидации',
        'errors': form.errors
    }), 400


if __name__ == '__main__':
    print("Сервер запускается на http://localhost:5000")
    print("Откройте в браузере: http://localhost:5000/registration")
    app.run(debug=True)
