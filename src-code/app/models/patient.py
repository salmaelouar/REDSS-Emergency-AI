"""
Patient Registration Database Model
Separate from emergency calls - for registered/existing patients
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RegisteredPatient(Base):
    """Registered patient with medical history"""
    __tablename__ = "registered_patients"
    
    # Primary key
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Information
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date)
    age = Column(Integer)
    sex = Column(String(10))
    blood_type = Column(String(10))
    
    # Contact Information
    phone = Column(String(50), index=True)
    street = Column(String(200), index=True)
    city = Column(String(100))
    postal_code = Column(String(20))
    
    # Medical Information
    primary_condition = Column(String(200))  # Main condition/disease
    allergies = Column(Text)  # Known allergies
    medications = Column(Text)  # Current medications
    medical_history = Column(Text)  # Past medical history
    
    # Journey Tracking
    journey_events = Column(Text)  # JSON string of journey events
    last_contact = Column(DateTime)
    next_followup = Column(Date)
    
    # AI Generated Images
    journey_image_1 = Column(String(500))  # Path to first AI image
    journey_image_2 = Column(String(500))  # Path to second AI image
    
    # Notes
    follow_up_notes = Column(Text)
    clinical_notes = Column(Text)
    
    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RegisteredPatient {self.patient_id} - {self.name}>"
