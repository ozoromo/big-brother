from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired, StopValidation

from app import ws

_picture_validators = [
    FileRequired(),
    FileAllowed(["jpeg", "jpg", "png"]),
]


class UsernameDoesNotExistsInDatabase(object):
    """
    Checks whether user doesn't exists in the database otherwise stops
    the validation chain.

    If the user doesn't exist, also removes prior errors
    (such as processing errors) from the field.
    """
    def __call__(self, form, field):
        if ws.DB.getUser(field.data):
            message = field.gettext(f"The username '{field.data}' already exists!")
            field.errors[:] = []
            raise StopValidation(message)


class CameraSignUpForm(FlaskForm):
    name = TextField(
        "Name:", validators=[
            DataRequired(),
            UsernameDoesNotExistsInDatabase(),
        ])
    submit = SubmitField("Sign In")


class SignUpForm(FlaskForm):
    name = TextField(
        "Name:",
        validators=[
            DataRequired(),
            UsernameDoesNotExistsInDatabase(),
        ])
    pic1 = FileField("Picture:", validators=_picture_validators)
    pic2 = FileField("Picture:", validators=_picture_validators)
    pic3 = FileField("Picture:", validators=_picture_validators)
    submit = SubmitField('Sign Up')
