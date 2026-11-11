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


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")