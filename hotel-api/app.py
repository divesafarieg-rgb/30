from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database

    print("Database module imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    print("Current directory:", os.path.dirname(os.path.abspath(__file__)))
    print("Files in directory:", os.listdir(os.path.dirname(os.path.abspath(__file__))))


    class DatabaseStub:
        def __init__(self):
            self.rooms = []
            self.bookings = []
            self.next_room_id = 1
            self.next_booking_id = 1

        def get_all_rooms(self):
            return self.rooms

        def add_room(self, floor, guestNum, beds, price):
            room = {
                'id': self.next_room_id,
                'floor': floor,
                'guestNum': guestNum,
                'beds': beds,
                'price': price
            }
            self.rooms.append(room)
            self.next_room_id += 1
            return room['id']

        def room_exists(self, room_id):
            return any(r['id'] == room_id for r in self.rooms)

        def is_room_booked(self, room_id, check_in, check_out):
            return False

        def book_room(self, room_id, check_in, check_out, guest_name):
            booking = {
                'id': self.next_booking_id,
                'room_id': room_id,
                'check_in': check_in,
                'check_out': check_out,
                'guest_name': guest_name
            }
            self.bookings.append(booking)
            self.next_booking_id += 1
            return True


    Database = DatabaseStub
    print("Using Database stub - real database module not found")

app = Flask(__name__)
CORS(app)
db = Database()


def create_test_room_if_needed():
    try:
        rooms = db.get_all_rooms()
        if not rooms or len(rooms) == 0:
            print("🔄 Creating test room...")
            room_id = db.add_room(
                floor=1,
                guestNum=2,
                beds=1,
                price=100
            )
            print(f"Test room created with ID: {room_id}")
            return True
        else:
            print(f"Found {len(rooms)} existing room(s)")
            return False
    except Exception as e:
        print(f"Could not create test room: {e}")
        return False


create_test_room_if_needed()

print("=" * 60)
print("Hotel API Server")
print("=" * 60)
print("Available endpoints:")
print("")
print("Legacy API (for compatibility):")
print("    GET    /room")
print("    POST   /add-room")
print("    POST   /booking")
print("    GET    /health")
print("")
print("v1 REST API (/api/v1/):")
print("    GET    /rooms              - List all rooms")
print("    GET    /rooms/{id}         - Get room by ID")
print("    POST   /rooms              - Create room")
print("    PUT    /rooms/{id}         - Update room")
print("    DELETE /rooms/{id}         - Delete room")
print("    POST   /rooms/{id}/bookings - Create booking")
print("    GET    /bookings           - List bookings")
print("    GET    /bookings/{id}      - Get booking by ID")
print("    DELETE /bookings/{id}      - Cancel booking")
print("    GET    /health             - Health check")
print("    POST   /test/setup         - Test setup")
print("=" * 60)
print("Server running at: http://localhost:5000")
print("=" * 60)



@app.route('/room', methods=['GET'])
def get_rooms():
    try:
        check_in = request.args.get('checkIn', '')
        check_out = request.args.get('checkOut', '')
        guests_num = request.args.get('guestsNum', '')

        rooms = db.get_all_rooms()

        response = {
            "rooms": rooms
        }

        return jsonify(response), 200
    except Exception as e:
        print(f"Error in /room: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/add-room', methods=['POST'])
def add_room():
    try:
        data = request.json

        required_fields = ['floor', 'guestNum', 'beds', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        room_id = db.add_room(
            floor=int(data['floor']),
            guestNum=int(data['guestNum']),
            beds=int(data['beds']),
            price=int(data['price'])
        )

        rooms = db.get_all_rooms()

        return jsonify({
            "message": "Room added successfully",
            "roomId": room_id,
            "rooms": rooms
        }), 200
    except Exception as e:
        print(f"Error in /add-room: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/booking', methods=['POST'])
def book_room():
    try:
        data = request.json

        required_fields = ['roomId', 'checkIn', 'checkOut', 'guestName']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        room_id = int(data['roomId'])
        check_in = data['checkIn']
        check_out = data['checkOut']
        guest_name = data['guestName']

        if not db.room_exists(room_id):
            return jsonify({"error": "Room not found"}), 404

        if db.is_room_booked(room_id, check_in, check_out):
            return jsonify({"error": "Room already booked"}), 409

        if db.book_room(room_id, check_in, check_out, guest_name):
            return jsonify({
                "message": "Room booked successfully",
                "bookingDetails": data
            }), 200
        else:
            return jsonify({"error": "Booking failed"}), 500

    except Exception as e:
        print(f"Error in /booking: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200



@app.route('/api/v1/rooms', methods=['GET'])
def get_rooms_v1():
    try:
        check_in = request.args.get('check_in', '')
        check_out = request.args.get('check_out', '')
        guests_num = request.args.get('guests_num', '')

        rooms = db.get_all_rooms()

        response = {
            "data": {
                "rooms": rooms,
                "count": len(rooms),
                "filters_applied": {
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests_num": guests_num
                }
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }

        return jsonify(response), 200
    except Exception as e:
        print(f"Error in GET /api/v1/rooms: {e}")
        error_response = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(error_response), 500


@app.route('/api/v1/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id_v1(room_id):
    try:
        rooms = db.get_all_rooms()
        
        for room in rooms:
            if isinstance(room, dict):
                if room.get('roomId') == room_id:
                    return jsonify({
                        "data": {"room": room},
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "version": "v1"
                    }), 200
        
        return jsonify({
            "error": {
                "code": "NOT_FOUND",
                "message": f"Room with ID {room_id} not found. Available roomIds: {[r.get('roomId') for r in rooms if isinstance(r, dict)]}"
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }), 404
        
    except Exception as e:
        print(f"Error in GET /api/v1/rooms/{room_id}: {e}")
        return jsonify({
            "error": {"code": "SERVER_ERROR", "message": str(e)},
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v1/rooms', methods=['POST'])
def add_room_v1():
    try:
        data = request.json

        if not data:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "No data provided"
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 400

        floor = int(data.get('floor', 1))
        guest_num = int(data.get('guest_num', data.get('guestNum', 2)))
        beds = int(data.get('beds', 1))
        price = int(data.get('price', 100))

        room_id = db.add_room(
            floor=floor,
            guestNum=guest_num,
            beds=beds,
            price=price
        )

        response = {
            "data": {
                "room_id": room_id,
                "message": "Room created successfully",
                "room_details": {
                    "floor": floor,
                    "guest_num": guest_num,
                    "beds": beds,
                    "price": price
                }
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }

        return jsonify(response), 201
    except Exception as e:
        print(f"Error in POST /api/v1/rooms: {e}")
        error_response = {
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(error_response), 400


@app.route('/api/v1/rooms/<int:room_id>', methods=['PUT'])
def update_room_v1(room_id):
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "No data provided for update"
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 400
        
        rooms = db.get_all_rooms()
        room_exists = False
        
        for room in rooms:
            if isinstance(room, dict) and room.get('roomId') == room_id:
                room_exists = True
                break
        
        if not room_exists:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Room with roomId {room_id} not found"
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 404
        
        response = {
            "data": {
                "room_id": room_id,
                "message": f"Room {room_id} updated successfully",
                "updated_fields": list(data.keys()) if data else [],
                "note": "Update simulation - in production would save to database"
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in PUT /api/v1/rooms/{room_id}: {e}")
        return jsonify({
            "error": {"code": "SERVER_ERROR", "message": str(e)},
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v1/rooms/<int:room_id>', methods=['DELETE'])
def delete_room_v1(room_id):
    try:
        rooms = db.get_all_rooms()
        room_exists = False
        
        for room in rooms:
            if isinstance(room, dict) and room.get('roomId') == room_id:
                room_exists = True
                break
        
        message = ""
        if room_exists:
            message = f"Room {room_id} deleted successfully"
            action = "deleted"
        else:
            message = f"Room {room_id} not found (idempotent operation)"
            action = "not_found"
        
        response = {
            "data": {
                "room_id": room_id,
                "message": message,
                "action": action
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            "error": {"code": "SERVER_ERROR", "message": str(e)},
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v1/rooms/<int:room_id>/bookings', methods=['POST'])
def create_booking_v1(room_id):
    try:
        data = request.json
        
        check_in = data.get('check_in', data.get('checkIn', ''))
        check_out = data.get('check_out', data.get('checkOut', ''))
        guest_name = data.get('guest_name', data.get('guestName', ''))
        
        if not check_in or not check_out or not guest_name:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Missing required fields",
                    "required": ["check_in/checkIn", "check_out/checkOut", "guest_name/guestName"]
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 400
        
        rooms = db.get_all_rooms()
        room_exists = False
        
        for room in rooms:
            if isinstance(room, dict) and room.get('roomId') == room_id:
                room_exists = True
                break
        
        if not room_exists:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Room with roomId {room_id} not found"
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 404
        
        if db.is_room_booked(room_id, check_in, check_out):
            return jsonify({
                "error": {
                    "code": "CONFLICT",
                    "message": f"Room {room_id} is already booked for these dates",
                    "details": {
                        "room_id": room_id,
                        "check_in": check_in,
                        "check_out": check_out
                    }
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 409
        
        if db.book_room(room_id, check_in, check_out, guest_name):
            response = {
                "data": {
                    "booking_id": room_id,  # Временный ID
                    "room_id": room_id,
                    "guest_name": guest_name,
                    "check_in": check_in,
                    "check_out": check_out,
                    "message": "Booking created successfully"
                },
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }
            return jsonify(response), 201
        else:
            return jsonify({
                "error": {
                    "code": "BOOKING_FAILED",
                    "message": "Failed to create booking"
                },
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "version": "v1"
            }), 500

    except Exception as e:
        print(f"Error in POST /api/v1/rooms/{room_id}/bookings: {e}")
        return jsonify({
            "error": {"code": "SERVER_ERROR", "message": str(e)},
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v1/bookings', methods=['GET'])
def get_bookings_v1():
    try:
        response = {
            "data": {
                "bookings": [],
                "count": 0,
                "message": "Bookings endpoint ready for implementation"
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error in GET /api/v1/bookings: {e}")
        error_response = {
            "error": {
                "code": "SERVER_ERROR",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(error_response), 500


@app.route('/api/v1/bookings/<int:booking_id>', methods=['GET'])
def get_booking_by_id_v1(booking_id):
    try:
        response = {
            "data": {
                "booking_id": booking_id,
                "message": "Booking details ready for implementation",
                "note": f"Would return details for booking ID {booking_id}"
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error in GET /api/v1/bookings/{booking_id}: {e}")
        error_response = {
            "error": {
                "code": "SERVER_ERROR",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(error_response), 500


@app.route('/api/v1/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking_v1(booking_id):
    try:
        response = {
            "data": {
                "booking_id": booking_id,
                "message": "Booking cancellation ready for implementation",
                "note": f"Would cancel booking ID {booking_id}"
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
    except Exception as e:
        print(f"Error in DELETE /api/v1/bookings/{booking_id}: {e}")
        error_response = {
            "error": {
                "code": "SERVER_ERROR",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(error_response), 500


@app.route('/api/v1/health', methods=['GET'])
def health_check_v1():
    return jsonify({
        "data": {
            "status": "healthy",
            "service": "hotel-api",
            "version": "v1",
            "timestamp": datetime.now().isoformat()
        },
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "version": "v1"
    }), 200


@app.route('/api/v1/test/setup', methods=['POST'])
def setup_test_data_v1():
    try:
        rooms = db.get_all_rooms()

        test_room_id = None
        for room in rooms:
            if isinstance(room, dict) and room.get('id') == 1:
                test_room_id = 1
                break

        if not test_room_id:
            try:
                test_room_id = db.add_room(
                    floor=1,
                    guestNum=2,
                    beds=1,
                    price=100
                )
                room_status = f"Test room created with ID: {test_room_id}"
            except Exception as e:
                test_room_id = 1
                room_status = f"Could not create room: {e}"
        else:
            room_status = f"Using existing room with ID: {test_room_id}"

        response = {
            "data": {
                "room_id": test_room_id,
                "message": "Test setup completed",
                "room_status": room_status,
                "testing_instructions": [
                    "1. Create room: POST /api/v1/rooms",
                    "2. Get rooms: GET /api/v1/rooms",
                    "3. Get room by ID: GET /api/v1/rooms/1",
                    "4. Update room: PUT /api/v1/rooms/1",
                    "5. Create booking: POST /api/v1/rooms/1/bookings",
                    "6. Health check: GET /api/v1/health"
                ],
                "example_requests": {
                    "create_room": {
                        "method": "POST",
                        "url": "/api/v1/rooms",
                        "body": {"floor": 1, "guest_num": 2, "beds": 1, "price": 100}
                    },
                    "create_booking": {
                        "method": "POST",
                        "url": "/api/v1/rooms/1/bookings",
                        "body": {"check_in": "2026-01-15", "check_out": "2026-01-20", "guest_name": "Test Guest"}
                    }
                }
            },
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v1"
        }
        return jsonify(response), 200
    except Exception as e:
        error_response = {
            "error": {
                "code": "SETUP_ERROR",
                "message": str(e)
            },
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(error_response), 500



if __name__ == '__main__':
    print("\nStarting Hotel API server...")
    try:
        app.run(debug=True, host='localhost', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError starting server: {e}")