from flask import Blueprint, jsonify, request, session
import mysql.connector
from config import get_db_connection

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')
# GET all teachers or the logged-in teacher's data

@teachers_bp.route('', methods=['GET'])
def get_teachers():
    """Fetch all teachers or only the logged-in teacher's details."""
    """Fetch all subjects."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Teachers
    """)
    
    subjects = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(subjects)




@teachers_bp.route('/username/<username>', methods=['GET'])
def check_username(username):
    """Check if a username is already taken."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Teachers WHERE username = %s", (username,))
    is_taken = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return jsonify({'is_taken': is_taken}), 200
    
@teachers_bp.route('', methods=['POST'])
def add_teacher():
    """Add a new teacher to the database."""
    data = request.json
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    role = data.get('role', 'simple')  

    if not username or not name or not password:
        return jsonify({'error': 'Username, name, and password are required'}), 400

    if role not in ['admin', 'simple']:
        return jsonify({'error': 'Invalid role. Must be "admin" or "simple".'}), 400

   
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        return jsonify({'error': 'Password must be at least 8 characters long, contain at least one number, and one uppercase letter.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check  ស្ទួន username
    cursor.execute("SELECT COUNT(*) FROM Teachers WHERE username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': 'Username is already taken'}), 400

    # Insert teacher into the database
    cursor.execute("""
        INSERT INTO Teachers (username, name, password, role)
        VALUES (%s, %s, %s, %s)
    """, (username, name, password, role))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Teacher added successfully'}), 201


# GET a specific teacher by ID
@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Fetch a specific teacher by ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, username, name, role FROM Teachers WHERE id = %s
    """, (teacher_id,))
    teacher = cursor.fetchone()
    cursor.close()
    connection.close()

    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    return jsonify(teacher)

# PUT update a teacher's details
@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Update a teacher's details."""
    data = request.json
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    role = data.get('role')

    if not username or not name or not password:
        return jsonify({'error': 'Username, name, and password are required'}), 400

    if role and role not in ['admin', 'simple']:
        return jsonify({'error': 'Invalid role. Must be "admin" or "simple".'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Teachers
        SET username = %s, name = %s, password = %s, role = %s
        WHERE id = %s
    """, (username, name, password, role, teacher_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Teacher not found or no changes made'}), 404

    return jsonify({'message': 'Teacher updated successfully'}), 200

@teachers_bp.route('', methods=['PUT'])
def update_teacher_role():
    """Update a teacher's role."""
    data = request.json
    teacher_id = data.get('id')
    new_role = data.get('role')

    if not teacher_id or not new_role:
        return jsonify({'error': 'Teacher ID and role are required'}), 400

    if new_role not in ['admin', 'simple']:
        return jsonify({'error': f'Invalid role: {new_role}'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Teachers
        SET role = %s
        WHERE id = %s
    """, (new_role, teacher_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Teacher not found or no changes made'}), 404

    return jsonify({'message': 'Role updated successfully'}), 200



# DELETE a teacher
@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Delete a teacher from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM Teachers WHERE id = %s
        """, (teacher_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Teacher not found'}), 404

        return jsonify({'message': 'Teacher deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500




#           login---------------
@teachers_bp.route('/login', methods=['POST'])
def login_teacher():
    """Authenticate a teacher and start a session."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, username, name, password, role FROM Teachers WHERE username = %s
    """, (username,))
    teacher = cursor.fetchone()
    cursor.close()
    connection.close()


    if not teacher:
        # If username is not found in the database
        return jsonify({'error': 'Username not registered'}), 404  # 404 for "not found"

    # If username is found, check if the password is correct
    if teacher['password'] != password:  # Assuming passwords are stored in plaintext (NOT RECOMMENDED)
        return jsonify({'error': 'Invalid password'}), 

    # Correct password comparison
    if teacher['password'] != password:  # Compare the stored password with the input
        return jsonify({'error': 'Invalid username or password'}), 401

    # Start the session and store user details
    session['teacher_id'] = teacher['id']
    session['teacher_username'] = teacher['username']
    session['teacher_name'] = teacher['name']
    session['teacher_role'] = teacher['role']

    return jsonify({'message': 'Login successful', 'user': teacher}), 200





# Logout route for teachers
@teachers_bp.route('/logout', methods=['POST'])
def logout_teacher():
    """Logout the teacher by clearing the session."""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200