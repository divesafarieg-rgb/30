import requests
import json

BASE_URL = "http://localhost:5000/api"


def send_jsonrpc_request(method: str, params: dict, id: int = 1):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id
    }

    print(f"📤 Отправка запроса:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    response = requests.post(BASE_URL, json=payload)

    print(f"📥 Ответ (код {response.status_code}):")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print("-" * 60)

    return response.json()


def test_all_operations():
    print("🧪 ТЕСТИРОВАНИЕ JSON-RPC КАЛЬКУЛЯТОРА")
    print("=" * 60)

    print("1. Проверка доступности сервиса:")
    send_jsonrpc_request("Calculator.ping", {})

    print("2. Получение списка доступных операций:")
    send_jsonrpc_request("Calculator.getOperations", {})

    print("3. Тестирование отдельных операций:")

    send_jsonrpc_request("Calculator.add", {"a": 10, "b": 5}, 3)

    send_jsonrpc_request("Calculator.subtract", {"a": 10, "b": 5}, 4)

    send_jsonrpc_request("Calculator.multiply", {"a": 10, "b": 5}, 5)

    send_jsonrpc_request("Calculator.divide", {"a": 10, "b": 5}, 6)

    print("4. Тестирование универсального метода calculate():")

    operations = [
        ("add", 15, 3),
        ("subtract", 15, 3),
        ("multiply", 15, 3),
        ("divide", 15, 3)
    ]

    for i, (op, a, b) in enumerate(operations, 7):
        print(f"   Операция: {op}({a}, {b})")
        send_jsonrpc_request(
            "Calculator.calculate",
            {"operation": op, "a": a, "b": b},
            i
        )

    print("5. Тестирование обработки ошибок:")

    print("   Деление на ноль:")
    send_jsonrpc_request("Calculator.divide", {"a": 10, "b": 0}, 11)

    print("   Неверная операция:")
    send_jsonrpc_request(
        "Calculator.calculate",
        {"operation": "power", "a": 2, "b": 3},
        12
    )

    print("   Недостаточно параметров:")
    send_jsonrpc_request("Calculator.add", {"a": 10}, 13)


def test_with_curl_commands():
    print("\n🔧 ПРИМЕРЫ CURL КОМАНД:")
    print("=" * 60)

    commands = [
        '''curl -X POST http://localhost:5000/api \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "method": "Calculator.ping", "params": {}, "id": 1}' ''',

        '''curl -X POST http://localhost:5000/api \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "method": "Calculator.add", "params": {"a": 7, "b": 3}, "id": 2}' ''',

        '''curl -X POST http://localhost:5000/api \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "method": "Calculator.calculate", "params": {"operation": "multiply", "a": 6, "b": 7}, "id": 3}' '''
    ]

    for cmd in commands:
        print(cmd)
        print()


if __name__ == "__main__":
    try:
        test_all_operations()
        test_with_curl_commands()

        print("\n✅ Тестирование завершено!")
        print(f"\n📚 Документация доступна по адресу: http://localhost:5000/api/browse")

    except requests.ConnectionError:
        print("\n❌ Ошибка: Сервер не запущен!")
        print("Запустите сервер командой: python calculator.py")
    except Exception as e:
        print(f"\n⚠️  Ошибка: {e}")