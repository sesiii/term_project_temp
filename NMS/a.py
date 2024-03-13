from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request, jsonify
from flask import request
from flask import Flask, render_template, request, jsonify
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dadi:root@localhost/ngo_management'
app.secret_key = 'your_secret_key'  # Add this line

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

def generate_uuid():
    return str(uuid.uuid4())

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), unique=True, default=generate_uuid)  # Call generate_uuid function
    name = db.Column(db.String(64), index=True)  # Removed unique=True
    age = db.Column(db.Integer)
    class_ = db.Column(db.String(64))
    school = db.Column(db.String(128))
    parental_income = db.Column(db.Float)
    help_type = db.Column(db.String(128))

    def __repr__(self):
        return '<Student {}>'.format(self.name)

    def to_dict(self):
        return {
            'id': self.id,

            'name': self.name,
            'age': self.age,
            'class': self.class_,
            'school': self.school,
            'parental_income': self.parental_income,
            'help_type': self.help_type
        }

from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from faker import Faker
import pyotp
from flask import url_for
from flask import session
fake = Faker()







@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


# @app.route('/create_student', methods=['GET', 'POST'])
# def create_student():
#     if request.method == 'POST':
#         # Generate a random name
#         random_name = fake.name()

#         # Hardcoded data for development purposes
#         data = {
#             'name': random_name,
#             'age': 15,
#             'class_': '10th Grade',
#             'school': 'XYZ High School',
#             'parental_income': 50000,
#             'help_type': 'Scholarship'
#         }
#         new_student = Student(name=data['name'], age=data['age'], class_=data['class_'], school=data['school'], parental_income=data['parental_income'], help_type=data['help_type'])        
#         db.session.add(new_student)
#         db.session.commit()
#         flash("Student created")
#         return redirect('/create_student')
#     return render_template('create_student.html')

@app.route('/', methods=['GET'])
def ngo_main():
    return render_template('ngo_main.html')

@app.route('/create_student', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        # Generate a random name
        random_name = fake.name()

        # Hardcoded data for development purposes
        data = {
            'name': random_name,
            'age': 15,
            'class_': '10th Grade',
            'school': 'XYZ High School',
            'parental_income': 50000,
            'help_type': 'Scholarship'
        }

        # # Get data from form
        # data = request.form

        new_student = Student(name=data['name'], age=data['age'], class_=data['class_'], school=data['school'], parental_income=data['parental_income'], help_type=data['help_type'])        
        db.session.add(new_student)
        db.session.commit()
        flash("Student created")
        return redirect('/create_student')
    return render_template('create_student.html')

@app.route('/students', methods=['GET'])
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Change this as needed
    students = Student.query.paginate(page=page, per_page=per_page, error_out=False)
    next_url = url_for('get_students', page=students.next_num) if students.has_next else None
    prev_url = url_for('get_students', page=students.prev_num) if students.has_prev else None
    return render_template('students.html', students=students.items, next_url=next_url, prev_url=prev_url)

@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return render_template('student.html', student=student)

@app.route('/students/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def student(id):
    if request.method == 'GET':
        # Get the student from the database
        student = Student.query.get_or_404(id)
        return render_template('student.html', student=student)
    elif request.method == 'PUT':
        data = request.get_json()
        student = Student.query.get_or_404(id)
        student.name = data['name']
        student.age = data['age']
        student.class_ = data['class_']
        student.school = data['school']
        student.parental_income = data['parental_income']
        student.help_type = data['help_type']
        db.session.commit()
        return jsonify({"message": "Student updated"}), 200
    elif request.method == 'DELETE':
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted"}), 200



    

@app.route('/students/<int:id>/update', methods=['GET', 'POST'])
def update_student(id):
    old_student = Student.query.get_or_404(id)

    if request.method == 'GET':
        # Render the update form with the old student's details
        return render_template('update_student.html', student=old_student)

    elif request.method == 'POST':
        data = request.form

        # Create a new student with the updated details
        new_student = Student(
            name=data.get('name', old_student.name),
            age=int(data.get('age', old_student.age)),
            school=data.get('school', old_student.school),
            parental_income=float(data.get('parental_income', old_student.parental_income)),
            help_type=data.get('help_type', old_student.help_type)
        )

        # Add the new student to the database
        db.session.add(new_student)

        # Delete the old student from the database
        db.session.delete(old_student)

        db.session.commit()
        return jsonify({'message': 'Student updated successfully'}), 200
  
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student account deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)


