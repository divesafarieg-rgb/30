import factory
from factory.faker import Faker
from app import db
from app.models import Client, Parking
import random


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = Faker('first_name', locale='ru_RU')

    surname = Faker('last_name', locale='ru_RU')

    credit_card = factory.Maybe(
        'has_credit_card',
        yes_declaration=Faker('credit_card_number', card_type='visa'),
        no_declaration=None
    )

    car_number = factory.Sequence(lambda n: f'CAR{n:03d}')

    class Params:
        has_credit_card = factory.Trait(
            credit_card=factory.Faker('credit_card_number', card_type='visa')
        )


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    address = Faker('address', locale='ru_RU')

    opened = Faker('boolean', chance_of_getting_true=70)

    count_places = Faker('random_int', min=10, max=200)

    count_available_places = factory.LazyAttribute(
        lambda o: random.randint(0, o.count_places)
    )