from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')

# GET all rooms
@rooms_bp.route('', methods=['GET'])
def get_rooms():
    """Fetch all rooms."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Rooms
    """)
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(rooms)

# POST a new room
@rooms_bp.route('', methods=['POST'])
def add_room():
    """Add a new room to the database."""
    data = request.json
    room_number = data.get('room_number')
    capacity = data.get('capacity')
    floor = data.get('floor')
    room_type = data.get('room_type')

    if not room_number or not capacity or not floor or not room_type:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Rooms (room_number, capacity, floor, room_type)
        VALUES (%s, %s, %s, %s)
    """, (room_number, capacity, floor, room_type))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Room added successfully'}), 201

# GET a specific room
@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Fetch a specific room by its ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    cursor.close()
    connection.close()

    if not room:
        return jsonify({'error': 'Room not found'}), 404

    return jsonify(room)

# PUT update an existing room
@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """Update an existing room's details."""
    data = request.json
    room_number = data.get('room_number')
    capacity = data.get('capacity')
    floor = data.get('floor')
    room_type = data.get('room_type')

    if not room_number or not capacity or not floor or not room_type:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Rooms
        SET room_number = %s, capacity = %s, floor = %s, room_type = %s
        WHERE id = %s
    """, (room_number, capacity, floor, room_type, room_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Room not found or no changes made'}), 404

    return jsonify({'message': 'Room updated successfully'}), 200

# DELETE a room
@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Rooms WHERE id = %s", (room_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Room not found'}), 404

        return jsonify({'message': 'Room deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
