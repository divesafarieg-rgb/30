@echo off
echo Исправляем все ошибки...

echo 1. Запускаем isort для сортировки импортов...
isort app tests

echo 2. Запускаем black для форматирования...
black app tests

echo 3. Проверяем flake8...
flake8 app tests

echo 4. Проверяем mypy...
mypy app --ignore-missing-imports

echo 5. Запускаем тесты...
pytest tests/ -v

echo Готово!
pause