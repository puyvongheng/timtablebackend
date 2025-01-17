from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

majors_bp = Blueprint('majors', __name__, url_prefix='/api/majors')

# GET all majors with their corresponding department names
@majors_bp.route('', methods=['GET'])
def get_majors():
    """Fetch all majors with their corresponding department names."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT Majors.id, Majors.name AS major_name, Departments.name AS department_name,Departments_id
        FROM Majors
        JOIN Departments ON Majors.Departments_id = Departments.id
    """)

    majors = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(majors)

# POST a new major
@majors_bp.route('', methods=['POST'])
def add_major():
    """Add a new major to the database."""
    data = request.json
    name = data.get('name')
    department_id = data.get('department_id')

    if not name or not department_id:
        return jsonify({'error': 'Name and department ID are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Majors (Departments_id, name) VALUES (%s, %s)", (department_id, name))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'message': 'Major added successfully'}), 201

# PUT update an existing major
@majors_bp.route('/<int:major_id>', methods=['PUT'])
def update_major(major_id):
    """Update an existing major."""
    data = request.json
    name = data.get('name')
    department_id = data.get('department_id')

    if not name or not department_id:
        return jsonify({'error': 'Name and department ID are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Majors
        SET name = %s, Departments_id = %s
        WHERE id = %s
    """, (name, department_id, major_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Major not found or no changes made'}), 404

    return jsonify({'message': 'Major updated successfully'}), 200

# DELETE a major
@majors_bp.route('/<int:major_id>', methods=['DELETE'])
def delete_major(major_id):
    """Delete a major from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Majors WHERE id = %s", (major_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Major not found'}), 404

        return jsonify({'message': 'Major deleted successfully'}), 200

    except mysql.connector.Error as err:
        # Handle foreign key constraint errors
        if err.errno == 1451:  # Foreign key constraint fails
            return jsonify({'error': 'Cannot delete major because it is referenced by other records.'}), 400
        else:
            return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
