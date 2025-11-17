from typing import Optional
from wtforms import Field, IntegerField, SubmitField, ValidationError
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from flask import Flask, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


def number_length(min: int, max: int, message: Optional[str] = None):
    def _number_length(form: FlaskForm, field: Field):
        value = field.data

        if value is None:
            raise ValidationError(message or 'Поле обязательно для заполнения')

        num_str = str(abs(value))
        length = len(num_str)

        if not (min <= length <= max):
            if message:
                raise ValidationError(message)
            else:
                raise ValidationError(f'Длина числа должна быть от {min} до {max} цифр')

    return _number_length


class NumberLength:
    def __init__(self, min: int, max: int, message: Optional[str] = None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        value = field.data

        if value is None:
            raise ValidationError(self.message or 'Поле обязательно для заполнения')

        num_str = str(abs(value))
        length = len(num_str)

        if not (self.min <= length <= self.max):
            if self.message:
                raise ValidationError(self.message)
            else:
                raise ValidationError(f'Длина числа должна быть от {self.min} до {self.max} цифр')


class PhoneForm1(FlaskForm):
    phone = IntegerField('Телефон (функциональный валидатор):',
                         validators=[InputRequired(), number_length(10, 15, "Номер должен содержать от 10 до 15 цифр")])
    submit = SubmitField('Проверить')


class PhoneForm2(FlaskForm):
    phone = IntegerField('Телефон (классный валидатор):',
                         validators=[InputRequired(), NumberLength(5, 12)])
    submit = SubmitField('Проверить')


@app.route('/', methods=['GET', 'POST'])
def index():
    form1 = PhoneForm1()
    form2 = PhoneForm2()

    if form1.submit.data and form1.validate():
        return f"Форма 1: Номер {form1.phone.data} прошел валидацию!"

    if form2.submit.data and form2.validate():
        return f"Форма 2: Номер {form2.phone.data} прошел валидацию!"

    template = '''
    <h3>Форма 1 (функциональный валидатор): от 10 до 15 цифр</h3>
    <form method="POST">
        {{ form1.csrf_token }}
        {{ form1.phone.label }} {{ form1.phone() }}<br>
        {% if form1.phone.errors %}
            <span style="color: red;">{{ form1.phone.errors[0] }}</span><br>
        {% endif %}
        {{ form1.submit() }}
    </form>

    <hr>

    <h3>Форма 2 (классный валидатор): от 5 до 12 цифр</h3>
    <form method="POST">
        {{ form2.csrf_token }}
        {{ form2.phone.label }} {{ form2.phone() }}<br>
        {% if form2.phone.errors %}
            <span style="color: red;">{{ form2.phone.errors[0] }}</span><br>
        {% endif %}
        {{ form2.submit() }}
    </form>
    '''

    return render_template_string(template, form1=form1, form2=form2)


if __name__ == '__main__':
    app.run(debug=True)
