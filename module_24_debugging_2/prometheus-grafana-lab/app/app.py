from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
import random
import time

app = Flask(__name__)

metrics = PrometheusMetrics(app)

metrics.info('app_info', 'Моё тестовое приложение', version='1.0.0')


@app.route('/test')
@metrics.counter(
    'test_requests_total',
    'Количество запросов к /test',
    labels={
        'endpoint': lambda: '/test',
        'status': lambda resp: resp.status_code
    }
)
def test_endpoint():
    return jsonify({
        'message': 'OK',
        'timestamp': time.time()
    }), 200


@app.route('/api/data')
@metrics.counter(
    'api_requests_total',
    'Запросы к API с разными кодами ответа',
    labels={
        'endpoint': lambda: '/api/data',
        'status': lambda resp: resp.status_code
    }
)
def get_data():
    random_value = random.random()

    if random_value < 0.6:
        return jsonify({
            'status': 'success',
            'data': {'value': random.randint(1, 100)}
        }), 200
    elif random_value < 0.8:
        return jsonify({'error': 'Data not found'}), 404
    elif random_value < 0.95:
        return jsonify({'error': 'Internal server error'}), 500
    else:
        return jsonify({'error': 'Unauthorized'}), 401


@app.route('/users/<int:user_id>')
@metrics.counter(
    'user_requests_total',
    'Запросы к пользователям',
    labels={
        'user_id': lambda: request.view_args['user_id'],
        'status': lambda resp: resp.status_code
    }
)
def get_user(user_id):
    if 1 <= user_id <= 50:
        return jsonify({
            'user_id': user_id,
            'name': f'User{user_id}',
            'email': f'user{user_id}@example.com'
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)