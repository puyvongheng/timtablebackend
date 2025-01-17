from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

teacher_subjects_bp = Blueprint('teacher_subjects', __name__, url_prefix='/api/teacher_subjects')

# GET all teacher-subject associations
@teacher_subjects_bp.route('', methods=['GET'])
def get_teacher_subjects():
    """Fetch all teacher-subject associations."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT Teachers.name AS teacher_name,teacher_id,subject_id, Subjects.name AS subject_name
        FROM teacher_subjects
        JOIN Teachers ON teacher_subjects.teacher_id = Teachers.id
        JOIN Subjects ON teacher_subjects.subject_id = Subjects.id
    """)
    teacher_subjects = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(teacher_subjects)

# POST a new teacher-subject association
@teacher_subjects_bp.route('', methods=['POST'])
def add_teacher_subject():
    """Assign a subject to a teacher."""
    data = request.json
    teacher_id = data.get('teacher_id')
    subject_id = data.get('subject_id')

    if not teacher_id or not subject_id:
        return jsonify({'error': 'Both teacher_id and subject_id are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO teacher_subjects (teacher_id, subject_id)
        VALUES (%s, %s)
    """, (teacher_id, subject_id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Teacher-Subject association added successfully'}), 201

# DELETE a teacher-subject association
@teacher_subjects_bp.route('', methods=['DELETE'])
def delete_teacher_subject():
    """Remove a teacher-subject association."""
    data = request.json
    teacher_id = data.get('teacher_id')
    subject_id = data.get('subject_id')

    if not teacher_id or not subject_id:
        return jsonify({'error': 'Both teacher_id and subject_id are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM teacher_subjects
        WHERE teacher_id = %s AND subject_id = %s
    """, (teacher_id, subject_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Association not found'}), 404

    return jsonify({'message': 'Teacher-Subject association deleted successfully'}), 200

