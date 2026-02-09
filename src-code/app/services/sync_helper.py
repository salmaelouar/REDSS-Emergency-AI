"""
Auto-sync helper to keep emergency calls and patient journey in sync
"""
from app.services.database import get_db
from app.models.call import EmergencyCall
from app.services.patient_service import create_patient, get_patient_by_name, update_patient, get_patient_db
import json
import uuid
from datetime import datetime

def sync_emergency_call_to_patient_journey(call_id: int):
    """
    Automatically sync an emergency call to patient journey database
    This is called after every emergency call is processed
    """
    try:
        # Get the emergency call
        with get_db() as emergency_db:
            call = emergency_db.query(EmergencyCall).filter(EmergencyCall.id == call_id).first()
            
            if not call or not call.patient_name:
                return None
            
            # Get patient journey database
            patient_db_gen = get_patient_db()
            patient_db = next(patient_db_gen)
            
            try:
                # Check if patient already exists
                existing = get_patient_by_name(patient_db, call.patient_name)
                
                if existing:
                    # Update existing patient - add new journey event
                    existing_events = json.loads(existing.journey_events) if existing.journey_events else []
                    
                    new_event = {
                        'segment': len(existing_events) + 1,
                        'date': call.created_at.strftime('%Y-%m-%d'),
                        'time': call.created_at.strftime('%H:%M'),
                        'description': f"Emergency call: {call.disease or 'Medical emergency'}",
                        'status': 'completed'
                    }
                    
                    existing_events.append(new_event)
                    
                    # Update notes
                    updated_history = (existing.medical_history or '') + f"\n[{call.created_at.strftime('%Y-%m-%d')}] Emergency call: {call.soap_subjective or ''}"
                    updated_clinical = (existing.clinical_notes or '') + f"\n{call.soap_assessment or ''}"
                    updated_plan = (existing.follow_up_notes or '') + f"\n{call.soap_plan or ''}"
                    
                    update_patient(patient_db, existing.patient_id, {
                        'primary_condition': call.disease or existing.primary_condition,
                        'medical_history': updated_history,
                        'clinical_notes': updated_clinical,
                        'follow_up_notes': updated_plan,
                        'journey_events': json.dumps(existing_events)
                    })
                    
                    print(f"✓ Updated existing patient in journey: {call.patient_name}")
                    return existing.patient_id
                    
                else:
                    # Create new patient
                    patient_data = {
                        'patient_id': f"PAT-{uuid.uuid4().hex[:8].upper()}",
                        'name': call.patient_name,
                        'primary_condition': call.disease or 'Emergency',
                        'medical_history': f"Emergency call on {call.created_at.strftime('%Y-%m-%d')}: {call.soap_subjective or ''}",
                        'clinical_notes': call.soap_assessment or '',
                        'follow_up_notes': call.soap_plan or '',
                        'journey_events': json.dumps([{
                            'segment': 1,
                            'date': call.created_at.strftime('%Y-%m-%d'),
                            'time': call.created_at.strftime('%H:%M'),
                            'description': f"Emergency call: {call.disease or 'Medical emergency'}",
                            'status': 'completed'
                        }])
                    }
                    
                    new_patient = create_patient(patient_db, patient_data)
                    print(f"✓ Created new patient in journey: {call.patient_name}")
                    return new_patient.patient_id
                    
            finally:
                patient_db.close()
                
    except Exception as e:
        print(f"✗ Failed to sync to patient journey: {e}")
        return None
