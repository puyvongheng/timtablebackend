CREATE DATABASE timetable; -- បង្កើតមូលដ្ឋានទិន្នន័យឈ្មោះ timetable
USE timetable; -- ជ្រើសរើសមូលដ្ឋានទិន្នន័យ timetable

CREATE TABLE Faculties (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    name VARCHAR(255) NOT NULL -- ឈ្មោះមហាវិទ្យាល័យ
);

CREATE TABLE Departments (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    Faculties_id INT, -- លេខសម្គាល់មហាវិទ្យាល័យ
    name VARCHAR(255) NOT NULL, -- ឈ្មោះដេប៉ាតឺម៉ង់
    FOREIGN KEY (Faculties_id) REFERENCES Faculties(id) -- តភ្ជាប់ទៅ Faculties
);

CREATE TABLE Majors (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    Departments_id INT, -- លេខសម្គាល់ដេប៉ាតឺម៉ង់
    name VARCHAR(255) NOT NULL, -- ឈ្មោះជំនាញ
    FOREIGN KEY (Departments_id) REFERENCES Departments(id) -- តភ្ជាប់ទៅ Departments
);

CREATE TABLE Teachers (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    username VARCHAR(255) NOT NULL, -- ឈ្មោះគណនី
    name VARCHAR(255) NOT NULL, -- ឈ្មោះគ្រូបង្រៀន
    password VARCHAR(255) NOT NULL -- ពាក្យសម្ងាត់
);

CREATE TABLE Subjects (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    name VARCHAR(255) NOT NULL -- ឈ្មោះមុខវិជ្ជា
);

CREATE TABLE teacher_subjects (
    teacher_id INT, -- លេខសម្គាល់គ្រូបង្រៀន
    subject_id INT, -- លេខសម្គាល់មុខវិជ្ជា
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id), -- តភ្ជាប់ទៅ Teachers
    FOREIGN KEY (subject_id) REFERENCES Subjects(id), -- តភ្ជាប់ទៅ Subjects
    PRIMARY KEY (teacher_id, subject_id) -- លេខសម្គាល់ Primary Key រួម
);

CREATE TABLE Rooms (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    room_number VARCHAR(20) NOT NULL, -- លេខបន្ទប់
    capacity INT, -- សមត្ថភាពបន្ទប់
    floor VARCHAR(10), -- ជាន់ដែលបន្ទប់ស្ថិតនៅ
    room_type ENUM('Laboratory', 'Lecture Hall', 'Classroom') DEFAULT 'Classroom' -- ប្រភេទបន្ទប់
);



CREATE TABLE study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY, -- លេខសម្គាល់ (Primary Key)
    shift_name ENUM(
        'Monday-Friday Morning',
        'Monday-Friday Afternoon',
        'Monday-Friday Evening',
        'Saturday-Sunday'
    ) NOT NULL,
    sessions_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL, -- ថ្ងៃសិក្សា
    session_time_start TIME, -- ម៉ោងចាប់ផ្តើម
    session_time_end TIME -- ម៉ោងបញ្ចប់
);

CREATE TABLE Students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    date_joined DATE,
    major_id INT,
    generation INT,
    batch INT,
    group_student INT,
    FOREIGN KEY (major_id) REFERENCES Majors(id)
);


CREATE TABLE Timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note VARCHAR(255),
    study_sessions_id INT,
    group_student INT,
    batch INT,
    generation INT,
    major_id INT,
    teacher_id INT,
    subject_id INT,
    room_id INT,
    FOREIGN KEY (study_sessions_id) REFERENCES study_sessions(id),
    FOREIGN KEY (major_id) REFERENCES Majors(id),
    FOREIGN KEY (teacher_id, subject_id) REFERENCES teacher_subjects(teacher_id, subject_id),
    FOREIGN KEY (room_id) REFERENCES Rooms(id)
);


-- Insert data into Faculties
INSERT INTO Faculties (name) VALUES 
('Engineering'),
('Science'),
('Business');

-- Insert data into Departments
INSERT INTO Departments (Faculties_id, name) VALUES
(1, 'Computer Science'),
(1, 'Electrical Engineering'),
(2, 'Biology'),
(3, 'Management');

-- Insert data into Majors
INSERT INTO Majors (Departments_id, name) VALUES
(1, 'Software Engineering'),
(1, 'Information Systems'),
(2, 'Electrical Power'),
(3, 'Business Administration');

-- Insert data into Teachers
INSERT INTO Teachers (username, name, password) VALUES
('jdoe', 'John Doe', 'password123'),
('asmith', 'Alice Smith', 'password456'),
('bmiller', 'Bob Miller', 'password789');

-- Insert data into Subjects
INSERT INTO Subjects (name) VALUES
('Mathematics'),
('Physics'),
('Computer Science'),
('Business Management');

-- Insert data into teacher_subjects
INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES
(1, 1),
(2, 2),
(1, 3),
(3, 4);

-- Insert data into Rooms
INSERT INTO Rooms (room_number, capacity, floor, room_type) VALUES
('A101', 30, '1st Floor', 'Classroom'),
('B201', 20, '2nd Floor', 'Lecture Hall'),
('C301', 15, '3rd Floor', 'Laboratory');

-- Insert data into study_sessions
INSERT INTO study_sessions (shift_name, sessions_day, session_time_start, session_time_end) VALUES
('Monday-Friday Morning', 'Monday', '08:00:00', '12:00:00'),
('Monday-Friday Afternoon', 'Tuesday', '13:00:00', '17:00:00'),
('Monday-Friday Evening', 'Wednesday', '18:00:00', '22:00:00'),
('Saturday-Sunday', 'Saturday', '09:00:00', '13:00:00');

-- Insert data into Students
INSERT INTO Students (username, name, password, date_joined, major_id, generation, batch, group_student) VALUES
('student1', 'Student One', 'password123', '2023-08-01', 1, 2023, 1, 1),
('student2', 'Student Two', 'password456', '2023-08-01', 2, 2023, 1, 1),
('student3', 'Student Three', 'password789', '2023-08-01', 3, 2023, 1, 2);

-- Insert data into Timetable
INSERT INTO Timetable (note, study_sessions_id, group_student, batch, generation, major_id, teacher_id, subject_id, room_id) VALUES
('Math class for Software Engineering', 1, 1, 1, 2023, 1, 1, 1, 1),
('Physics class for Electrical Power', 2, 1, 1, 2023, 2, 2, 2, 2),
('Computer Science class for Business Administration', 3, 2, 1, 2023, 3, 1, 3, 3),
('Business Management class for Business Administration', 4, 2, 1, 2023, 3, 3, 4, 2);


វិភាគលើកាវង្កើត timetable មិនស្តួន
គ្រូរបុខចិជ្ជា
គ្រូរម្នាក់អាចបង្រៀនច្រើនមុខវិជ្ញា
តែ បើ​ shift_name Monday-Friday Morning sessions_day Monday ម៉ោងចាប់ផ្តើម ម៉ោងបញ្ចប់
room
 study_sessions

  sessions_day
   group_student
    batch
     generation
     .
     .
     .
     .