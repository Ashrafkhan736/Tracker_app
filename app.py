from datetime import datetime
from flask import Flask, redirect, render_template, request
from flask_restful import Api
from tables import Description
from model import *
import os
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(current_dir, "tracker.sqlite3")
#api = Api(app)
app.app_context().push()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        user_name = request.form["username"]
        user = User(user_name=user_name)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("signin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["username"]
        user = User.query.filter(User.user_name == user_name).one()
        return redirect("/dashboard/{}".format(user.user_id))
    else:
        return render_template("login.html")


@app.route("/add/<int:uid>", methods=["GET", "POST"])
def add(uid):
    if request.method == "POST":
        tracker_name = request.form["name"]
        description = request.form["description"]
        tracker_type = request.form["tracker_type"]
        print(tracker_name, tracker_type, description, uid)
        #time = datetime.now()
        if tracker_type == "MultipleChoice":
            options = request.form["options"]
            tracker = Tracker_info(name=tracker_name,
                                   description=description, tracker_type=tracker_type, user_id=uid, options=options)
        else:
            tracker = Tracker_info(name=tracker_name,
                                   description=description, tracker_type=tracker_type, user_id=uid)
        db.session.add(tracker)
        db.session.commit()
        return redirect("/dashboard/{}".format(uid))


@app.route("/dashboard/<int:uid>", methods=["GET", "POST"])
def dashboard(uid):
    if request.method == "GET":
        user = User.query.filter(User.user_id == uid).one()
        print(user.trackers)
        return render_template("dashboard.html", user=user, trackers=user.trackers)


@app.route("/log/<int:tid>", methods=["GET", "POST"])
def log(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    if request.method == "GET":
        return render_template("addnumericallog.html", tracker=tracker)
    else:
        value = request.form["value"]
        note = request.form["note"]
        if tracker.tracker_type == "MultipleChoice":
            log = Mcq_log(value=value, note=note, tracker_id=tid)
        else:
            log = Numerical_log(value=value, note=note, tracker_id=tid)
        db.session.add(log)
        db.session.commit()
        return redirect("/dashboard/{}".format(tracker.user_id))


@app.route("/view/<int:tid>")
def view(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    if tracker.tracker_type == "Numerical":
        return render_template("log.html", tracker=tracker, logs=tracker.numerical_log)
    else:
        return render_template("log.html", tracker=tracker, logs=tracker.mcq_log)


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000)