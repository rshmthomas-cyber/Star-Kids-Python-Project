from flask import Flask, render_template, redirect, url_for, request, flash, session
from extensions import db, bcrypt, login_manager
from models import Parent, Kid, Task
from flask_login import login_user, logout_user, login_required, current_user
import random

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kids_rewards.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ✅ initialize extensions only once
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    with app.app_context():
        db.create_all()

    # ================= ROUTES =================
    @login_manager.user_loader
    def load_user(user_id):
        return Parent.query.get(int(user_id))

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if Parent.query.filter_by(username=username).first():
                flash("⚠️ Username already exists.", "warning")
                return redirect(url_for("register"))

            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            new_parent = Parent(username=username, password=hashed)
            db.session.add(new_parent)
            db.session.commit()
            flash("✅ Registered successfully. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            parent = Parent.query.filter_by(username=username).first()
            if parent and bcrypt.check_password_hash(parent.password, password):
                login_user(parent)
                session["parent_id"] = parent.id
                return redirect(url_for("dashboard"))

            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        kids = Kid.query.filter_by(parent_id=current_user.id).all()
        return render_template("dashboard.html", kids=kids)

    @app.route("/add_kid", methods=["GET", "POST"])
    @login_required
    def add_kid():
        if request.method == "POST":
            name = request.form["name"]
            age = int(request.form["age"])
            new_kid = Kid(name=name, age=age, parent_id=current_user.id)
            db.session.add(new_kid)
            db.session.commit()
            flash("✅ Kid added.", "success")
            return redirect(url_for("dashboard"))
        return render_template("add_kid.html")

    @app.route("/add_task/<int:kid_id>", methods=["GET", "POST"])
    @login_required
    def add_task(kid_id):
        kid = Kid.query.get_or_404(kid_id)
        if request.method == "POST":
            description = request.form["description"]
            points = int(request.form["points"])
            new_task = Task(description=description, points=points, kid_id=kid.id)
            db.session.add(new_task)
            db.session.commit()
            flash("✅ Task added.", "success")
            return redirect(url_for("dashboard"))
        return render_template("add_task.html", kid=kid)

    @app.route("/complete_task/<int:task_id>")
    @login_required
    def complete_task(task_id):
        task = Task.query.get_or_404(task_id)
        if not task.completed:
            task.completed = True
            task.kid.points += task.points
            task.kid.weekly_points += task.points
            db.session.commit()
            flash(f"{task.kid.name} earned {task.points} pts!", "success")
        return redirect(url_for("dashboard"))

    @app.route("/reset_daily")
    @login_required
    def reset_daily():
        kids = Kid.query.filter_by(parent_id=current_user.id).all()
        for kid in kids:
            kid.points = 0
            for task in kid.tasks:
                task.completed = False
        db.session.commit()
        flash("🔄 Daily tasks reset (weekly totals kept).", "info")
        return redirect(url_for("dashboard"))

    @app.route("/reset_weekly_points")
    @login_required
    def reset_weekly_points():
        kids = Kid.query.filter_by(parent_id=current_user.id).all()
        if not kids:
            flash("⚠️ No kids found.", "warning")
            return redirect(url_for("dashboard"))

        winner = max(kids, key=lambda k: k.weekly_points)
        rewards = ["Trip to Oberon Mall", "Order Chicking!", "Ice cream party"]
        reward = random.choice(rewards)
        flash(f"🏆 Weekly Winner: {winner.name} with {winner.weekly_points} pts! Reward: {reward}", "winner")

        for kid in kids:
            kid.points = 0
            kid.weekly_points = 0
            for task in kid.tasks:
                task.completed = False
        db.session.commit()
        return redirect(url_for("dashboard"))

    @app.route("/leaderboard")
    @login_required
    def leaderboard():
        kids = Kid.query.filter_by(parent_id=current_user.id).order_by(Kid.weekly_points.desc()).all()
        return render_template("leaderboard.html", kids=kids)

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
