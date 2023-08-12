# Standard libraries
import uuid

# Third party
from flask import render_template, make_response, request, Blueprint

# Own libraries
from app import ws
from app.login.routes import logincamera


main = Blueprint('main', __name__)


@main.route("/team21")
def team():
    return render_template("team21.html")


@main.route("/team23")
def team2():
    return render_template("team23.html")


@main.route("/algorithms")
def algorithms():
    return render_template("algorithms.html")


@main.route("/index", methods=["GET", "POST"])
@main.route("/", methods=["GET", "POST"])
def index():
    form = None
    if request.method == "POST":
        # TODO: Is this really necessary?
        return logincamera()

    cookie = request.cookies.get("session_uuid")
    if not cookie:

        response = make_response(render_template("index.html", BigBrotherUserList=ws.BigBrotherUserList, form=form))
        uuid_ = uuid.uuid4()
        print("setting new uuid: ", uuid_)
        response.set_cookie("session_uuid", str(uuid_))

        return response
    return render_template("index.html", BigBrotherUserList=ws.BigBrotherUserList, form=form)
