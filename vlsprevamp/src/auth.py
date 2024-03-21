from src.handlers import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, redirect
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__) 

@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    return sign_up()

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    return render_template("sign_up.html")

@auth.route("/login", methods=['GET', 'POST'])
def login():
    #data = request.form
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        debug(f"Email: {email} and Password: {password}")
        if not email and not password:
            flash("Fields cannot be empty.", category="error") 
            return render_template("login.html")
        
        elif not UserService.registered(email, generate_password_hash(password)):
            flash("No Account for that email/password combination found.", category="error")
            return render_template("login.html")
        
        else:
            user = UserService.get(email, password)
            if not user: 
                flash("Couldn't fetch user records", category = "error")
                return render_template("login.html")

            flash("Logged in Successfully!", category="success")
            return redirect(url_for("views.index"))

    if request.method == "GET":
        return render_template("login.html")
@auth.route("/logout")
def logout():
    return render_template("login.html")