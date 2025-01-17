from flask import Blueprint, jsonify, request
import mysql
from config import get_db_connection

faculties_bp = Blueprint('faculties', __name__, url_prefix='/api/faculties')

# GET all faculties
@faculties_bp.route('', methods=['GET'])
def get_faculties():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Faculties")
    faculties = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(faculties)

# POST a new faculty
@faculties_bp.route('', methods=['POST'])
def add_faculty():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Faculties (name) VALUES (%s)", (name,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Faculty added successfully'}), 201

# GET a specific faculty
@faculties_bp.route('/<int:faculty_id>', methods=['GET'])
def get_faculty(faculty_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Faculties WHERE id = %s", (faculty_id,))
    faculty = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    return jsonify(faculty)

# PUT update a faculty
@faculties_bp.route('/<int:faculty_id>', methods=['PUT'])
def update_faculty(faculty_id):
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Faculties SET name = %s WHERE id = %s", (name, faculty_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Faculty not found or no changes made'}), 404
    
    return jsonify({'message': 'Faculty updated successfully'}), 200

# DELETE a faculty
@faculties_bp.route('/<int:faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Faculties WHERE id = %s", (faculty_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Faculty not found'}), 404

        return jsonify({'message': 'Faculty deleted successfully'}), 200

    except mysql.connector.Error as err:
        # Handle specific MySQL errors (e.g., foreign key constraint failure)
        if err.errno == 1451:  # Foreign key constraint fails
            return jsonify({'error': 'Cannot delete faculty because it is referenced by other records.'}), 400
        else:
            return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
