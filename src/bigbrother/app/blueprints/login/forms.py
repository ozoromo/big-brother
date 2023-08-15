from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.validators import DataRequired, StopValidation

from app import ws


_picture_validators = [
    FileRequired(),
    FileAllowed(["jpeg", "jpg", "png"]),
]


class UsernameExistsInDatabase(object):
    """
    Checks whether user exists in the database otherwise stops
    the validation chain.

    If the user exists, also removes prior errors
    (such as processing errors) from the field.
    """
    def __call__(self, form, field):
        if not ws.DB.getUser(field.data):
            message = field.gettext(f"The username '{field.data}' doesn't exist!")
            field.errors[:] = []
            raise StopValidation(message)


class LoginForm(FlaskForm):
    name = TextField(
        "Name:",
        validators=[
            DataRequired(),
            UsernameExistsInDatabase()
        ])
    pic = FileField("Picture:", validators=_picture_validators)
    submit = SubmitField("Login")


class CameraLoginForm(FlaskForm):
    name = TextField(
        'Name:', validators=[
            DataRequired(),
            UsernameExistsInDatabase(),
        ]
    )
    submit = SubmitField('Login')
