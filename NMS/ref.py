
from flask import Flask, render_template, flash, redirect, request, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from faker import Faker
import pyotp
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dadi:root@localhost/ngo_management'
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

def generate_uuid():
    return str(uuid.uuid4())

from sqlalchemy import DateTime

from sqlalchemy import func

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_no = db.Column(db.String(15), nullable=True)
    email_id = db.Column(db.String(255), nullable=True)
    help_type = db.Column(db.String(255), nullable=False)  # Store as comma-separated values
    donation_amount = db.Column(db.Float, nullable=True)
    donation_date = db.Column(DateTime, nullable=False, default=func.now())

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), unique=True, default=generate_uuid)
    name = db.Column(db.String(64), index=True)
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

fake = Faker()

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

from datetime import datetime, timezone
now = datetime.now(timezone.utc)
from datetime import datetime, timedelta, timezone

@app.route('/donate', methods=['GET', 'POST'])
def submit_donation():
    if request.method == 'POST':
        name = request.form.get('name')
        phone_no = request.form.get('phone_no')
        email_id = request.form.get('email_id')
        help_type = request.form.getlist('help_type')  # Get list of selected checkboxes
        donation_amount = request.form.get('donation_amount')
        
        # Check if all required fields are filled in
        if not name or not phone_no or not email_id or not help_type:
            return render_template('donate.html', error="All fields are required.")

        # Convert help_type list to comma-separated string
        help_type = ', '.join(help_type)

        if not donation_amount or donation_amount.strip() == '':
            donation_amount = None
        else:
            donation_amount = float(donation_amount)
        
        donation_date = datetime.now(timezone.utc)


        donor = Donor(name=name, phone_no=phone_no, email_id=email_id, help_type=help_type, donation_amount=donation_amount)
        db.session.add(donor)
        db.session.commit()

        return render_template('donate.html', name=name)
    else:
        return render_template('donate.html')
    

from sqlalchemy import or_, cast, Date
from datetime import datetime

@app.route('/donor_list')
def donor_list():
    # Get the selected help types and donation dates from the query parameters
    selected_help_types = request.args.getlist('help_type')
    selected_help_types = [help_type for help_type in selected_help_types if help_type]

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Start with a query that includes all donors
    query = Donor.query

    # If help types are selected, filter donors whose help_type field contains any of the selected help types
    if selected_help_types:
        query = query.filter(or_(*[Donor.help_type.like(f"%{help_type}%") for help_type in selected_help_types]))

    # If a date range is selected, filter donors whose donation_date field is within the selected range
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Donor.donation_date.between(start_date, end_date))
        except ValueError:
            pass  # Ignore invalid dates

    # Order the donors by donation_amount from highest to lowest and then by donation_date from newest to oldest
    query = query.order_by(Donor.donation_amount.desc(), Donor.donation_date.desc())

    donors = query.all()

    # Get all distinct help types for the select input
    help_types = db.session.query(Donor.help_type).distinct()

    # Render the donor_list.html template and pass the donors and help types to it
    return render_template('donor_list.html', donors=donors, help_types=help_types)



@app.route('/login', methods=['GET', 'POST'])
def login():
    ban_until = session.get('ban_until')
    if ban_until is not None:
        ban_until = datetime.strptime(ban_until, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < ban_until:
            return render_template('login.html', ban_until=ban_until)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin_username = 'admin'
        admin_password = 'admin123'

        if username == admin_username and password == admin_password:
            session.pop('login_attempts', None)
            session.pop('first_failed_login_time', None)
            session.pop('ban_until', None)
            flash('Successful login', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
            now = datetime.now(timezone.utc)

            if 'login_attempts' in session:
                session['login_attempts'] += 1
                if session['login_attempts'] > 5 and now - session['first_failed_login_time'] <= timedelta(minutes=2):
                    if 'ban_until' not in session or now >= ban_until:
                        ban_until = now + timedelta(minutes=5)
                        session['ban_until'] = ban_until.isoformat()
                    flash('Too many failed attempts. Try again in 5 minutes.', 'danger')
                    return render_template('login.html', ban_until=ban_until)
            else:
                session['login_attempts'] = 1
                session['first_failed_login_time'] = now.isoformat()

    return render_template('login.html')

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
    else:
        # Render the form for creating a new student
        return render_template('create_student.html')
    
@app.route('/students', methods=['GET'])
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page =15 # Change this as needed

    # Get search terms from query parameters
    field = request.args.get('field')
    query = request.args.get('query')

    # Filter students
    students_query = Student.query
    if field and query:
        if field == 'class':
            students_query = students_query.filter(Student.class_.like(f"%{query}%"))
        elif field == 'help_type':
            students_query = students_query.filter(Student.help_type.like(f"%{query}%"))
        elif field == 'school':
            students_query = students_query.filter(Student.school.like(f"%{query}%"))

    students = students_query.paginate(page=page, per_page=per_page, error_out=False)
    next_url = url_for('get_students', page=students.next_num) if students.has_next else None
    prev_url = url_for('get_students', page=students.prev_num) if students.has_prev else None
    return render_template('students.html', students=students.items, next_url=next_url, prev_url=prev_url)

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

