from wtforms import Form, TextField, SubmitField, FileField
from wtforms.validators import DataRequired


class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    submit = SubmitField('Sign In')


class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignUpForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic1 = FileField('Picture:')
    pic2 = FileField('Picture:')
    pic3 = FileField('Picture:')
    submit = SubmitField('Sign Up')
