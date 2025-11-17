from flask import Flask, request
import subprocess
import shlex

app = Flask(__name__)


@app.route('/ps')
def ps_command():
    try:
        args: list[str] = request.args.getlist('arg')

        print("=" * 50)
        print(f"Получен запрос к /ps")
        print(f"Аргументы: {args}")
        print(f"Тип аргументов: {type(args)}")
        print(f"Все параметры запроса: {request.args}")

        if not args:
            return "<pre>Ошибка: не указаны аргументы. Используйте: /ps?arg=a&arg=u&arg=x</pre>"

        command = ["ps"] + args
        print(f"Выполняемая команда: {command}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )

        print(f"Код возврата: {result.returncode}")

        if result.returncode == 0:
            output = result.stdout
            if not output.strip():
                output = "Команда выполнена, но вывод пуст"
        else:
            output = f"Ошибка выполнения:\n{result.stderr}"

        response = f"<pre>Команда: {' '.join(command)}\n\n{output}</pre>"
        return response

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return f"<pre>Ошибка: {str(e)}</pre>"


@app.route('/')
def home():
    return '''
    <html>
        <head><title>PS Endpoint Test</title></head>
        <body>
            <h1>Тестирование endpoint /ps</h1>
            <p>Проверьте следующие ссылки:</p>
            <ul>
                <li><a href="/ps?arg=a&arg=u&arg=x">PS aux</a></li>
                <li><a href="/ps?arg=aux">PS aux (одним аргументом)</a></li>
                <li><a href="/ps?arg=-ef">PS -ef</a></li>
                <li><a href="/ps">Без аргументов</a></li>
            </ul>
        </body>
    </html>
    '''


if __name__ == '__main__':
    print("Запуск сервера...")
    print("После запуска откройте: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
