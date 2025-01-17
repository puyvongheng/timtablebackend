from flask import Blueprint, app, jsonify, request, flash
import mysql.connector
from config import get_db_connection

timetable_bp = Blueprint('timetable', __name__, url_prefix='/api/timetable')


# GET timetable entries and related form options (sessions, majors, teachers, rooms, subjects)

@timetable_bp.route('/filter', methods=['GET'])
def get_timetable_filter():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Extract query parameters
        major_id = request.args.get('major_id')
        batch = request.args.get('batch')
        years = request.args.get('years')
        semester = request.args.get('semester')
        generation = request.args.get('generation')
        shift_name = request.args.get('shift_name')  # New filter for shift name

        # Build the query with optional filters
        query = """
            SELECT 
                t.id, 
                t.note, 
                t.study_sessions_id, 
                t.group_student, 
                t.batch, 
                t.generation, 
                t.major_id, 
                t.teacher_id, 
                t.subject_id, 
                t.room_id,
                t.years,
                t.semester,
                ss.shift_name AS study_shift_name,  
                ss.sessions_day AS study_session_day,
                m.name AS major_name,
                ts.teacher_id AS teacher_id, 
                ts.subject_id AS subject_id,
                r.room_number AS room_number,
                sub.name AS subject_name
            FROM Timetable t
            LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
            LEFT JOIN Majors m ON t.major_id = m.id
            LEFT JOIN teacher_subjects ts ON t.teacher_id = ts.teacher_id AND t.subject_id = ts.subject_id
            LEFT JOIN Rooms r ON t.room_id = r.id
            LEFT JOIN Subjects sub ON t.subject_id = sub.id
            WHERE 1=1
        """
        
        filters = []
        if major_id:
            query += " AND t.major_id = %s"
            filters.append(major_id)
        if batch:
            query += " AND t.batch LIKE %s"
            filters.append(f"%{batch}%")
        if years:
            query += " AND t.years = %s"
            filters.append(years)
        if semester:
            query += " AND t.semester = %s"
            filters.append(semester)
        if generation:
            query += " AND t.generation LIKE %s"
            filters.append(f"%{generation}%")
        if shift_name:  # Apply the shift_name filter
            query += " AND ss.shift_name LIKE %s"
            filters.append(f"%{shift_name}%")

        cursor.execute(query, tuple(filters))
        timetable_entries = cursor.fetchall()

        return jsonify({'timetable_entries': timetable_entries})

    except Exception as e:
        app.logger.error(f"Error fetching timetable data: {e}")
        return jsonify({'error': 'An error occurred while fetching timetable data'}), 500
    finally:
        cursor.close()
        connection.close()




@timetable_bp.route('', methods=['GET'])
def get_timetable():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch timetable data with detailed error logging
        cursor.execute("""
            SELECT 
                t.id, 
                t.note, 
                t.study_sessions_id, 
                t.group_student, 
                t.batch, 
                t.generation, 
                t.major_id, 
                t.teacher_id, 
                t.subject_id, 
                t.room_id,
                        t.years,
                        t.semester,
                       
                TIME_FORMAT(session_time_start, '%H:%i:%s') AS session_time_start,
                TIME_FORMAT(session_time_end, '%H:%i:%s') AS session_time_end,
                ss.shift_name AS study_shift_name,  
                ss.sessions_day AS study_session_day,
                m.name AS major_name,
                ts.teacher_id AS teacher_id, 
                ts.subject_id AS subject_id,
                r.room_number AS room_number,
             
                sub.name AS subject_name
              
                       
            FROM Timetable t
            LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
            LEFT JOIN Majors m ON t.major_id = m.id
            LEFT JOIN teacher_subjects ts ON t.teacher_id = ts.teacher_id AND t.subject_id = ts.subject_id
            LEFT JOIN Rooms r ON t.room_id = r.id
            LEFT JOIN Subjects sub ON t.subject_id = sub.id
         
        """)
        timetable_entries = cursor.fetchall()

        return jsonify({'timetable_entries': timetable_entries})

    except Exception as e:
        # Log the exception details
        app.logger.error(f"Error fetching timetable data: {e}")
        return jsonify({'error': 'An error occurred while fetching timetable data'}), 500
    finally:
        cursor.close()
        connection.close()


from flask import current_app

@timetable_bp.route('', methods=['POST'])
def create_timetable():
    """Create a new timetable entry."""
    data = request.json
    current_app.logger.info(f"Received data: {data}")

    # Required fields
    required_fields = [ 'study_sessions_id', 'group_student', 'batch', 'generation',
                       'major_id', 'teacher_id', 'subject_id', 'room_id', 'years', 'semester']
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    errors = []
    if missing_fields:
        errors.append({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Extract fields
    note = data.get('note').strip()
    study_sessions_id = data.get('study_sessions_id')
    group_student = data.get('group_student')
    batch = data.get('batch')
    generation = data.get('generation')
    major_id = data.get('major_id')
    teacher_id = data.get('teacher_id')
    subject_id = data.get('subject_id')
    room_id = data.get('room_id')
    years = data.get('years')
    semester = data.get('semester')

    connection = get_db_connection()
    cursor = connection.cursor()


    

    try:
        cursor.execute("""
                                SELECT t.id, ss.id AS study_sessions_id, t.years, t.semester, m.name AS major_name, sub.name AS subject_name, te.name AS teacher_name
                        FROM Timetable t
                        LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
                        LEFT JOIN Majors m ON t.major_id = m.id
                        LEFT JOIN Subjects sub ON t.subject_id = sub.id
                        LEFT JOIN Teachers te ON t.teacher_id = te.id
                        WHERE t.room_id = %s AND t.study_sessions_id = %s AND t.years = %s AND t.semester = %s
        """, (room_id, study_sessions_id, years, semester))

        existing_room = cursor.fetchone()

        if existing_room:
            errors.append({
     'error': f'<strong>បន្ទប់មិនទំនេរព្រោះជាប់</strong> <br/>'
              f'<strong>Timetable ID:</strong> {existing_room[0]} '
              f'<strong>Study Session ID:</strong> {existing_room[1]} '
              f'<strong>Year:</strong> {existing_room[2]} '
              f'<strong>Semester:</strong> {existing_room[3]} <br/>'
              f'<strong>ជំនាញ:</strong> {existing_room[4]} <br/>'
              f'<strong>មុខវិជ្ជា:</strong> {existing_room[5]} <br/>'
              f'<strong>គ្រូ:</strong> {existing_room[6]} <br/>​ <hr>'
})
            


        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE teacher_id = %s AND study_sessions_id = %s AND years = %s AND Semester = %s
        """, (teacher_id, study_sessions_id, years, semester))
        

        if cursor.fetchone():
            errors.append({
                'error': f'<strong>គ្រូរមិនទំនេរ</strong> <br/>'
                        f'<strong>Teacher is already assigned for this session  គ្រូត្រូវបានចាត់តាំងរួចហើយសម្រាប់វគ្គនេះ</strong> <br/> <hr>'
            })

        # Check for group conflicts
        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE group_student = %s AND study_sessions_id = %s AND years = %s AND Semester = %s AND major_id = %s AND generation = %s 
        """, (group_student, study_sessions_id, years, semester, major_id, generation))

        if cursor.fetchone():
            errors.append({
                'error': f'<strong>ក្រុមសិស្ស</strong> <br/>'
                        f'<strong>Group is already assigned for this session within the same major​ ក្រុមត្រូវបានចាត់តាំងរួចហើយសម្រាប់វគ្គនេះនៅក្នុងផ្នែកសំខាន់ដូចគ្នា។</strong> <br/> ​<hr>'
            })




        
        # Check for existing conflicts
        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE room_id = %s AND study_sessions_id = %s AND years = %s AND Semester = %s
        """, (room_id, study_sessions_id, years, semester))
        if cursor.fetchone():
            errors.append({'error': 'Room is already booked for this session/បន្ទប់មិនទំនេ  ' }), 400

        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE teacher_id = %s AND study_sessions_id = %s AND years = %s AND Semester = %s
        """, (teacher_id, study_sessions_id, years, semester))
        if cursor.fetchone():
            errors.append({'error': 'Teacher is already assigned for this session/គ្រូរមិនទំនេរ ជាប់បង្រៀន '}), 400

    
        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE group_student = %s AND study_sessions_id = %s AND years = %s AND Semester = %s AND major_id = %s AND generation = %s 
       """, (group_student, study_sessions_id, years, semester, major_id,generation))
        if cursor.fetchone():
           errors.append({'error': 'Group is already assigned for this session within the same major/មានម៉ោងសិក្សារហើយ'}), 400
        

        # Check teacher-subject pairing
        cursor.execute("""
            SELECT * FROM teacher_subjects 
            WHERE teacher_id = %s AND subject_id = %s
        """, (teacher_id, subject_id))
        if not cursor.fetchone():
            errors.append({'error': 'This teacher and subject pair does not exist in teacher_subjects/គ្រូរ មិ​នអាច់បង្រៀនមុខវិជ្ជានេះបានទេ'}), 400

        if errors:
            return jsonify({'errors': errors}), 400

        # Insert new timetable entry
        cursor.execute("""
            INSERT INTO Timetable (
                study_sessions_id, group_student, note, batch, generation, major_id,
                teacher_id, subject_id, room_id, years, Semester
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (study_sessions_id, group_student, note, batch, generation, major_id,
              teacher_id, subject_id, room_id, years, semester))

        connection.commit()
        return jsonify({'message': 'Timetable entry created successfully/ បានបង្កើតដោយជោគជ័យ'}), 201

    except mysql.connector.Error as err:
        connection.rollback()
        current_app.logger.error(f"Error creating timetable: {err}")
        errors.append({'error': f'An error occurred : {err}'}), 500
        return jsonify({'errors': errors}), 500

    finally:
        cursor.close()
        connection.close()




@timetable_bp.route('/<int:timetable_id>', methods=['DELETE'])
def delete_timetable(timetable_id):
    """Delete a timetable entry by ID."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the timetable entry exists
        cursor.execute("SELECT * FROM Timetable WHERE id = %s", (timetable_id,))
        timetable = cursor.fetchone()

        if not timetable:
            return jsonify({'error': 'Timetable entry not found'}), 404

        # Perform the delete operation
        cursor.execute("DELETE FROM Timetable WHERE id = %s", (timetable_id,))
        connection.commit()

        return jsonify({'message': 'Timetable entry deleted successfully'}), 200

    except mysql.connector.Error as err:
        connection.rollback()
        app.logger.error(f"Error deleting timetable: {err}")
        return jsonify({'error': f'An error occurred: {err}'}), 500

    finally:
        cursor.close()
        connection.close()
