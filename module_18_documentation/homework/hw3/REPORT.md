# Отчет: Калькулятор JSON-RPC

## 1. Общее описание

Реализован калькулятор по спецификации **JSON-RPC 2.0**, поддерживающий базовые математические операции над двумя переменными.

**Основные характеристики:**

- Соответствие JSON-RPC 2.0 спецификации
- Поддержка операций: сложение, вычитание, умножение, деление
- Полная обработка ошибок с соответствующими HTTP кодами
- Встроенная веб-документация

## 2. Перечисление операций (enum)
from enum import Enum

class Operation(Enum):
    ADD = "add"       # Сложение: a + b
    SUBTRACT = "subtract"  # Вычитание: a - b
    MULTIPLY = "multiply"  # Умножение: a * b
    DIVIDE = "divide"      # Деление: a / b (b ≠ 0)

## 3. Основной метод API
Endpoint: POST http://localhost:5000/api
{
    "jsonrpc": "2.0",
    "method": "Calculator.calculate",
    "params": {
        "operation": "add|subtract|multiply|divide",
        "a": число,
        "b": число
    },
    "id": 1
}

## 4. Запуск
pip install flask flask-jsonrpc
python calculator.py

Документация: http://localhost:5000/api/browse
