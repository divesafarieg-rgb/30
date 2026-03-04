import pytest
import tempfile
import os
from app import create_app, db
from app.models import Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.fixture(scope='function')
def app():
    db_fd, db_path = tempfile.mkstemp()

    class TestConfig:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        TESTING = True
        SECRET_KEY = 'test-key'

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        client1 = Client(
            name='Иван',
            surname='Петров',
            credit_card='1234-5678-9012-3456',
            car_number='A123BC'
        )
        db.session.add(client1)

        client2 = Client(
            name='Петр',
            surname='Иванов',
            credit_card=None,
            car_number='B456CD'
        )
        db.session.add(client2)

        client3 = Client(
            name='Сергей',
            surname='Сидоров',
            credit_card='1111-2222-3333-4444',
            car_number=None
        )
        db.session.add(client3)

        parking1 = Parking(
            address='ул. Ленина, 10',
            opened=True,
            count_places=50,
            count_available_places=50
        )
        db.session.add(parking1)

        parking2 = Parking(
            address='ул. Пушкина, 20',
            opened=False,
            count_places=30,
            count_available_places=30
        )
        db.session.add(parking2)

        parking3 = Parking(
            address='ул. Гоголя, 15',
            opened=True,
            count_places=5,
            count_available_places=1
        )
        db.session.add(parking3)

        active_session = ClientParking(
            client_id=1,
            parking_id=3,
            time_in=datetime.now() - timedelta(hours=2),
            time_out=None
        )
        db.session.add(active_session)

        completed_session = ClientParking(
            client_id=2,
            parking_id=1,
            time_in=datetime.now() - timedelta(hours=3),
            time_out=datetime.now() - timedelta(hours=1)
        )
        db.session.add(completed_session)

        db.session.commit()

        app.test_data = {
            'client_with_card': 1,
            'client_without_card': 2,
            'client_without_car': 3,
            'parking_open': 1,
            'parking_closed': 2,
            'parking_almost_full': 3,
            'active_session_id': 1
        }

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        import time
        time.sleep(0.1)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture
def test_data(app):
    return app.test_data


@pytest.fixture
def new_client_data():
    return {
        'name': 'Новый',
        'surname': 'Клиент',
        'credit_card': '9999-8888-7777-6666',
        'car_number': 'H123OP'
    }


@pytest.fixture
def new_parking_data():
    return {
        'address': 'Тестовая улица, 1',
        'count_places': 100,
        'opened': True
    }