# Standard libraries
import uuid

# Third party
from flask import render_template, make_response, request, Blueprint

# Own libraries
from app import user_manager
from app.blueprints.login.routes import logincamera


main = Blueprint('main', __name__)


@main.route("/team21")
def team():
    return render_template("team21.html")


@main.route("/team23")
def team2():
    return render_template("team23.html")

@main.route("/team24")
def team3():
    return render_template("team24.html")

@main.route("/algorithms")
def algorithms():
    return render_template("algorithms.html")


@main.route("/index", methods=["GET", "POST"])
@main.route("/", methods=["GET", "POST"])
def index():
    # TODO: What is this condition used for. Why don't we directly send the POST
    # request to the route of the logincamera function?
    # TODO: This should probably be avoided, because it would be best for the
    # home route not to contain anything related to the login if possible
    if request.method == "POST":
        return logincamera()

    form = None
    template = render_template(
        "index.html",
        BigBrotherUserList=user_manager.BigBrotherUserList,
        form=form
    )

    cookie = request.cookies.get("session_uuid")
    if not cookie:
        response = make_response(template)
        response.set_cookie("session_uuid", str(uuid.uuid4()))
        return response

    return template
