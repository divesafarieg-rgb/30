import uuid
import os
import json
import threading
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template_string
from PIL import Image, ImageFilter

SMTP_USER = "test@localhost"
SMTP_HOST = "localhost"
SMTP_PASSWORD = "test"
SMTP_PORT = 1025

os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)
os.makedirs('data', exist_ok=True)


class TaskStorage:
    FILE_PATH = 'data/tasks_status.json'

    @classmethod
    def _ensure_file(cls):
        if not os.path.exists(cls.FILE_PATH):
            os.makedirs(os.path.dirname(cls.FILE_PATH), exist_ok=True)
            with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)

    @classmethod
    def load(cls):
        cls._ensure_file()
        try:
            with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @classmethod
    def save(cls, data):
        cls._ensure_file()
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def get(cls, group_id):
        return cls.load().get(group_id)

    @classmethod
    def set(cls, group_id, value):
        data = cls.load()
        data[group_id] = value
        cls.save(data)


class SubscriberStorage:
    FILE_PATH = 'data/subscribers.json'

    @classmethod
    def _ensure_file(cls):
        if not os.path.exists(cls.FILE_PATH):
            os.makedirs(os.path.dirname(cls.FILE_PATH), exist_ok=True)
            with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)

    @classmethod
    def load(cls):
        cls._ensure_file()
        try:
            with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    @classmethod
    def save(cls, data):
        cls._ensure_file()
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def add(cls, email):
        subscribers = cls.load()
        if email not in subscribers:
            subscribers.append(email)
            cls.save(subscribers)
            print(f"✅ Подписан: {email}")
            return True
        return False

    @classmethod
    def remove(cls, email):
        subscribers = cls.load()
        if email in subscribers:
            subscribers.remove(email)
            cls.save(subscribers)
            print(f"✅ Отписан: {email}")
            return True
        return False

    @classmethod
    def get_all(cls):
        return cls.load()


def blur_image(src_filename: str, dst_filename: str = None):
    if not dst_filename:
        dst_filename = f'blurred_{os.path.basename(src_filename)}'

    try:
        with Image.open(src_filename) as img:
            img.load()
            new_img = img.filter(ImageFilter.GaussianBlur(5))
            new_img.save(dst_filename)
        print(f"✅ Изображение обработано: {os.path.basename(dst_filename)}")
    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {e}")
        raise


def send_image_email(order_id, receiver, filename):
    print("\n" + "=" * 60)
    print(f"📧 ТЕСТОВАЯ ОТПРАВКА ПИСЬМА")
    print(f"📧 Кому: {receiver}")
    print(f"📧 Тема: Изображение обработано. Заказ №{order_id}")
    print(f"📧 Файл: {filename}")
    print(f"📧 Размер файла: {os.path.getsize(filename) if os.path.exists(filename) else 0} байт")
    print("=" * 60 + "\n")
    return True


def send_newsletter_email(email):
    print("\n" + "=" * 60)
    print(f"📬 ТЕСТОВАЯ РАССЫЛКА")
    print(f"📬 Кому: {email}")
    print(f"📬 Тема: Новости сервиса обработки изображений")
    print(f"📬 Содержимое: Еженедельная рассылка с новостями сервиса")
    print("=" * 60 + "\n")
    return True


def async_task(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return str(uuid.uuid4())

    return wrapper


@async_task
def process_image(image_path, email, group_id):
    try:
        output_filename = f"blurred_{uuid.uuid4()}_{os.path.basename(image_path)}"
        output_path = os.path.join('processed', output_filename)

        print(f"🖼️ Обработка: {os.path.basename(image_path)}")

        blur_image(image_path, output_path)

        send_image_email(group_id, email, output_path)

        status = TaskStorage.get(group_id)
        if status:
            status['completed'] += 1
            if status['completed'] == status['total']:
                status['status'] = 'completed'
                print(f"✅ Задача {group_id} завершена")
            TaskStorage.set(group_id, status)

        try:
            os.remove(image_path)
            print(f"🗑️ Удален оригинал: {os.path.basename(image_path)}")
        except:
            pass

        return output_path
    except Exception as e:
        print(f"❌ Ошибка обработки: {e}")
        status = TaskStorage.get(group_id)
        if status:
            status['failed'] += 1
            TaskStorage.set(group_id, status)
        return None


def process_images_group(image_paths, email):
    group_id = str(uuid.uuid4())

    TaskStorage.set(group_id, {
        'total': len(image_paths),
        'completed': 0,
        'failed': 0,
        'status': 'processing',
        'email': email,
        'created_at': datetime.now().isoformat()
    })

    print(f"🚀 Запущена задача {group_id} с {len(image_paths)} изображениями")

    for image_path in image_paths:
        process_image(image_path, email, group_id)

    return group_id


def send_weekly_newsletter():
    subscribers = SubscriberStorage.get_all()

    if not subscribers:
        print("📭 Нет подписчиков на рассылку")
        return "No subscribers"

    print(f"📬 Отправка рассылки {len(subscribers)} подписчикам")

    for email in subscribers:
        send_newsletter_email(email)

    return f"Newsletter sent to {len(subscribers)} subscribers"


class SimpleScheduler:

    def __init__(self):
        self.tasks = []
        self.running = False
        self.thread = None

    def add_weekly_task(self, task_func, day='monday', hour=10, minute=0):
        self.tasks.append({
            'func': task_func,
            'day': day.lower(),
            'hour': hour,
            'minute': minute
        })
        print(f"📅 Добавлена задача: {task_func.__name__} по {day} в {hour}:{minute:02d}")

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Планировщик задач запущен")

    def _run_scheduler(self):
        while self.running:
            now = datetime.now()

            for task in self.tasks:
                if self._should_run(task, now):
                    try:
                        print(f"🔄 Запуск задачи: {task['func'].__name__}")
                        task['func']()
                    except Exception as e:
                        print(f"❌ Ошибка в задаче: {e}")

            time.sleep(60)

    def _should_run(self, task, now):
        if now.hour != task['hour'] or now.minute != task['minute']:
            return False

        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }

        return now.weekday() == days.get(task['day'], 0)


scheduler = SimpleScheduler()
scheduler.add_weekly_task(send_weekly_newsletter, day='monday', hour=10, minute=0)
scheduler.start()

app = Flask(__name__)

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Сервис обработки изображений</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; 
            margin: 0 auto; 
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 30px; text-align: center; }
        h2 { color: #764ba2; margin: 30px 0 20px; font-size: 1.5em; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        input[type=email], input[type=file], input[type=text] { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 14px 28px; 
            border: none; 
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .message { 
            margin-top: 20px; 
            padding: 15px; 
            border-radius: 8px;
            display: none;
        }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .task-list { margin-top: 20px; }
        .task-item { 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 4px; 
            margin-bottom: 5px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Сервис обработки изображений</h1>

        <div id="statusMessage" class="message"></div>

        <h2>🎨 Загрузить изображения</h2>
        <form id="uploadForm" onsubmit="uploadImages(event)">
            <div class="form-group">
                <label>📧 Email для получения результата:</label>
                <input type="email" id="email" required placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>🖼️ Выберите изображения:</label>
                <input type="file" id="images" multiple accept="image/*" required>
            </div>
            <button type="submit">Загрузить и обработать</button>
        </form>

        <h2>📬 Подписка на рассылку</h2>
        <form id="subscribeForm" onsubmit="subscribe(event)">
            <div class="form-group">
                <input type="email" id="subscribeEmail" placeholder="your@email.com" required>
            </div>
            <button type="submit">Подписаться</button>
        </form>

        <h2>📭 Отписка от рассылки</h2>
        <form id="unsubscribeForm" onsubmit="unsubscribe(event)">
            <div class="form-group">
                <input type="email" id="unsubscribeEmail" placeholder="your@email.com" required>
            </div>
            <button type="submit">Отписаться</button>
        </form>

        <h2>📊 Проверить статус</h2>
        <form id="statusForm" onsubmit="checkStatusById(event)">
            <div class="form-group">
                <input type="text" id="taskId" placeholder="Введите ID задачи" required>
            </div>
            <button type="submit">Проверить статус</button>
        </form>

        <h2>📋 Активные задачи</h2>
        <button onclick="loadTasks()" style="margin-bottom: 10px;">Обновить список</button>
        <div id="taskList" class="task-list"></div>
    </div>

    <script>
        function showMessage(message, type = 'success') {
            const msgDiv = document.getElementById('statusMessage');
            msgDiv.textContent = message;
            msgDiv.className = `message ${type}`;
            msgDiv.style.display = 'block';
            setTimeout(() => { msgDiv.style.display = 'none'; }, 5000);
        }

        async function uploadImages(event) {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const files = document.getElementById('images').files;

            if (!email || files.length === 0) {
                showMessage('Заполните все поля!', 'error');
                return;
            }

            if (!email.includes('@')) {
                showMessage('Введите корректный email!', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('email', email);
            for (let file of files) {
                formData.append('images', file);
            }

            try {
                const response = await fetch('/blur', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(`✅ ${data.message}. ID: ${data.task_id}`, 'success');
                    checkStatus(data.task_id);
                } else {
                    showMessage(`❌ Ошибка: ${data.error}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Ошибка соединения: ${error}`, 'error');
            }
        }

        async function subscribe(event) {
            event.preventDefault();
            const email = document.getElementById('subscribeEmail').value;

            if (!email.includes('@')) {
                showMessage('Введите корректный email!', 'error');
                return;
            }

            try {
                const response = await fetch('/subscribe', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email})
                });

                const data = await response.json();
                showMessage(data.message, response.ok ? 'success' : 'info');
                if (response.ok) {
                    document.getElementById('subscribeEmail').value = '';
                }
            } catch (error) {
                showMessage(`❌ Ошибка: ${error}`, 'error');
            }
        }

        async function unsubscribe(event) {
            event.preventDefault();
            const email = document.getElementById('unsubscribeEmail').value;

            if (!email.includes('@')) {
                showMessage('Введите корректный email!', 'error');
                return;
            }

            try {
                const response = await fetch('/unsubscribe', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email})
                });

                const data = await response.json();
                showMessage(data.message, response.ok ? 'success' : 'info');
                if (response.ok) {
                    document.getElementById('unsubscribeEmail').value = '';
                }
            } catch (error) {
                showMessage(`❌ Ошибка: ${error}`, 'error');
            }
        }

        async function checkStatus(taskId) {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/status/${taskId}`);
                    const data = await response.json();

                    if (data.status === 'completed') {
                        showMessage(`✅ Все изображения обработаны! Проверьте почту.`, 'success');
                        clearInterval(interval);
                        loadTasks();
                    }
                } catch (error) {
                    console.error('Status check error:', error);
                }
            }, 2000);
        }

        async function checkStatusById(event) {
            event.preventDefault();
            const taskId = document.getElementById('taskId').value;

            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();

                if (response.ok) {
                    showMessage(`Статус: ${data.status}, Прогресс: ${data.progress}`, 'info');
                } else {
                    showMessage(`Задача не найдена`, 'error');
                }
            } catch (error) {
                showMessage(`Ошибка: ${error}`, 'error');
            }
        }

        async function loadTasks() {
            try {
                const response = await fetch('/tasks');
                const data = await response.json();

                const taskList = document.getElementById('taskList');
                taskList.innerHTML = '';

                const tasks = data.tasks || {};
                const taskIds = Object.keys(tasks);

                if (taskIds.length === 0) {
                    taskList.innerHTML = '<p>Нет активных задач</p>';
                    return;
                }

                taskIds.slice(0, 5).forEach(taskId => {
                    const task = tasks[taskId];
                    const taskDiv = document.createElement('div');
                    taskDiv.className = 'task-item';
                    taskDiv.innerHTML = `
                        <strong>ID:</strong> ${taskId}<br>
                        <strong>Статус:</strong> ${task.status}<br>
                        <strong>Прогресс:</strong> ${task.completed}/${task.total}<br>
                        <strong>Email:</strong> ${task.email}<br>
                        <hr style="margin: 5px 0;">
                    `;
                    taskList.appendChild(taskDiv);
                });
            } catch (error) {
                console.error('Error loading tasks:', error);
            }
        }

        // Загружаем список задач при загрузке страницы
        window.onload = function() {
            loadTasks();
        };
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)


@app.route('/blur', methods=['POST'])
def blur_images():
    if 'images' not in request.files:
        return jsonify({'error': 'Изображения не загружены'}), 400

    email = request.form.get('email')
    if not email:
        return jsonify({'error': 'Email обязателен'}), 400

    files = request.files.getlist('images')
    image_paths = []

    if len(files) == 0 or files[0].filename == '':
        return jsonify({'error': 'Не выбраны файлы'}), 400

    for file in files:
        if file.filename:
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                return jsonify({'error': f'Файл {file.filename} не является изображением'}), 400

            filename = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join('uploads', filename)
            file.save(path)
            image_paths.append(path)

    group_id = process_images_group(image_paths, email)

    return jsonify({
        'task_id': group_id,
        'message': f'Начата обработка {len(image_paths)} изображений',
        'status_url': f'/status/{group_id}'
    }), 202


@app.route('/status/<group_id>')
def get_status(group_id):
    status = TaskStorage.get(group_id)

    if not status:
        return jsonify({'error': 'Задача не найдена'}), 404

    progress = f"{status['completed']}/{status['total']}"
    percent = (status['completed'] / status['total']) * 100 if status['total'] > 0 else 0

    return jsonify({
        'progress': progress,
        'percent': percent,
        'status': status['status'],
        'completed': status['completed'],
        'total': status['total'],
        'failed': status.get('failed', 0)
    })


@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email') if data else request.form.get('email')

        if not email:
            return jsonify({'error': 'Email обязателен'}), 400

        if SubscriberStorage.add(email):
            return jsonify({'message': f'✅ {email} успешно подписан на рассылку'}), 200
        else:
            return jsonify({'message': f'ℹ️ {email} уже подписан на рассылку'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        data = request.get_json()
        email = data.get('email') if data else request.form.get('email')

        if not email:
            return jsonify({'error': 'Email обязателен'}), 400

        if SubscriberStorage.remove(email):
            return jsonify({'message': f'✅ {email} отписан от рассылки'}), 200
        else:
            return jsonify({'message': f'❌ {email} не найден в подписках'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test-newsletter', methods=['POST'])
def test_newsletter():
    try:
        result = send_weekly_newsletter()
        return jsonify({'message': 'Рассылка запущена', 'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/subscribers', methods=['GET'])
def list_subscribers():
    subscribers = SubscriberStorage.get_all()
    return jsonify({'subscribers': subscribers, 'count': len(subscribers)}), 200


@app.route('/tasks', methods=['GET'])
def list_tasks():
    tasks = TaskStorage.load()
    return jsonify({'tasks': tasks}), 200


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("✅ СЕРВИС ОБРАБОТКИ ИЗОБРАЖЕНИЙ ЗАПУЩЕН")
    print("=" * 60)
    print("\n📧 ТЕСТОВЫЙ РЕЖИМ ОТПРАВКИ ПИСЕМ")
    print("   Письма выводятся в консоль, не отправляются реально")
    print("\n📁 Структура папок:")
    print("   📂 'data' - хранилище данных")
    print("   📂 'uploads' - загруженные файлы")
    print("   📂 'processed' - обработанные файлы")
    print("\n🌐 Откройте в браузере: http://localhost:5000")
    print("\n🔧 Тестовые endpoints:")
    print("   GET  /subscribers - список подписчиков")
    print("   GET  /tasks - список задач")
    print("   POST /test-newsletter - тестовая рассылка")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000)