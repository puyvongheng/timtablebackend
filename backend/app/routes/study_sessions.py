from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

study_sessions_bp = Blueprint('study_sessions', __name__, url_prefix='/api/study_sessions')

# GET all study sessions
@study_sessions_bp.route('', methods=['GET'])
def get_study_sessions():
    """Fetch all study sessions."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, shift_name, sessions_day, 
                   TIME_FORMAT(session_time_start, '%H:%i:%s') AS session_time_start,
                   TIME_FORMAT(session_time_end, '%H:%i:%s') AS session_time_end
            FROM study_sessions
        """)
        study_sessions = cursor.fetchall()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(study_sessions)

# POST a new study session
@study_sessions_bp.route('', methods=['POST'])
def add_study_session():
    """Add a new study session to the database."""
    data = request.json
    shift_name = data.get('shift_name')
    sessions_day = data.get('sessions_day')
    session_time_start = data.get('session_time_start')
    session_time_end = data.get('session_time_end')

    if not shift_name or not sessions_day or not session_time_start or not session_time_end:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO study_sessions (shift_name, sessions_day, session_time_start, session_time_end)
        VALUES (%s, %s, %s, %s)
    """, (shift_name, sessions_day, session_time_start, session_time_end))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Study session added successfully'}), 201

# GET a specific study session
@study_sessions_bp.route('/<int:study_session_id>', methods=['GET'])
def get_study_session(study_session_id):
    """Fetch a specific study session by its ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM study_sessions WHERE id = %s", (study_session_id,))
    study_session = cursor.fetchone()
    cursor.close()
    connection.close()

    if not study_session:
        return jsonify({'error': 'Study session not found'}), 404

    return jsonify(study_session)

# PUT update an existing study session
@study_sessions_bp.route('/<int:study_session_id>', methods=['PUT'])
def update_study_session(study_session_id):
    """Update an existing study session's details."""
    data = request.json
    shift_name = data.get('shift_name')
    sessions_day = data.get('sessions_day')
    session_time_start = data.get('session_time_start')
    session_time_end = data.get('session_time_end')

    if not shift_name or not sessions_day or not session_time_start or not session_time_end:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE study_sessions
        SET shift_name = %s, sessions_day = %s, session_time_start = %s, session_time_end = %s
        WHERE id = %s
    """, (shift_name, sessions_day, session_time_start, session_time_end, study_session_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Study session not found or no changes made'}), 404

    return jsonify({'message': 'Study session updated successfully'}), 200

# DELETE a study session
@study_sessions_bp.route('/<int:study_session_id>', methods=['DELETE'])
def delete_study_session(study_session_id):
    """Delete a study session from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM study_sessions WHERE id = %s", (study_session_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Study session not found'}), 404

        return jsonify({'message': 'Study session deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
