from app import db
from app.models import Client, Parking
from tests.factories import ClientFactory, ParkingFactory


class TestClientFactory:
    def test_create_client_with_factory(self, app):
        with app.app_context():
            client = ClientFactory()

            assert client.id is not None
            assert client.name is not None
            assert client.surname is not None

            db_client = db.session.get(Client, client.id)
            assert db_client is not None
            assert db_client.name == client.name

    def test_create_client_with_credit_card(self, app):
        with app.app_context():
            client = ClientFactory(has_credit_card=True)

            assert client.credit_card is not None
            assert any(c.isdigit() for c in client.credit_card)

    def test_create_client_without_credit_card(self, app):
        with app.app_context():
            client = ClientFactory(has_credit_card=False)

            assert client.credit_card is None

    def test_create_multiple_clients(self, app):
        with app.app_context():
            clients = ClientFactory.create_batch(5)

            assert len(clients) == 5
            for client in clients:
                assert client.id is not None

            total_clients = db.session.query(Client).count()
            assert total_clients >= 5

    def test_client_with_specific_data(self, app):
        with app.app_context():
            specific_data = {"name": "Петр", "surname": "Петров", "car_number": "A123BC"}

            client = ClientFactory(**specific_data)

            assert client.name == "Петр"
            assert client.surname == "Петров"
            assert client.car_number == "A123BC"


class TestParkingFactory:
    def test_create_parking_with_factory(self, app):
        with app.app_context():
            parking = ParkingFactory()

            assert parking.id is not None
            assert parking.address is not None
            assert parking.count_places > 0
            assert 0 <= parking.count_available_places <= parking.count_places

            db_parking = db.session.get(Parking, parking.id)
            assert db_parking is not None

    def test_create_multiple_parkings(self, app):
        with app.app_context():
            parkings = ParkingFactory.create_batch(3)

            assert len(parkings) == 3
            for parking in parkings:
                assert parking.id is not None
                assert parking.address is not None

            total_parkings = db.session.query(Parking).count()
            assert total_parkings >= 3

    def test_parking_places_constraint(self, app):
        with app.app_context():
            parking = ParkingFactory(count_places=50)

            assert parking.count_places == 50
            assert parking.count_available_places <= 50
            assert parking.count_available_places >= 0

    def test_parking_opened_status(self, app):
        with app.app_context():
            parking = ParkingFactory()

            assert parking.opened in [True, False]

    def test_parking_with_specific_data(self, app):
        with app.app_context():
            specific_data = {
                "address": "ул. Тестовая, 1",
                "opened": True,
                "count_places": 100,
                "count_available_places": 75,
            }

            parking = ParkingFactory(**specific_data)

            assert parking.address == "ул. Тестовая, 1"
            assert parking.opened is True
            assert parking.count_places == 100
            assert parking.count_available_places == 75


class TestIntegrationWithFactories:
    def test_create_client_and_parking(self, app):
        with app.app_context():
            client = ClientFactory(has_credit_card=True)
            parking = ParkingFactory(opened=True, count_places=10, count_available_places=5)

            assert client.id is not None
            assert parking.id is not None
            assert client.credit_card is not None
            assert parking.opened is True
            assert parking.count_available_places == 5

    def test_batch_create_with_mixed_data(self, app):
        with app.app_context():
            clients = [
                ClientFactory(has_credit_card=True),
                ClientFactory(has_credit_card=False),
                ClientFactory(name="Иван", surname="Иванов"),
            ]

            assert len(clients) == 3
            assert clients[0].credit_card is not None
            assert clients[1].credit_card is None
            assert clients[2].name == "Иван"

            parkings = [
                ParkingFactory(opened=True, count_places=50),
                ParkingFactory(opened=False, count_places=30),
                ParkingFactory(count_places=100, count_available_places=0),
            ]

            assert len(parkings) == 3
            assert parkings[0].opened is True
            assert parkings[1].opened is False
            assert parkings[2].count_available_places == 0
