from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from models import db, seed_doctors, Doctor, Patient, Photo
from datetime import datetime
from pathlib import Path
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doctor_i.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)
with app.app_context():
    db.create_all()
    seed_doctors()

# Главная
@app.route("/")
def index():
    return redirect(url_for("doctors_list"))

# Список врачей
@app.route("/doctors")
def doctors_list():
    doctors = Doctor.query.all()
    return render_template("doctors.html", doctors=doctors)

# Страница врача
@app.route("/doctor/<int:doctor_id>")
def doctor_detail(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("doctor_detail.html", doctor=doctor)

# Добавление пациента
@app.route("/patient/new/<int:doctor_id>", methods=["GET", "POST"])
def patient_new(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == "POST":
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        gender = request.form.get("gender")

        if not all([first_name, last_name, age, gender]):
            flash("Заполните все обязательные поля!", "error")
            return redirect(url_for("patient_new", doctor_id=doctor.id))

        patient = Patient(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            age=int(age),
            gender=gender,
            doctor_id=doctor.id
        )
        db.session.add(patient)
        db.session.commit()
        flash("Пациент добавлен!", "success")
        return redirect(url_for("doctor_detail", doctor_id=doctor.id))

    return render_template("patient_new.html", doctor=doctor)

# Страница пациента
@app.route("/patient/<int:patient_id>")
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # передаём photos упорядоченные по дате (новые первыми)
    photos = Photo.query.filter_by(patient_id=patient.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template("patient_detail.html", patient=patient, photos=photos)

# Исправленный upload_photo
@app.route("/patient/<int:patient_id>/upload", methods=["POST"])
def upload_photo(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    file = request.files.get("photo")

    if file and file.filename:
        # Формируем имена папок
        doctor_folder = patient.doctor.folder_name
        patient_folder = patient.folder_name
        date_folder = datetime.utcnow().strftime("%d.%m.%Y")

        # Абсолютный путь в static/uploads/...
        base_upload_dir = Path(current_app.static_folder) / "uploads" / doctor_folder / patient_folder / date_folder
        base_upload_dir.mkdir(parents=True, exist_ok=True)

        # Формируем безопасное имя
        ext = Path(file.filename).suffix or ".jpg"
        safe_name = f"{uuid.uuid4().hex}{ext}"
        filepath = base_upload_dir / safe_name
        file.save(str(filepath))

        # Относительный путь с POSIX-слешами, без префикса 'uploads/'
        relative_path = (Path(doctor_folder) / patient_folder / date_folder / safe_name).as_posix()

        photo = Photo(filename=relative_path, patient_id=patient.id)
        db.session.add(photo)
        db.session.commit()

        flash("Фото добавлено!", "success")
    else:
        flash("Файл не выбран или невалидный", "error")

    return redirect(url_for("patient_detail", patient_id=patient.id))

if __name__ == "__main__":
    app.run(debug=True)
