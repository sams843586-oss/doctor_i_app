from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), nullable=True)

    patients = db.relationship("Patient", back_populates="doctor", cascade="all, delete-orphan")

    @property
    def folder_name(self):
        # безопасный folder name: заменяем пробелы на подчёркивания
        return self.full_name.replace(" ", "_")

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    doctor = db.relationship("Doctor", back_populates="patients")

    photos = db.relationship("Photo", back_populates="patient", cascade="all, delete-orphan")

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def folder_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return "_".join(filter(None, parts)).replace(" ", "_")

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # хранит относительный путь без 'uploads/' префикса
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    patient = db.relationship("Patient", back_populates="photos")

def seed_doctors():
    if Doctor.query.count() == 0:
        doctors = [
            Doctor(full_name="Баштовая Яна Сергеевна", specialty=""),
            Doctor(full_name="Веснянцева Алёна Николаевна", specialty=""),
            Doctor(full_name="Кулешова Яна Владимировна", specialty=""),
        ]
        db.session.add_all(doctors)
        db.session.commit()
