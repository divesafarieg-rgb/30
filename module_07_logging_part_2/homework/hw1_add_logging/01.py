import logging
from utils import calculate

logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('calculator.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def main():
    logger.info("Запуск калькулятора")

    try:
        a = float(input("Введите первое число: "))
        b = float(input("Введите второе число: "))
        operation = input("Введите операцию (+, -, *, /): ")

        logger.info(f"Получены данные: a={a}, b={b}, операция='{operation}'")

        result = calculate(a, b, operation)
        logger.info(f"Результат операции: {result}")
        print(f"Результат: {result}")

    except ValueError as e:
        logger.error(f"Ошибка ввода данных: {e}")
        print("Ошибка: введите корректные числа")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Ошибка: {e}")

    logger.info("Завершение работы калькулятора")


if __name__ == "__main__":
    main()
