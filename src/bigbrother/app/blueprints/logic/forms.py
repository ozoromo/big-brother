from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired


class VideoUploadForm(FlaskForm):
    name = TextField("Name:", validators=[DataRequired()])
    video = FileField(
        "Video:",
        validators=[
            FileRequired(),
            FileAllowed(["mp4"])
        ])
    submit = SubmitField("Upload")
