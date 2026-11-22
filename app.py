from flask import *
from student import studentbp
from admin import adminbp

app = Flask(__name__)
app.register_blueprint(studentbp)
app.register_blueprint(adminbp)

app.secret_key = "Hdgyusgfdyuwegywgeuyfgyufewgyweu"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/age3-6")
def th():
    return render_template("age3-6.html")

@app.route("/age7-12")
def seven():
    return render_template("age7-12.html")

@app.route("/age13-19")
def teen():
     return render_template("age13-19.html")


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")