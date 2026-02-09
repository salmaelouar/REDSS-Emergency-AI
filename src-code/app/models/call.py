"""
Real-Time Emergency Call System
Database Model with SOAP and Urgency Fields
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EmergencyCall(Base):
    """Emergency call record with SOAP notes and urgency"""
    __tablename__ = "emergency_calls"
    
    # Primary key
    id = Column(Integer, primary_key=True)
    call_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Audio information
    audio_path = Column(String(255))
    audio_duration = Column(Float)
    
    # Identity & Context (New)
    patient_name = Column(String(100))
    patient_id = Column(String(50)) # Link to RegisteredPatient
    doctor_name = Column(String(100))
    disease = Column(String(100))
    
    # Transcription
    transcript = Column(Text)
    language = Column(String(10), default="en")
    
    # SOAP Notes
    soap_subjective = Column(Text)
    soap_objective = Column(Text)
    soap_assessment = Column(Text)
    soap_plan = Column(Text)
    
    # Urgency Classification 
    urgency_level = Column(String(20))      # CRITICAL, HIGH, MEDIUM, LOW
    urgency_score = Column(Float)           # 0-100
    urgency_reasoning = Column(Text)        # Why this level?
    # Translation Cache (JSON storage for multiple languages)
    # Stores: {"ja": {"patient_name": "...", "disease": "...", ...}}
    translated_data = Column(Text, default="{}")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<EmergencyCall {self.call_id} - {self.urgency_level}>" # 
