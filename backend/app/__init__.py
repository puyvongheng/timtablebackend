from operator import index
from flask import Flask, render_template


from flask_cors import CORS

from app.routes.faculties import faculties_bp
from app.routes.departments import departments_bp
from app.routes.majors import majors_bp
from app.routes.timetable import timetable_bp
from app.routes.teachers import teachers_bp
from app.routes.teacher_subjects import teacher_subjects_bp
from app.routes.rooms import rooms_bp 
from app.routes.study_sessions import study_sessions_bp
from app.routes.students import students_bp
from app.routes.subjects import subjects_bp 

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Required for flash messages

    
  
  #  CORS(app)  # Allow CORS for all origins

    # Allow specific origins (production and development)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://your-production-website.com",
                "http://localhost:4200"  # Development site
            ]
        }
    })




   # Register the 'welcom' blueprint
    app.register_blueprint(faculties_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(majors_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(teacher_subjects_bp)
    app.register_blueprint(study_sessions_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(rooms_bp) 
    app.register_blueprint(subjects_bp)

    @app.route('/')
    def home():
        return "hi"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  
