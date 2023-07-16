# @Author: Julius U. Heller
# @Date:   2021-05-17T16:09:26+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: forms.py
# @Last modified by:   Julius U. Heller
# @Last modified time: 2021-06-20T21:58:25+02:00


from flask_wtf import FlaskForm
from wtforms import Form, TextField, TextAreaField,StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.utils import secure_filename

#neues form
class SignUpForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    #
    # Anscheinend ist FileRequired verbuggt und funktioniert nicht!
    #
    #pic1 = FileField('Picture:', validators=[FileRequired(),FileAllowed(['jpg', 'png'], 'PNG/JPG Images only!')])
    #pic2 = FileField('Picture:', validators=[FileRequired(),FileAllowed(['jpg', 'png'], 'PNG/JPG Images only!')])
    #pic3 = FileField('Picture:', validators=[FileRequired(),FileAllowed(['jpg', 'png'], 'PNG/JPG Images only!')])
    pic1 = FileField('Picture:')
    pic2 = FileField('Picture:')
    pic3 = FileField('Picture:')
    submit = SubmitField('Sign Up')
#neues form
class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    #pic = FileField('Picture:', validators=[FileRequired(),FileAllowed(['jpg', 'png'], 'PNG/JPG Images only!')])
    submit = SubmitField('Sign In')

#neues form
class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    
class VideoUploadForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    video = FileField('Video:', validators=[DataRequired()])
    submit = SubmitField('Hochladen')
    

#kim: eigentlich müll diese drei forms
class CreateForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    picturefront = FileField('Gesicht von vorne', validators=[FileRequired(),FileAllowed(['jpg', 'png'], 'PNG Images only!') ])
    pictureleft = FileField('Gesicht von links', validators=[FileRequired(),FileAllowed(['jpg','png'], 'PNG Images only!') ])
    pictureright = FileField('Gesicht von rechts', validators=[FileRequired(),FileAllowed(['jpg','png'], 'PNG Images only!') ])

    #picturefront = FileField('Gesicht von vorne')
    #pictureleft = FileField('Gesicht von links')
    #pictureright = FileField('Gesicht von rechts')
    submit = SubmitField('Sign In')


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    # Added File Required and FileAllowed to Field
    picture = FileField('Gesicht von vorne', validators=[FileRequired(),FileAllowed(['jpg','png'], 'PNG Images only!') ])
    submit = SubmitField('Sign In')


class LoginCameraForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    # Added File Required and FileAllowed to Field
    submit = SubmitField('Sign In')
