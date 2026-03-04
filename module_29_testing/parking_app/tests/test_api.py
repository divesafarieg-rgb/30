import pytest
from app.models import Client, Parking, ClientParking
from datetime import datetime


class TestClientsAPI:

    @pytest.mark.parametrize("url,expected_status", [
        ('/clients', 200),
        ('/clients/1', 200),
        ('/clients/999', 404),
    ])
    def test_get_clients_status(self, client, url, expected_status):
        response = client.get(url)
        assert response.status_code == expected_status

    def test_get_all_clients(self, client):
        response = client.get('/clients')
        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_client_by_id(self, client, test_data):
        response = client.get(f'/clients/{test_data["client_with_card"]}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['id'] == test_data["client_with_card"]
        assert data['name'] == 'Иван'
        assert data['surname'] == 'Петров'
        assert data['credit_card'] is not None
        assert data['car_number'] is not None

    @pytest.mark.parametrize("client_data,expected_status,expected_fields", [
        (
                {'name': 'Анна', 'surname': 'Сидорова'},
                201,
                ['id', 'name', 'surname']
        ),
        (
                {'name': 'Мария', 'surname': 'Иванова', 'credit_card': '1111-2222-3333-4444', 'car_number': 'M123MM'},
                201,
                ['id', 'name', 'surname', 'credit_card', 'car_number']
        ),
        (
                {'name': 'Ольга'},
                400,
                ['error']
        ),
        (
                {},
                400,
                ['error']
        ),
    ])
    def test_create_client(self, client, client_data, expected_status, expected_fields):
        response = client.post('/clients', json=client_data)
        assert response.status_code == expected_status

        data = response.get_json()
        for field in expected_fields:
            assert field in data

        if expected_status == 201:
            assert data['name'] == client_data['name']
            assert data['surname'] == client_data['surname']


class TestParkingsAPI:

    def test_create_parking(self, client, new_parking_data):
        response = client.post('/parkings', json=new_parking_data)
        assert response.status_code == 201

        data = response.get_json()
        assert data['address'] == new_parking_data['address']
        assert data['count_places'] == new_parking_data['count_places']
        assert data['opened'] == new_parking_data['opened']
        assert data['count_available_places'] == new_parking_data['count_places']
        assert 'id' in data

    @pytest.mark.parametrize("parking_data,expected_status", [
        ({'address': 'Новая парковка', 'count_places': 20}, 201),
        ({'address': 'Закрытая парковка', 'count_places': 30, 'opened': False}, 201),
        ({'address': 'Ул. Тестовая'}, 400),
        ({'count_places': 50}, 400),
        ({}, 400),
    ])
    def test_create_parking_parametrized(self, client, parking_data, expected_status):
        response = client.post('/parkings', json=parking_data)
        assert response.status_code == expected_status


@pytest.mark.parking
class TestParkingOperations:

    def test_enter_parking_success(self, client, test_data):
        enter_data = {
            'client_id': test_data['client_with_card'],
            'parking_id': test_data['parking_open']
        }

        response = client.post('/client_parkings', json=enter_data)
        assert response.status_code == 201

        data = response.get_json()
        assert data['message'] == 'Successfully entered parking'
        assert data['session']['client_id'] == test_data['client_with_card']
        assert data['session']['parking_id'] == test_data['parking_open']
        assert data['session']['time_out'] is None

    def test_enter_parking_no_places(self, client, test_data):
        new_parking = {
            'address': 'Тестовая парковка с 1 местом',
            'count_places': 1,
            'opened': True
        }
        parking_response = client.post('/parkings', json=new_parking)
        parking_id = parking_response.get_json()['id']

        client1_data = {
            'name': 'Первый',
            'surname': 'Клиент',
            'credit_card': '1111-2222-3333-4444',
            'car_number': 'CAR001'
        }
        client1_resp = client.post('/clients', json=client1_data)
        client1_id = client1_resp.get_json()['id']

        client2_data = {
            'name': 'Второй',
            'surname': 'Клиент',
            'credit_card': '5555-6666-7777-8888',
            'car_number': 'CAR002'
        }
        client2_resp = client.post('/clients', json=client2_data)
        client2_id = client2_resp.get_json()['id']

        enter1_data = {
            'client_id': client1_id,
            'parking_id': parking_id
        }
        enter1_response = client.post('/client_parkings', json=enter1_data)
        assert enter1_response.status_code == 201

        enter2_data = {
            'client_id': client2_id,
            'parking_id': parking_id
        }
        enter2_response = client.post('/client_parkings', json=enter2_data)

        assert enter2_response.status_code == 400
        assert 'No available places' in enter2_response.get_json()['error']

    def test_enter_parking_when_already_on_parking(self, client, test_data):
        enter_data = {
            'client_id': test_data['client_with_card'],
            'parking_id': test_data['parking_almost_full']
        }

        response = client.post('/client_parkings', json=enter_data)

        assert response.status_code == 400
        error_msg = response.get_json()['error']
        assert 'Client already on this parking' in error_msg

    def test_enter_closed_parking(self, client, test_data):
        enter_data = {
            'client_id': test_data['client_with_card'],
            'parking_id': test_data['parking_closed']
        }

        response = client.post('/client_parkings', json=enter_data)
        assert response.status_code == 400
        assert 'Parking is closed' in response.get_json()['error']

    def test_enter_without_car(self, client, test_data):
        enter_data = {
            'client_id': test_data['client_without_car'],
            'parking_id': test_data['parking_open']
        }

        response = client.post('/client_parkings', json=enter_data)
        assert response.status_code == 400
        assert 'Client has no car registered' in response.get_json()['error']

    def test_enter_nonexistent_client(self, client, test_data):
        enter_data = {
            'client_id': 999,
            'parking_id': test_data['parking_open']
        }

        response = client.post('/client_parkings', json=enter_data)
        assert response.status_code == 404
        assert 'Client with id 999 not found' in response.get_json()['error']

    def test_exit_parking_success(self, client, test_data):
        client_id = test_data['client_with_card']
        parking_id = test_data['parking_open']

        enter_data = {'client_id': client_id, 'parking_id': parking_id}
        enter_response = client.post('/client_parkings', json=enter_data)
        assert enter_response.status_code == 201

        exit_data = {'client_id': client_id, 'parking_id': parking_id}
        exit_response = client.delete('/client_parkings', json=exit_data)
        assert exit_response.status_code == 200

        data = exit_response.get_json()
        assert data['message'] == 'Successfully exited parking'
        assert 'cost' in data
        assert 'parking_duration' in data
        assert data['session']['time_out'] is not None

    def test_exit_without_card(self, client, test_data):
        new_client_data = {
            'name': 'Без',
            'surname': 'Карты',
            'car_number': 'TEST01'
        }
        create_response = client.post('/clients', json=new_client_data)
        assert create_response.status_code == 201
        client_without_card_id = create_response.get_json()['id']

        enter_data = {
            'client_id': client_without_card_id,
            'parking_id': test_data['parking_open']
        }
        enter_response = client.post('/client_parkings', json=enter_data)
        assert enter_response.status_code == 201

        exit_data = {
            'client_id': client_without_card_id,
            'parking_id': test_data['parking_open']
        }
        exit_response = client.delete('/client_parkings', json=exit_data)
        assert exit_response.status_code == 400
        assert 'Client has no credit card' in exit_response.get_json()['error']

    def test_exit_without_active_session(self, client, test_data):
        exit_data = {
            'client_id': test_data['client_with_card'],
            'parking_id': test_data['parking_closed']
        }

        response = client.delete('/client_parkings', json=exit_data)
        assert response.status_code == 404
        assert 'No active parking session found' in response.get_json()['error']

    def test_parking_places_count_changes(self, client, test_data):
        new_client_data = {
            'name': 'Тест',
            'surname': 'Мест',
            'credit_card': '1234-5678-9012-3456',
            'car_number': 'TEST02'
        }
        create_response = client.post('/clients', json=new_client_data)
        client_id = create_response.get_json()['id']

        parking_id = test_data['parking_open']


        enter_data = {'client_id': client_id, 'parking_id': parking_id}
        enter_response = client.post('/client_parkings', json=enter_data)
        assert enter_response.status_code == 201

        data = enter_response.get_json()
        assert 'available_places' in data

        exit_data = {'client_id': client_id, 'parking_id': parking_id}
        exit_response = client.delete('/client_parkings', json=exit_data)
        assert exit_response.status_code == 200

        data = exit_response.get_json()
        assert 'available_places' in data


class TestEdgeCases:

    def test_invalid_json(self, client):
        response = client.post('/clients', data='not json', content_type='application/json')
        assert response.status_code == 400

    def test_method_not_allowed(self, client):
        response = client.put('/clients')
        assert response.status_code == 405

    def test_nonexistent_endpoint(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404