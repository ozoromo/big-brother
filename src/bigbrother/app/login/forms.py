from wtforms import Form, TextField, SubmitField
from wtforms.validators import DataRequired

from flask_wtf.file import FileField


class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    submit = SubmitField('Sign In')


class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')
