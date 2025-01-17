from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

subjects_bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')







# GET all subjects
@subjects_bp.route('', methods=['GET'])
def get_subjects():
    """Fetch all subjects."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Subjects
    """)
    subjects = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(subjects)

# POST a new subject
@subjects_bp.route('', methods=['POST'])
def add_subject():
    """Add a new subject to the database."""
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Subjects (name)
        VALUES (%s)
    """, (name,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Subject added successfully'}), 201

# GET a specific subject by ID
@subjects_bp.route('/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    """Fetch a specific subject by ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Subjects WHERE id = %s
    """, (subject_id,))
    subject = cursor.fetchone()
    cursor.close()
    connection.close()

    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    return jsonify(subject)

# PUT update a subject's details
@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    """Update a subject's details."""
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Subjects
        SET name = %s
        WHERE id = %s
    """, (name, subject_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Subject not found or no changes made'}), 404

    return jsonify({'message': 'Subject updated successfully'}), 200

# DELETE a subject
@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete a subject from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM Subjects WHERE id = %s
        """, (subject_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Subject not found'}), 404

        return jsonify({'message': 'Subject deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
