"""
Patient Registration Service
Handles registered patient database operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models.patient import RegisteredPatient, Base
import json
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///./data/registered_patients.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

def get_patient_db():
    """Get database session"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_patient(db: Session, patient_data: dict):
    """Create a new registered patient"""
    patient = RegisteredPatient(
        patient_id=patient_data.get('patient_id'),
        name=patient_data.get('name'),
        date_of_birth=patient_data.get('date_of_birth'),
        age=patient_data.get('age'),
        sex=patient_data.get('sex'),
        blood_type=patient_data.get('blood_type'),
        phone=patient_data.get('phone'),
        street=patient_data.get('street'),
        city=patient_data.get('city'),
        postal_code=patient_data.get('postal_code'),
        primary_condition=patient_data.get('primary_condition'),
        allergies=patient_data.get('allergies'),
        medications=patient_data.get('medications'),
        medical_history=patient_data.get('medical_history'),
        journey_events=patient_data.get('journey_events', json.dumps([])),
        follow_up_notes=patient_data.get('follow_up_notes', ''),
        clinical_notes=patient_data.get('clinical_notes', '')
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patient_by_id(db: Session, patient_id: str):
    """Get patient by ID"""
    return db.query(RegisteredPatient).filter(RegisteredPatient.patient_id == patient_id).first()

def get_patient_by_name(db: Session, name: str):
    """Get patient by name (case-insensitive)"""
    return db.query(RegisteredPatient).filter(RegisteredPatient.name.ilike(f"%{name}%")).first()

def search_patients(db: Session, name: str = None, street: str = None, phone: str = None):
    """Search patients by multiple criteria"""
    query = db.query(RegisteredPatient)
    
    if name:
        query = query.filter(RegisteredPatient.name.ilike(f"%{name}%"))
    if street:
        query = query.filter(RegisteredPatient.street.ilike(f"%{street}%"))
    if phone:
        query = query.filter(RegisteredPatient.phone.ilike(f"%{phone}%"))
    
    return query.all()

def get_all_patients(db: Session, skip: int = 0, limit: int = 100):
    """Get all registered patients"""
    return db.query(RegisteredPatient).offset(skip).limit(limit).all()

def update_patient(db: Session, patient_id: str, update_data: dict):
    """Update patient information"""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return None
    
    for key, value in update_data.items():
        if hasattr(patient, key):
            setattr(patient, key, value)
    
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient

def add_journey_event(db: Session, patient_id: str, event: dict):
    """Add a journey event to patient"""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return None
    
    events = json.loads(patient.journey_events) if patient.journey_events else []
    events.append(event)
    patient.journey_events = json.dumps(events)
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: str):
    """Delete a patient"""
    patient = get_patient_by_id(db, patient_id)
    if patient:
        db.delete(patient)
        db.commit()
        return True
    return False
