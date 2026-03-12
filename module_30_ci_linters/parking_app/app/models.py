from datetime import datetime
from typing import Any, Dict, Optional

from app import db


class Client(db.Model):

    __tablename__ = "client"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(50), nullable=False)
    surname: str = db.Column(db.String(50), nullable=False)
    credit_card: Optional[str] = db.Column(db.String(50), nullable=True)
    car_number: Optional[str] = db.Column(db.String(10), nullable=True)

    parkings = db.relationship("ClientParking", backref="client", lazy=True)

    def __repr__(self) -> str:
        return f"<Client {self.name} {self.surname}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "credit_card": self.credit_card,
            "car_number": self.car_number,
        }


class Parking(db.Model):

    __tablename__ = "parking"

    id: int = db.Column(db.Integer, primary_key=True)
    address: str = db.Column(db.String(100), nullable=False)
    opened: bool = db.Column(db.Boolean, default=True)
    count_places: int = db.Column(db.Integer, nullable=False)
    count_available_places: int = db.Column(db.Integer, nullable=False)

    clients = db.relationship("ClientParking", backref="parking", lazy=True)

    def __repr__(self) -> str:
        return f"<Parking {self.address}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "address": self.address,
            "opened": self.opened,
            "count_places": self.count_places,
            "count_available_places": self.count_available_places,
        }


class ClientParking(db.Model):

    __tablename__ = "client_parking"

    id: int = db.Column(db.Integer, primary_key=True)
    client_id: int = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    parking_id: int = db.Column(db.Integer, db.ForeignKey("parking.id"), nullable=False)
    time_in: datetime = db.Column(db.DateTime, default=datetime.now)
    time_out: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),)

    def __repr__(self) -> str:
        return f"<ClientParking client:{self.client_id} parking:{self.parking_id}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "parking_id": self.parking_id,
            "time_in": self.time_in.isoformat() if self.time_in else None,
            "time_out": self.time_out.isoformat() if self.time_out else None,
        }


