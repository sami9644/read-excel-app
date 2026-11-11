from flask import *
from functools import wraps
from dotenv import load_dotenv
import os
import pymysql
import uuid
from gemini import run

load_dotenv()

adminbp = Blueprint('admin',__name__,url_prefix='/admin')
def db():
    conn = pymysql.connect(host='localhost',database='readdb',password='Sami@4998',user='root')
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user ID or a logged-in flag exists in the session
        if "admin" not in session:
            flash("You need to login first.", "warning")
            # Redirect to login page, appending the 'next' URL to return later
            return redirect(url_for("admin.home", next=request.url))
        # If logged in, proceed to the actual view function
        return f(*args, **kwargs)
    return decorated_function

@adminbp.route("/")
def home():
    if 'admin' in session:
        return redirect(url_for("admin.dash"))
    return render_template("admin/home.html")

@adminbp.route("/login",methods=['POST'])
def login():
    admin = request.form['admin_username']
    pass_ = request.form['admin_password']
    if admin == os.getenv('admin') and pass_ == os.getenv('password'):
        session['admin'] = admin
        return redirect(url_for("admin.dash"))
    else:
        return '<script>alert("Invalid credentials");location.href="/admin";</script>'
    
@adminbp.route("/dashboard")
@login_required
def dash():
    return render_template("admin/dash.html")

@adminbp.route("/passages")
@login_required
def passages():
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM passages")
        passages = cur.fetchall()
    return render_template('admin/passages.html',passages=passages)

@adminbp.route("/add/passage",methods=['POST'])
@login_required
def addpassage():
    level = request.form['level']
    age_range = request.form['age-range']
    title = request.form['title']
    passage = request.form['passage']
    args = (str(uuid.uuid4()),title,passage,level,age_range)
    with db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO passages(passage_id,title,passage,CEFR,age) VALUES (%s,%s,%s,%s,%s)",args)
        conn.commit()
    return '<script>alert("Passage added!");location.href="/admin"</script>'

@adminbp.route("/delete/passage/<passid>")
def deletepassage(passid):
    with db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM passages WHERE passage_id = %s",(passid,))
        conn.commit()
    return '<script>alert("Passage added!");location.href="/admin"</script>'

import json

@adminbp.route("/add/quiz/<passid>", methods=['GET', 'POST'])
@login_required
def addquiz(passid):
    if request.method == 'GET':
        with db() as conn:
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute("SELECT * FROM passages WHERE passage_id = %s", (passid,))
            data = cur.fetchone()
        return render_template("admin/quizform.html", data=data)

    elif request.method == 'POST':
        # Retrieve JSON string from hidden input
        questions_json = request.form.get('questions_json')
        
        if not questions_json:
            return '<script>alert("No questions submitted!");history.back();</script>'

        quiz_id = str(uuid.uuid4())
        
        with db() as conn:
            cur = conn.cursor()
            # Store JSON string inside the quizzes table under the question column
            cur.execute(
                "INSERT INTO quizzes (quizid, question, passage) VALUES (%s, %s, %s)",
                (quiz_id, questions_json, passid)
            )
            conn.commit()

        return '<script>alert("Quiz created successfully!");location.href="/admin/passages";</script>'
    else:
        return abort(405)

@adminbp.route("/evaluate")
def evaluate():
    query = '''
SELECT
    students.fullname,
    students.phone,
    audiorec.audioid,
    audiorec.audio,
    passages.passage,
    audiorec.feedback
FROM audiorec
JOIN students
    ON audiorec.student = students.studid
JOIN passages
    ON audiorec.passage = passages.passage_id;
    '''
    with db() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute(query)
        audios = cur.fetchall()
    return render_template('admin/evaluate.html',audios=audios)

@adminbp.route("/feedback/<audioid>",methods=['POST'])
@login_required
def addfeedback(audioid):
    sql = 'UPDATE audiorec SET feedback = %s WHERE audioid = %s'
    args = (request.form['feedback'],audioid)
    with db() as conn:
        cur = conn.cursor()
        cur.execute(sql,args)
        conn.commit()
    return '<script>alert("feedback updated!");location.href="/admin/dashboard"</script>'


@adminbp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/admin")