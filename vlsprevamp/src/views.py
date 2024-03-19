from src.handlers import *
from psutil import Process, cpu_percent
from os import getpid

views = Blueprint("views", __name__)

@views.route("/")
def index() -> Response:
    return render_template("index.html")

# Route to get memory and CPU usage
@views.route('/system-info')
def system_info() -> Response:
    pid = getpid()
    memory_usage = f"{Process(pid).memory_info().rss / (1024 ** 2):.2f}"  # in MB
    cpu_usage = f"{cpu_percent():.2f}"
    return jsonify(memory_usage=memory_usage, cpu_usage=cpu_usage)