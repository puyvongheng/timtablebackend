from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection

students_bp = Blueprint('students', __name__, url_prefix='/api/students')




@students_bp.route('/logout', methods=['POST'])
def logout_student():
    """Log out the student by clearing the session or token."""
    # Assuming the client handles removing the token from local storage or cookies
    return jsonify({'message': 'Logged out successfully'}), 200



@students_bp.route('/login', methods=['POST'])
def login_student():
    """Authenticate a student and return their details."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
      # Check if the username exists in the database
    cursor.execute("SELECT * FROM Students WHERE username = %s", (username,))
    student = cursor.fetchone()



    if not student:
        # If username is not found in the database
        return jsonify({'error': 'Username not registered'}), 404  # 404 for "not found" error
    
          # If username is found, check if the password is correct
    if student['password'] != password:  # Assuming passwords are stored in plaintext (NOT RECOMMENDED)
        return jsonify({'error': 'Invalid password'}), 401  # Unauthorized if the password is incorrect



    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Students WHERE username = %s AND password = %s", (username, password))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    if not student:
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful', 'user': student}), 200




@students_bp.route('', methods=['GET'])
def get_students():
    """Fetch all students with their corresponding major names, with pagination."""
    
    # Get page and pageSize from query params, set defaults if not provided
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    
    if page <= 0 or page_size <= 0:
        return jsonify({'error': 'Page and pageSize must be positive integers'}), 400
    
    offset = (page - 1) * page_size

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to get the total count of students
    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM Students
        JOIN Majors ON Students.major_id = Majors.id
    """)
    total_students = cursor.fetchone()['total_students']
    
    # Query to fetch students with pagination
    cursor.execute("""
        SELECT Students.id, Students.name AS student_name, batch, shift_name, generation, group_student, Majors.name AS major_name, Students.username
        FROM Students
        JOIN Majors ON Students.major_id = Majors.id
        LIMIT %s OFFSET %s
    """, (page_size, offset))
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        'currentPage': page,
        'pageSize': page_size,
        'totalStudents': total_students,
        'students': students
    })




@students_bp.route('', methods=['POST'])
def add_student():
    """Add a new student to the database."""
    data = request.json

    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    major_id = data.get('major_id')
    date_joined = data.get('date_joined')
    generation = data.get('generation')
    batch = data.get('batch')
    group_student = data.get('group_student')
    shift_name = data.get('shift_name') 
    
    if not username or not password or not major_id or not shift_name:
        return jsonify({'error': 'Username, password, major_id, and shift_name are required fields.'}), 400


  
    allowed_shifts = [
        'Monday-Friday Morning',
        'Monday-Friday Afternoon',
        'Monday-Friday Evening',
        'Saturday-Sunday'
    ]

    if shift_name not in allowed_shifts:
        return jsonify({'error': 'Invalid shift_name. Allowed values are: "Monday-Friday Morning", "Monday-Friday Afternoon", "Monday-Friday Evening", "Saturday-Sunday".'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if username already exists in the database
    cursor.execute("SELECT 1 FROM Students WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Username already taken, return an error response
        cursor.close()
        connection.close()
        return jsonify({'error': 'Username already taken'}), 400

    # Insert the new student into the database
    cursor.execute("""
        INSERT INTO Students (username, name, password, major_id, date_joined, generation, batch, group_student, shift_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (username, name, password, major_id, date_joined, generation, batch, group_student, shift_name))

    connection.commit()
    cursor.close()
    connection.close()


    return jsonify({'message': 'Student added successfully'}), 201



# GET a specific student
@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Fetch a specific student by their ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student)

@students_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update an existing student's details with optional fields."""
    
    data = request.json
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    major_id = data.get('major_id')
    generation = data.get('generation')
    batch = data.get('batch')
    group_student = data.get('group_student')

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Prepare the update query dynamically based on the provided fields
    update_values = []
    update_query = "UPDATE Students SET "

    if username is not None:
        update_query += "username = %s, "
        update_values.append(username)
    if name is not None:
        update_query += "name = %s, "
        update_values.append(name)
    if password is not None:
        update_query += "password = %s, "
        update_values.append(password)
    if major_id is not None:
        update_query += "major_id = %s, "
        update_values.append(major_id)
    if generation is not None:
        update_query += "generation = %s, "
        update_values.append(generation)
    if batch is not None:
        update_query += "batch = %s, "
        update_values.append(batch)
    if group_student is not None:
        update_query += "group_student = %s, "
        update_values.append(group_student)

    # Remove trailing comma and space
    update_query = update_query.rstrip(", ")

    # Ensure that at least one field is provided for update
    if not update_values:
        return jsonify({'error': 'No fields to update'}), 400

    update_query += " WHERE id = %s"
    update_values.append(student_id)

    # Execute the query and commit changes
    cursor.execute(update_query, tuple(update_values))
    connection.commit()

    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Student not found or no changes made'}), 404

    return jsonify({'message': 'Student updated successfully'}), 200


# DELETE a student
@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Students WHERE id = %s", (student_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify({'message': 'Student deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
