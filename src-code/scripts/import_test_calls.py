"""
Import test data from evaluated_text_data.py into database
"""
import sys
import os
# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from app.services.database import init_db, get_db
from app.models.call import EmergencyCall
from data.text.evaluated_text_data import EVALUATED_CALLS as TEST_CALLS

def import_test_calls():
    """Import test calls into database"""
    print("🔄 Starting import...")
    init_db()
    
    imported = 0
    skipped = 0
    
    with get_db() as db:
        for call_data in TEST_CALLS:
            # Check if call already exists
            existing = db.query(EmergencyCall).filter(
                EmergencyCall.call_id == call_data['call_id']
            ).first()
            
            if existing:
                print(f"⏭️  Skipping {call_data['call_id']} (already exists)")
                skipped += 1
                continue
            
            # Create new call
            new_call = EmergencyCall(
                call_id=call_data['call_id'],
                transcript=call_data['text'],
                audio_duration=0,
                soap_subjective=call_data['expected_soap']['subjective'],
                soap_objective=call_data['expected_soap']['objective'],
                soap_assessment=call_data['expected_soap']['assessment'],
                soap_plan=call_data['expected_soap']['plan'],
                urgency_level=call_data['expected_urgency'].upper(),
                urgency_score=95 if call_data['expected_urgency'] == 'critical' else 
                             75 if call_data['expected_urgency'] == 'high' else
                             50 if call_data['expected_urgency'] == 'medium' else 25,
                urgency_reasoning=f"{call_data['expected_type']} - Test data import",
                created_at=datetime.now(),
                processed_at=datetime.now()
            )
            
            db.add(new_call)
            db.commit()
            print(f"✅ Imported {call_data['call_id']}")
            imported += 1
    
    print(f"\n🎉 Import complete! Imported: {imported}, Skipped: {skipped}")

if __name__ == "__main__":
    import_test_calls()