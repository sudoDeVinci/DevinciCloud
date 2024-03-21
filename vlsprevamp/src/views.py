from src.handlers import *
from psutil import Process, cpu_percent
from os import getpid
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def index() -> Response:
    return render_template("index.html", user=current_user)

@views.route("/about", methods=['GET'])
def about() -> Response:
    return render_template("about.html", user = current_user)

@views.route('/system-info')
def system_info() -> Response:
    """
    Memory info and cpu usage in json return.
    """
    pid = getpid()
    memory_usage = f"{Process(pid).memory_info().rss / (1024 ** 2):.2f}"  # in MB
    cpu_usage = f"{cpu_percent():.2f}"
    return jsonify(memory_usage=memory_usage, cpu_usage=cpu_usage)