from asyncio import tasks
from datetime import datetime
from unittest import result
from flask import Flask, redirect, render_template, request
from model import *
import os
import matplotlib.pyplot as plt
import workers
import tasks
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

db.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(current_dir, "tracker.sqlite3")

#api = Api(app)
celery = workers.celery
celery.conf.update(broker_url="redis://localhost:6379/1",
                   result_backend="redis://localhost:6379/2")
celery.Task = workers.ContextTask
app.app_context().push()


def graph(logs, ttype):
    if ttype == "Numerical":
        values = [log.value for log in logs]
        time = [log.timestamp.strftime("%d %b %H:%M") for log in logs]
        # f = plt.figure()
        # f.set_figwidth(15)
        # f.set_figheight(8)
        my_dpi = 100
        plt.figure(figsize=(1200/my_dpi, 700/my_dpi), dpi=my_dpi)
        plt.plot(time, values)
        plt.title("Trend line")
        plt.xlabel("Dates")
        plt.ylabel("Values")
        plt.xticks(rotation=30, ha='right')
        plt.savefig("./static/trendline.png", dpi=my_dpi)
        plt.close()
    else:
        values = [log.value for log in logs]
        my_dpi = 100
        plt.figure(figsize=(1200/my_dpi, 700/my_dpi), dpi=my_dpi)
        plt.hist(values,)
        plt.xlabel("Choices")
        plt.ylabel("frequency")
        plt.xticks(rotation=30, ha='right')
        plt.savefig("./static/trendline.png", dpi=my_dpi)
        plt.close()
    return


def numerical_stats(logs):
    values = [log.value for log in logs]
    return min(values), max(values), (sum(values)/len(values))


def mcq_stats(logs):
    options = {}
    for log in logs:
        options[log.value] = options.get(log.value, 0) + 1

    options_sort = sorted(options.keys(), key=lambda x: options[x])
    return options_sort[0], options_sort[-1]


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        try:
            user = User(user_name=user_name, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            return render_template("signup_error.html")
    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        try:
            user = User.query.filter(
                User.user_name == user_name).filter(User.password == password).one()

            return redirect("/dashboard/{}".format(user.user_id))
        except:
            return render_template("login_error.html")
    else:
        return render_template("login.html")


@app.route("/dashboard/<int:uid>", methods=["GET", "POST"])
def dashboard(uid):
    if request.method == "GET":
        user = User.query.filter(User.user_id == uid).one()
        print(user.trackers)
        return render_template("dashboard.html", user=user, trackers=user.trackers)


@app.route("/add_tracker/<int:uid>", methods=["GET", "POST"])
def add_tracker(uid):
    if request.method == "POST":
        tracker_name = request.form["name"]
        description = request.form["description"]
        tracker_type = request.form["tracker_type"]
        #print(tracker_name, tracker_type, description, uid)
        #time = datetime.now()
        try:
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
        except:
            return render_template("tracker_error.html", uid=uid)


@app.route("/delete_tracker/<int:tid>")
def delete_tracker(tid):
    tracker = Tracker_info.query.filter(
        Tracker_info.tracker_id == tid).one()
    Tracker_info.query.filter(
        Tracker_info.tracker_id == tid).delete()
    if tracker.tracker_type == "Numerical":
        Numerical_log.query.filter(Numerical_log.tracker_id == tid).delete()
    else:
        Mcq_log.query.filter(Mcq_log.tracker_id == tid).delete()

    db.session.commit()
    return redirect("/dashboard/{}".format(tracker.user_id))


@app.route("/edit_tracker/<int:tid>", methods=["GET", "POST"])
def edit_tracker(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    tracker.timestamp = datetime.now()
    db.session.add(tracker)
    db.session.commit()

    if request.method == "GET":
        return render_template("edit_tracker.html", tracker=tracker)
    else:
        tracker.name = request.form["name"]
        tracker.description = request.form["description"]
        tracker.timestamp = datetime.now()
        db.session.add(tracker)
        db.session.commit()
        return redirect("/dashboard/{}".format(tracker.user_id))


@app.route("/add_log/<int:tid>", methods=["GET", "POST"])
def add_log(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    tracker.timestamp = datetime.now()
    db.session.add(tracker)
    db.session.commit()

    if request.method == "GET":
        return render_template("add_log.html", tracker=tracker)
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


@app.route("/view_log/<int:tid>")
def view_log(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    tracker.timestamp = datetime.now()
    db.session.add(tracker)
    db.session.commit()

    if tracker.tracker_type == "Numerical":
        return render_template("view_log.html", tracker=tracker, logs=tracker.numerical_log)
    else:
        return render_template("view_log.html", tracker=tracker, logs=tracker.mcq_log)


@app.route("/delete_log/<int:tid>/<int:lid>")
def delete_log(tid, lid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    if tracker.tracker_type == "MultipleChoice":
        Mcq_log.query.filter(Mcq_log.log_id == lid).delete()
        db.session.commit()
        return render_template("view_log.html", tracker=tracker, logs=tracker.mcq_log)
    else:
        Numerical_log.query.filter(Numerical_log.log_id == lid).delete()
        db.session.commit()
        return render_template("view_log.html", tracker=tracker, logs=tracker.numerical_log)


@app.route("/edit_log/<int:tid>/<int:lid>", methods=["GET", "POST"])
def edit_log(tid, lid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    tracker.timestamp = datetime.now()
    db.session.add(tracker)
    db.session.commit()

    if tracker.tracker_type == "MultipleChoice":
        log = Mcq_log.query.filter(Mcq_log.log_id == lid).one()

        if request.method == "GET":
            return render_template("edit_log.html", log=log, tracker=tracker)
        elif request.method == "POST":
            log.timestamp = datetime.strptime(
                request.form["timestamp"], '%Y-%m-%dT%H:%M')
            log.value = request.form['value']
            log.note = request.form['note']
            db.session.add(log)
            db.session.commit()
            return render_template("view_log.html", tracker=tracker,
                                   logs=tracker.mcq_log)

    elif tracker.tracker_type == "Numerical":
        log = Numerical_log.query.filter(Numerical_log.log_id == lid).one()

        if request.method == "GET":
            return render_template("edit_log.html", log=log, tracker=tracker)
        elif request.method == "POST":
            log.timestamp = datetime.strptime(
                request.form["timestamp"], '%Y-%m-%dT%H:%M')
            log.value = request.form['value']
            log.note = request.form['note']
            db.session.add(log)
            db.session.commit()
            return render_template("view_log.html", tracker=tracker,
                                   logs=tracker.numerical_log)


# fuctions for drawing time series graphs
@app.route("/stats_log/<int:tid>")
def stats_log(tid):
    tracker = Tracker_info.query.filter(Tracker_info.tracker_id == tid).one()
    tracker.timestamp = datetime.now()
    db.session.add(tracker)
    db.session.commit()

    mini, maxi, avg = 0, 0, 0
    if tracker.tracker_type == "Numerical":
        if len(tracker.numerical_log) > 0:
            mini, maxi, avg = numerical_stats(tracker.numerical_log)
        graph(tracker.numerical_log, "Numerical")
        return render_template("stats_log.html", mini=mini, maxi=maxi, avg=avg, ttype="Numerical", tid=tid)
    else:
        mini, maxi = "", ""
        if len(tracker.mcq_log) > 0:
            mini, maxi = mcq_stats(tracker.mcq_log)
        graph(tracker.mcq_log, "MultipleChoice")
        return render_template("stats_log.html", mini=mini, maxi=maxi, ttype="MultipleChoice", tid=tid)


@app.route("/hello/<name>")
def hello(name):
    job = tasks.just_say_hello.delay(name)
    return str(job), 200


if __name__ == '__main__':
    # Run the Flask app
    app.run(host="0.0.0.0", debug=True)
    #app.debug = True
