from tests.factories import ClientFactory, ParkingFactory


class TestDuplicateClientsAPI:
    def test_create_client_with_factory(self, app, client):
        client_data = ClientFactory.build()

        payload = {
            "name": client_data.name,
            "surname": client_data.surname,
            "credit_card": client_data.credit_card,
            "car_number": client_data.car_number,
        }

        response = client.post("/clients", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == client_data.name
        assert data["surname"] == client_data.surname
        assert "id" in data

    def test_create_client_with_factory_and_credit_card(self, app, client):
        client_data = ClientFactory.build(has_credit_card=True)

        payload = {
            "name": client_data.name,
            "surname": client_data.surname,
            "credit_card": client_data.credit_card,
            "car_number": client_data.car_number,
        }

        response = client.post("/clients", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["credit_card"] is not None

    def test_create_client_with_factory_without_credit_card(self, app, client):
        client_data = ClientFactory.build(has_credit_card=False)

        payload = {
            "name": client_data.name,
            "surname": client_data.surname,
            "credit_card": client_data.credit_card,
            "car_number": client_data.car_number,
        }

        response = client.post("/clients", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["credit_card"] is None

    def test_create_multiple_clients_with_factory(self, app, client):
        clients_data = ClientFactory.build_batch(3)

        for client_data in clients_data:
            payload = {
                "name": client_data.name,
                "surname": client_data.surname,
                "credit_card": client_data.credit_card,
                "car_number": client_data.car_number,
            }

            response = client.post("/clients", json=payload)
            assert response.status_code == 201

        response = client.get("/clients")
        assert len(response.get_json()) >= 3


class TestDuplicateParkingsAPI:
    def test_create_parking_with_factory(self, app, client):
        parking_data = ParkingFactory.build()

        payload = {
            "address": parking_data.address,
            "count_places": parking_data.count_places,
            "opened": parking_data.opened,
        }

        response = client.post("/parkings", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["address"] == parking_data.address
        assert data["count_places"] == parking_data.count_places
        assert data["opened"] == parking_data.opened
        assert data["count_available_places"] == parking_data.count_places
        assert "id" in data

    def test_create_closed_parking_with_factory(self, app, client):
        parking_data = ParkingFactory.build(opened=False)

        payload = {
            "address": parking_data.address,
            "count_places": parking_data.count_places,
            "opened": parking_data.opened,
        }

        response = client.post("/parkings", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["opened"] is False

    def test_create_parking_with_small_capacity(self, app, client):
        parking_data = ParkingFactory.build(count_places=5)

        payload = {
            "address": parking_data.address,
            "count_places": parking_data.count_places,
            "opened": parking_data.opened,
        }

        response = client.post("/parkings", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["count_places"] == 5

    def test_create_multiple_parkings_with_factory(self, app, client):
        parkings_data = ParkingFactory.build_batch(3)

        for parking_data in parkings_data:
            payload = {
                "address": parking_data.address,
                "count_places": parking_data.count_places,
                "opened": parking_data.opened,
            }

            response = client.post("/parkings", json=payload)
            assert response.status_code == 201
