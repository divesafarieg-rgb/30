import pytest
from freezegun import freeze_time
from hello_word_with_day import app, GREETINGS


def test_can_get_correct_username_with_weekdate():
    test_client = app.test_client()

    with freeze_time("2024-01-01"):
        response = test_client.get('/hello-world/Иван')
        assert response.status_code == 200
        assert 'Привет, Иван. Хорошего понедельника!' in response.get_data(as_text=True)


def test_correct_weekday_for_all_days():
    test_client = app.test_client()

    test_dates = [
        ("2024-01-01", "понедельника"),
        ("2024-01-02", "вторника"),
        ("2024-01-03", "среды"),
        ("2024-01-04", "четверга"),
        ("2024-01-05", "пятницы"),
        ("2024-01-06", "субботы"),
        ("2024-01-07", "воскресенья"),
    ]

    for date, expected_day in test_dates:
        with freeze_time(date):
            response = test_client.get('/hello-world/Тест')
            response_text = response.get_data(as_text=True)
            assert f'Хорошего {expected_day}' in response_text or f'Хорошей {expected_day}' in response_text
            assert response.status_code == 200