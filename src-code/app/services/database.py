"""
Real-Time Emergency Call System
Database Service with Urgency Support - FIXED WITH EXPUNGE
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime
from app.models.call import Base, EmergencyCall

DATABASE_URL = "sqlite:///./data/emergency_calls.db"

# Add connection parameters for better concurrent access
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={
        "check_same_thread": False,  # Allow concurrent access
        "timeout": 30  # Wait up to 30 seconds for lock to be released
    }
)
SessionLocal = sessionmaker(bind=engine) # SessionLocal is a class that will be used to create database sessions in the context manager because 


def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine) 
    print("✓ Database tables created")


@contextmanager
def get_db():
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def save_call(call_id: str, audio_path: str, transcript: str, duration: float, 
              patient_name: str = None, patient_id: str = None, doctor_name: str = None, disease: str = None,
              language: str = "en") -> EmergencyCall:
    """Save an emergency call to database"""
    with get_db() as db:
        call = EmergencyCall(
            call_id=call_id,
            audio_path=audio_path,
            transcript=transcript,
            audio_duration=duration,
            patient_name=patient_name,
            patient_id=patient_id,
            doctor_name=doctor_name,
            disease=disease,
            language=language
        )
        db.add(call)
        db.flush()
        db.refresh(call)
        
        # Detach object from session before returning
        db.expunge(call)
        
        return call


def update_soap(call_id: str, subjective: str, objective: str, 
                assessment: str, plan: str) -> EmergencyCall: #-> EmergencyCall is the return type and the function returns the updated call object
    """Update SOAP notes for a call"""
    with get_db() as db:
        call = db.query(EmergencyCall).filter(
            EmergencyCall.call_id == call_id
        ).first()
        
        if call:
            call.soap_subjective = subjective
            call.soap_objective = objective
            call.soap_assessment = assessment
            call.soap_plan = plan
            call.processed_at = datetime.utcnow()
            db.flush()
            db.refresh(call)
            
            # Detach object from session before returning
            db.expunge(call)
        
        return call


def update_urgency(call_id: str, level: str, score: float, reasoning: str) -> EmergencyCall:
    """Update urgency classification for a call"""
    with get_db() as db:
        call = db.query(EmergencyCall).filter(
            EmergencyCall.call_id == call_id
        ).first()
        
        if call:
            call.urgency_level = level
            call.urgency_score = score
            call.urgency_reasoning = reasoning
            db.flush()
            db.refresh(call)
            
            # Detach object from session before returning
            db.expunge(call)
        
        return call


def get_call(call_id: str) -> EmergencyCall:
    """Retrieve a call by call_id"""
    with get_db() as db:
        call = db.query(EmergencyCall).filter(
            EmergencyCall.call_id == call_id
        ).first()
        
        if call:
            # Detach object from session before returning
            db.expunge(call)
        
        return call


def get_all_calls(limit: int = 100) -> list:
    """Get all calls (most recent first)"""
    with get_db() as db:
        calls = db.query(EmergencyCall).order_by(
            EmergencyCall.created_at.desc()
        ).limit(limit).all()
        
        # Detach all objects from session before returning
        for call in calls:
            db.expunge(call)
        
        return calls


def get_calls_by_urgency(urgency_level: str, limit: int = 100) -> list:
    """Get calls by urgency level"""
    with get_db() as db:
        calls = db.query(EmergencyCall).filter(
            EmergencyCall.urgency_level == urgency_level
        ).order_by(EmergencyCall.created_at.desc()).limit(limit).all()
        
        # Detach all objects from session before returning
        for call in calls:
            db.expunge(call)
        
        return calls