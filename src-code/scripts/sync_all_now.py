"""
Script to sync ALL existing emergency calls to registered patients database.
Run this once to populate the Patient Journey with legacy data.
"""
from app.services.database import get_db
from app.models.call import EmergencyCall
from app.services.sync_helper import sync_emergency_call_to_patient_journey
from sqlalchemy.orm import Session

def sync_all_calls():
    print("🔄 Starting massive sync of emergency calls to patient journey...")
    
    with get_db() as db:
        calls = db.query(EmergencyCall).all()
        print(f"found {len(calls)} emergency calls.")
        
        count = 0
        for call in calls:
            if call.patient_name and len(call.patient_name) > 1:
                try:
                    result = sync_emergency_call_to_patient_journey(call.id)
                    if result:
                        count += 1
                        print(f"  ✓ Synced: {call.patient_name}")
                except Exception as e:
                    print(f"  ✗ Failed {call.patient_name}: {e}")
            else:
                print(f"  - Skipped call {call.id} (no name)")
                
    print(f"\n✅ Sync Complete! {count} patients synced/updated.")

if __name__ == "__main__":
    sync_all_calls()
