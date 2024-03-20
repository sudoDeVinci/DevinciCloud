from src.handlers import *
from werkzeug.security import generate_password_hash, check_password_hash

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
        elif not UserService.registered(email, password):
            flash("No Account for that email/password combination found.", category="error")

        else:
            flash("Logged in Successfully!", category="success")
    return render_template("login.html")

@auth.route("/logout")
def logout():
    return render_template("login.html")