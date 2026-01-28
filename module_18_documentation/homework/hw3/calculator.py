from flask import Flask
from flask_jsonrpc import JSONRPC
import enum

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)


class Operations(str, enum.Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@jsonrpc.method('Calculator.calculate')
def calculate(operation: str, a: float, b: float) -> float:
    try:
        valid_operations = [op.value for op in Operations]
        if operation not in valid_operations:
            raise ValueError(
                f"Недопустимая операция '{operation}'. "
                f"Допустимые операции: {valid_operations}"
            )

        if operation == Operations.ADD:
            return float(a + b)
        elif operation == Operations.SUBTRACT:
            return float(a - b)
        elif operation == Operations.MULTIPLY:
            return float(a * b)
        elif operation == Operations.DIVIDE:
            if b == 0:
                raise ValueError("Деление на ноль недопустимо")
            return float(a / b)

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(f"Внутренняя ошибка: {str(e)}")


@jsonrpc.method('Calculator.getOperations')
def get_operations() -> list:
    return [op.value for op in Operations]


@jsonrpc.method('Calculator.ping')
def ping() -> str:
    return "pong"


@jsonrpc.method('Calculator.add')
def add(a: float, b: float) -> float:
    return float(a + b)


@jsonrpc.method('Calculator.subtract')
def subtract(a: float, b: float) -> float:
    return float(a - b)


@jsonrpc.method('Calculator.multiply')
def multiply(a: float, b: float) -> float:
    return float(a * b)


@jsonrpc.method('Calculator.divide')
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Деление на ноль недопустимо")
    return float(a / b)


if __name__ == '__main__':
    print("=" * 60)
    print("JSON-RPC Калькулятор запущен!")
    print("=" * 60)
    print("\nДоступные эндпоинты:")
    print("1. JSON-RPC API: http://localhost:5000/api")
    print("2. Документация и тестирование: http://localhost:5000/api/browse")
    print("\nПримеры запросов:")
    print("""
    Запрос сложения:
    {
        "jsonrpc": "2.0",
        "method": "Calculator.add",
        "params": {"a": 5, "b": 3},
        "id": 1
    }

    Универсальный запрос:
    {
        "jsonrpc": "2.0", 
        "method": "Calculator.calculate",
        "params": {"operation": "add", "a": 5, "b": 3},
        "id": 1
    }
    """)
    print("=" * 60)
    app.run(debug=True, port=5000)