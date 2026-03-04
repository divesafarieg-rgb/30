from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    db.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

        from app.models import Client, Parking
        clients_count = Client.query.count()
        parkings_count = Parking.query.count()
        print(f"Clients in DB: {clients_count}, Parkings in DB: {parkings_count}")

    return app