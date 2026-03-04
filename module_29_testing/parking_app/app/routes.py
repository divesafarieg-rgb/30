from flask import Blueprint, request, jsonify
from app import db
from app.models import Client, Parking, ClientParking
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return jsonify({
        'message': 'Parking API is running',
        'endpoints': {
            'GET /clients': 'List all clients',
            'GET /clients/<id>': 'Get client by ID',
            'POST /clients': 'Create new client',
            'POST /parkings': 'Create new parking zone',
            'POST /client_parkings': 'Enter parking',
            'DELETE /client_parkings': 'Exit parking'
        }
    })


@bp.route('/clients', methods=['GET'])
def get_clients():
    try:
        stmt = select(Client)
        clients = db.session.execute(stmt).scalars().all()
        return jsonify([client.to_dict() for client in clients]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    try:
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({'error': f'Client with id {client_id} not found'}), 404
        return jsonify(client.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@bp.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    if not data.get('surname'):
        return jsonify({'error': 'Surname is required'}), 400

    client = Client(
        name=data['name'],
        surname=data['surname'],
        credit_card=data.get('credit_card'),
        car_number=data.get('car_number')
    )

    try:
        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@bp.route('/parkings', methods=['POST'])
def create_parking():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('address'):
        return jsonify({'error': 'Address is required'}), 400
    if not data.get('count_places'):
        return jsonify({'error': 'count_places is required'}), 400

    try:
        count_places = int(data['count_places'])
        if count_places <= 0:
            return jsonify({'error': 'count_places must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'count_places must be a number'}), 400

    parking = Parking(
        address=data['address'],
        opened=data.get('opened', True),
        count_places=count_places,
        count_available_places=data.get('count_available_places', count_places)
    )

    try:
        db.session.add(parking)
        db.session.commit()
        return jsonify(parking.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@bp.route('/client_parkings', methods=['POST'])
def enter_parking():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('client_id'):
        return jsonify({'error': 'client_id is required'}), 400
    if not data.get('parking_id'):
        return jsonify({'error': 'parking_id is required'}), 400

    try:
        client = db.session.get(Client, data['client_id'])
        parking = db.session.get(Parking, data['parking_id'])

        if not client:
            return jsonify({'error': f'Client with id {data["client_id"]} not found'}), 404
        if not parking:
            return jsonify({'error': f'Parking with id {data["parking_id"]} not found'}), 404

        if not parking.opened:
            return jsonify({'error': 'Parking is closed'}), 400

        if parking.count_available_places <= 0:
            return jsonify({'error': 'No available places'}), 400

        if not client.car_number:
            return jsonify({'error': 'Client has no car registered'}), 400

        stmt = select(ClientParking).where(
            ClientParking.client_id == client.id,
            ClientParking.parking_id == parking.id,
            ClientParking.time_out == None
        )
        active_session = db.session.execute(stmt).scalar_one_or_none()

        if active_session:
            return jsonify({'error': 'Client already on this parking'}), 400

        client_parking = ClientParking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=datetime.now()
        )

        parking.count_available_places -= 1

        db.session.add(client_parking)
        db.session.commit()

        return jsonify({
            'message': 'Successfully entered parking',
            'session': client_parking.to_dict(),
            'available_places': parking.count_available_places
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500


@bp.route('/client_parkings', methods=['DELETE'])
def exit_parking():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('client_id'):
        return jsonify({'error': 'client_id is required'}), 400
    if not data.get('parking_id'):
        return jsonify({'error': 'parking_id is required'}), 400

    try:
        client = db.session.get(Client, data['client_id'])
        parking = db.session.get(Parking, data['parking_id'])

        if not client:
            return jsonify({'error': f'Client with id {data["client_id"]} not found'}), 404
        if not parking:
            return jsonify({'error': f'Parking with id {data["parking_id"]} not found'}), 404

        if not client.credit_card:
            return jsonify({'error': 'Client has no credit card for payment'}), 400

        stmt = select(ClientParking).where(
            ClientParking.client_id == client.id,
            ClientParking.parking_id == parking.id,
            ClientParking.time_out == None
        )
        active_session = db.session.execute(stmt).scalar_one_or_none()

        if not active_session:
            return jsonify({'error': 'No active parking session found'}), 404

        active_session.time_out = datetime.now()

        parking.count_available_places += 1

        parking_duration = active_session.time_out - active_session.time_in
        hours = parking_duration.total_seconds() / 3600
        cost = round(hours * 100, 2)  # 100 рублей в час

        db.session.commit()

        return jsonify({
            'message': 'Successfully exited parking',
            'parking_duration': str(parking_duration),
            'cost': f'{cost} RUB',
            'session': active_session.to_dict(),
            'available_places': parking.count_available_places
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500