import os
import random
import requests
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, String, Integer, Boolean, JSON, ForeignKey, text
from sqlalchemy.dialects.postgresql import ARRAY
from pathlib import Path


def load_env_file():
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Загружено: {key}={value}")


load_env_file()

app = Flask(__name__)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ВНИМАНИЕ: DATABASE_URL не найден, используем значение по умолчанию")
    database_url = 'postgresql://postgres@127.0.0.1:5432/skillbox_db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Используется БД: {app.config['SQLALCHEMY_DATABASE_URI']}")

db = SQLAlchemy(app)

app.config['DB_INITIALIZED'] = False


class Coffee(db.Model):
    __tablename__ = 'coffee'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200))
    description = db.Column(db.String(200))
    reviews = db.Column(ARRAY(String))

    users = db.relationship('User', backref='coffee', lazy=True)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    has_sale = db.Column(db.Boolean, default=False)
    address = db.Column(JSON)
    coffee_id = db.Column(db.Integer, db.ForeignKey('coffee.id'))


FIRST_NAMES = ['Алексей', 'Мария', 'Дмитрий', 'Анна', 'Сергей', 'Елена', 'Иван', 'Ольга', 'Михаил', 'Татьяна']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Павлов', 'Соколов',
              'Михайлов']


def init_database():
    with app.app_context():
        print("Создание таблиц...")
        db.create_all()
        print("Таблицы созданы")

        if Coffee.query.count() == 0:
            print("Инициализация базы данных...")

            try:
                response = requests.get('https://dummyjson.com/products/search?q=coffee')
                coffee_data = response.json()

                if coffee_data['products']:
                    coffee = coffee_data['products'][0]
                    reviews_comments = [review['comment'] for review in coffee.get('reviews', [])]

                    new_coffee = Coffee(
                        title=coffee['title'],
                        category=coffee['category'],
                        description=coffee['description'],
                        reviews=reviews_comments
                    )
                    db.session.add(new_coffee)
                    db.session.commit()
                    print(f"✅ Создан кофе: {coffee['title']}")

                    for i in range(10):
                        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

                        try:
                            address_response = requests.get('https://dummyjson.com/users')
                            if address_response.status_code == 200:
                                users_data = address_response.json()
                                random_user = random.choice(users_data['users'])
                                address = random_user['address']
                            else:
                                address = {'country': 'Russia', 'city': 'Moscow', 'address': 'Unknown'}
                        except Exception as e:
                            print(f"Ошибка получения адреса: {e}")
                            address = {'country': 'Russia', 'city': 'Moscow', 'address': 'Unknown'}

                        user = User(
                            name=name,
                            has_sale=random.choice([True, False]),
                            address=address,
                            coffee_id=new_coffee.id
                        )
                        db.session.add(user)

                    db.session.commit()
                    print(f"✅ Создано 10 пользователей")
                else:
                    print("❌ Не удалось получить данные о кофе из API")
            except Exception as e:
                print(f"❌ Ошибка при инициализации: {e}")

            app.config['DB_INITIALIZED'] = True
        else:
            print("✅ Данные уже существуют в базе")
            app.config['DB_INITIALIZED'] = True


with app.app_context():
    init_database()


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'API для работы с кофе и пользователями',
        'endpoints': {
            'POST /users': 'Добавить нового пользователя',
            'GET /coffee/search/<query>': 'Поиск кофе по названию',
            'GET /coffee/reviews/unique': 'Уникальные отзывы о кофе',
            'GET /users/country/<country>': 'Пользователи по стране',
            'GET /stats': 'Статистика'
        }
    })


@app.route('/users', methods=['POST'])
def add_user():
    data = request.json

    if not data or 'name' not in data:
        return jsonify({'error': 'Поле name обязательно'}), 400

    coffee_id = data.get('coffee_id')
    if not coffee_id:
        coffee = Coffee.query.first()
        coffee_id = coffee.id if coffee else None

    user = User(
        name=data['name'],
        has_sale=data.get('has_sale', False),
        address=data.get('address', {}),
        coffee_id=coffee_id
    )

    db.session.add(user)
    db.session.commit()

    result = {
        'id': user.id,
        'name': user.name,
        'has_sale': user.has_sale,
        'address': user.address,
        'coffee': {
            'id': user.coffee.id,
            'title': user.coffee.title,
            'category': user.coffee.category
        } if user.coffee else None
    }

    return jsonify(result), 201


@app.route('/coffee/search/<query>')
def search_coffee(query):
    coffees = Coffee.query.filter(
        Coffee.title.ilike(f'%{query}%')
    ).all()

    result = []
    for coffee in coffees:
        result.append({
            'id': coffee.id,
            'title': coffee.title,
            'category': coffee.category,
            'description': coffee.description,
            'reviews_count': len(coffee.reviews) if coffee.reviews else 0
        })

    return jsonify({
        'query': query,
        'count': len(result),
        'results': result
    })


@app.route('/coffee/reviews/unique')
def unique_reviews():
    result = db.session.execute(
        text("""
            SELECT DISTINCT unnest(reviews) as review
            FROM coffee
            WHERE reviews IS NOT NULL
        """)
    ).fetchall()

    unique_reviews = [row[0] for row in result]

    return jsonify({
        'count': len(unique_reviews),
        'unique_reviews': unique_reviews
    })


@app.route('/users/country/<country>')
def users_by_country(country):
    users = User.query.filter(
        User.address.op('->>')('country') == country
    ).all()

    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'has_sale': user.has_sale,
            'address': user.address,
            'coffee': {
                'id': user.coffee.id,
                'title': user.coffee.title
            } if user.coffee else None
        })

    return jsonify({
        'country': country,
        'count': len(result),
        'users': result
    })


@app.route('/stats')
def get_stats():
    total_users = User.query.count()
    total_coffee = Coffee.query.count()
    users_with_sale = User.query.filter_by(has_sale=True).count()

    country_stats = db.session.execute(
        text("""
            SELECT address->>'country' as country, COUNT(*) as count
            FROM users
            WHERE address->>'country' IS NOT NULL
            GROUP BY address->>'country'
            ORDER BY count DESC
        """)
    ).fetchall()

    recent_users = User.query.order_by(User.id.desc()).limit(5).all()

    return jsonify({
        'total_users': total_users,
        'total_coffee': total_coffee,
        'users_with_sale': users_with_sale,
        'users_by_country': [{'country': row[0], 'count': row[1]} for row in country_stats],
        'recent_users': [{'id': u.id, 'name': u.name} for u in recent_users]
    })

if __name__ == '__main__':
    print("🚀 Запуск сервера на http://localhost:5000")
    app.run(debug=True, port=5000)