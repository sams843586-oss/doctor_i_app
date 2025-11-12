from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class PatientForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired(), Length(min=1, max=120)])
    last_name = StringField("Фамилия", validators=[DataRequired(), Length(min=1, max=120)])
    age = IntegerField("Возраст", validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField("Пол", choices=[("М", "Мужской"), ("Ж", "Женский")], validators=[DataRequired()])
    submit = SubmitField("Создать пациента")

class PhotoUploadForm(FlaskForm):
    photo = FileField("Фотография", validators=[
        FileRequired(),
        FileAllowed(["jpg", "jpeg", "png"], "Только изображения JPG/PNG")
    ])
    submit = SubmitField("Загрузить")
