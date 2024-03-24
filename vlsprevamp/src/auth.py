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
    return render_template("sign_up.html", user = current_user)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    #data = request.form
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        debug(f"Email: {email} and Password: {password}")
        if not email or not password:
            flash("Fields cannot be empty.", category="error") 
            return render_template("login.html", user = current_user)
        
        elif not UserService.exists(email):
            flash("No Account for that email found", category="error")
            return render_template("login.html", user = current_user)
        
        else:
            user = UserService.get(email, password=None)
            if not user: 
                flash("User was not found.", category = "error")
                return render_template("login.html", user = current_user)
            
            # print("We got the user!")
            correct = check_password_hash(user.get_password(), password)
            if not correct:
                flash("Incorrect email/password combination.", category = "error")
                return render_template("login.html", user = current_user)

            flash("Logged in Successfully!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.index"))

    if request.method == "GET":
        return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("login.html", user=current_user)