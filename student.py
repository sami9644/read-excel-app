from flask import *
import pymysql
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from datetime import datetime
import pytz
from chapa_utils import initialize_payment,verify_payment
import os
from gemini import run
import json
import re

studentbp = Blueprint('student',__name__,url_prefix='/student')
def db():
    conn = pymysql.connect(host='localhost',database='readdb',password='Sami@4998',user='root')
    return conn

from datetime import timedelta
import pymysql

def extend_student_payment(studid, months=1):
    connection = db()
    
    days_to_add = months * 30
    
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT paiduntil FROM students WHERE studid = %s", (studid,))
            student = cursor.fetchone()
            
            if not student:
                return False, "Student not found."
            
            current_paid_until = student['paiduntil']
            today = datetime.now(pytz.timezone('Africa/Addis_Ababa')).date()
            
            if current_paid_until is None or current_paid_until < today:
                new_paid_until = today + timedelta(days=days_to_add)
            else:
                new_paid_until = current_paid_until + timedelta(days=days_to_add)
                
            cursor.execute(
                "UPDATE students SET paiduntil = %s WHERE studid = %s",
                (new_paid_until, studid)
            )
            connection.commit()
            return True
    finally:
        connection.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user ID or a logged-in flag exists in the session
        if "student" not in session:
            flash("You need to login first.", "warning")
            # Redirect to login page, appending the 'next' URL to return later
            return redirect(url_for("student.home", next=request.url))
        # If logged in, proceed to the actual view function
        return f(*args, **kwargs)
    return decorated_function

def payment_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student' not in session:
            return redirect(url_for('student.home'))
        
        studid = session['student']
        
        # Get current date in Ethiopia timezone using pytz
        tz = pytz.timezone('Africa/Addis_Ababa')
        current_date = datetime.now(tz).date()
        
        # Database connection using pymysql
        connection = db()
        
        try:
            with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT paiduntil FROM students WHERE studid = %s", (studid,))
                student = cursor.fetchone()
                
                # Check if student doesn't exist, paiduntil is NULL, or date is expired
                if not student or student['paiduntil'] is None or student['paiduntil'] < current_date:
                    flash('Your subscription has expired or is required.', 'danger')
                    return redirect(url_for('student.payment')) # Update to your payment route
        finally:
            connection.close()
            
        return f(*args, **kwargs)
    return decorated_function

def get_student_age(studid):
    with db() as conn:
        with conn.cursor(cursor=pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT birthdate FROM students WHERE studid = %s", (studid,))
            student = cur.fetchone()
            if not student or not student['birthdate']:
                return 0
            birthdate = student['birthdate']
            today = datetime.now(pytz.timezone('Africa/Addis_Ababa')).date()
            if isinstance(birthdate, str):
                birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age

def get_age_category(studid):
    age = get_student_age(studid)
    if 3 <= age <= 6:
        return "3-6"
    elif 7 <= age <= 12:
        return "7-12"
    elif 13 <= age <= 19:
        return "13-19"
    else:
        return "20+"


def getlevel(studid):
    with db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CEFR FROM students WHERE studid = %s",(studid,))
        data = cur.fetchone()
    return data[0] 

@studentbp.route("/")
def home():
    return render_template("student/index.html")

@studentbp.route("/signup",methods=['POST'])
def register():
    name = request.form['name']
    phone = request.form['phone']
    birthdate = request.form['birthdate']
    cefr_level = request.form['cefr_level']
    password = request.form['password']
    args = (str(uuid.uuid4()),name,phone,birthdate,cefr_level,generate_password_hash(password))
    with db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO students(studid,fullname,phone,birthdate,CEFR,password) VALUES(%s,%s,%s,%s,%s,%s)",args)
        conn.commit()
    return '<script>alert("Registered successfully");location.href="/student"</script>'

@studentbp.route("/signin",methods=['POST'])
def login():
    phone = request.form['phone']
    password = request.form['password']
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE phone = %s",(phone,))
        data = cur.fetchone()
    if data and check_password_hash(data['password'],password):
        session['student'] = data['studid']
        return redirect(url_for('student.dash'))
    else:
        return '<script>alert("Invalid credentials");location.href="/student"</script>'
    
# payment page
@studentbp.route("/pay",methods=['GET',"POST"])
@login_required
def payment():
    if request.method == 'GET':
        return render_template("student/payment.html")
    elif request.method == 'POST':
        txref = str(uuid.uuid4())
        amount = 500 * float(request.form['months'])
        url = f'http://127.0.0.1:5000/student/verify/{txref}/{request.form['months']}'
        checkout = initialize_payment(amount,'sami@gmail.com',txref,url,url)
        return redirect(checkout)
    else:
        return abort(405)
    
@studentbp.route("/verify/<txref>/<month>")
@login_required
def verify(txref,month):
    # txref = txref
    month = int(month)
    print(month)
    verifyp = verify_payment(txref)
    if verifyp:
        extend_student_payment(session['student'],month)
        return '<script>alert("paid successfully!");location.href="/student/dashboard"</script>'
    else:
        return '<script>alert("payment error!");location.href="/student/dashboard"</script>'

    
@studentbp.route("/dashboard")
@login_required
@payment_required
def dash():
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE studid = %s",(session['student']))
        data = cur.fetchone()
    return render_template('student/dash.html',data = data)

@studentbp.route("/passages")
@login_required
@payment_required
def passages():
    level = getlevel(session['student'])
    age_category = get_age_category(session['student'])
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM passages WHERE CEFR = %s AND age = %s", (level, age_category))
        data = cur.fetchall()
    return render_template("student/passages.html", passages=data)

@studentbp.route("/read/<passageid>")
@login_required
@payment_required
def read(passageid):
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM passages WHERE passage_id = %s",(passageid,))
        passage_data = cur.fetchone()
    return render_template('student/audio.html',data = passage_data)

@studentbp.route("/upload/<passageid>", methods=['POST'])
@login_required
@payment_required
def upload(passageid):
    recfile = request.files['audiorec']
    
    if not recfile or recfile.filename == '':
        return '<script>alert("No audio file selected!");history.back();</script>'
        
    filename = recfile.filename.split('.')
    file_extension = filename[-1] if len(filename) > 1 else 'mp3'
    
    # Construct the file path string explicitly
    audiopath = f'static/{session["student"]}.{file_extension}'
    
    # Save the file to disk using the path string
    recfile.save(audiopath)
    
    query = "INSERT INTO audiorec(audioid, audio, student, passage) VALUES(%s, %s, %s, %s)"
    args = (str(uuid.uuid4()), audiopath, session['student'], passageid)
    
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute(query, args)
        conn.commit()
        
    return '<script>alert("Audio uploaded!");location.href="/student/dashboard";</script>'


@studentbp.route("/game")
@login_required
@payment_required
def game():
    return render_template("student/forest-readers.html")

@studentbp.route("/game2")
@login_required
@payment_required
def game2():
    return render_template("student/Story Quest.html")

@studentbp.route("/changelevel",methods=['POST'])
@login_required
@payment_required
def changelevel():
    level = request.form['cefr_level']
    with db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE students SET CEFR = %s",(level,))
        conn.commit()
    return '<script>alert("level changed!");location.href="/student/dashboard";</script>'

@studentbp.route("/fillquiz/<passid>")
@login_required
@payment_required
def fillquiz(passid):
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # Fetch passage details
        cur.execute("SELECT * FROM passages WHERE passage_id = %s", (passid,))
        passage = cur.fetchone()
        
        # Fetch all generated quizzes for this passage
        cur.execute("SELECT * FROM quizzes WHERE passage = %s", (passid,))
        quizzes = cur.fetchall()

    if not passage:
        return '<script>alert("Passage not found");location.href="/student/dashboard";</script>', 404

    # Format quizzes for carousel consumption
    formatted_quizzes = []
    for q in quizzes:
        try:
            questions_data = json.loads(q['question'])
        except Exception:
            questions_data = []
            
        formatted_quizzes.append({
            "quizid": q['quizid'],
            "isevaluated": q.get('isevaluated', 'NO'),
            "questions": questions_data
        })

    return render_template("student/quiz.html", passage=passage, quizzes=formatted_quizzes)


# @studentbp.route("/evaluate/quiz/<quizid>", methods=['POST'])
# @login_required
# @payment_required
# def evaluate_quiz(quizid):
#     with db() as conn:
#         cur = conn.cursor()
#         cur.execute("UPDATE quizzes SET isevaluated = 'YES' WHERE quizid = %s", (quizid,))
#         conn.commit()
#     return jsonify({"status": "success", "message": "Quiz marked as evaluated."})

@studentbp.route("/logout")
def logout():
    session.clear()
    return redirect("/")