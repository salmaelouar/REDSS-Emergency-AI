"""
Seed script to add sample registered patients to the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.patient_service import get_patient_db, create_patient
import json
from datetime import datetime, timedelta

# Sample patients
SAMPLE_PATIENTS = [
    {
        "patient_id": "PAT-COVID001",
        "name": "John Smith",
        "age": 45,
        "sex": "Male",
        "blood_type": "O+",
        "phone": "+1-555-0123",
        "street": "123 Main Street",
        "city": "Tokyo",
        "postal_code": "100-0001",
        "primary_condition": "COVID-19 Recovery",
        "allergies": "Penicillin",
        "medications": "Vitamin D, Zinc supplements",
        "medical_history": "Diagnosed with COVID-19 on March 28th. Experienced fever, cough, and fatigue.",
        "follow_up_notes": "Patient showing improvement. Weekly check-ins recommended.",
        "clinical_notes": "Recovering well from COVID-19. No current symptoms.",
        "journey_events": json.dumps([
            {
                "segment": 1,
                "date": "2024-03-28",
                "time": "17:00",
                "description": "Initial COVID-19 diagnosis - fever and cough",
                "status": "completed"
            },
            {
                "segment": 2,
                "date": "2024-03-29",
                "time": "10:00",
                "description": "First follow-up - symptoms persisting",
                "status": "completed"
            },
            {
                "segment": 3,
                "date": "2024-04-05",
                "time": "14:00",
                "description": "Weekly check-in - improvement noted",
                "status": "completed"
            },
            {
                "segment": 4,
                "date": "2024-04-12",
                "time": "11:00",
                "description": "Recovery assessment - cleared to return to activities",
                "status": "pending"
            }
        ])
    },
    {
        "patient_id": "PAT-HEART002",
        "name": "Maria Garcia",
        "age": 62,
        "sex": "Female",
        "blood_type": "A+",
        "phone": "+1-555-0456",
        "street": "456 Oak Avenue",
        "city": "Yokohama",
        "postal_code": "220-0001",
        "primary_condition": "Heart Attack Recovery",
        "allergies": "None",
        "medications": "Aspirin, Beta blockers, Statins",
        "medical_history": "Heart attack on April 1st. Underwent angioplasty.",
        "follow_up_notes": "Cardiac rehabilitation ongoing. Diet and exercise plan in place.",
        "clinical_notes": "Post-MI recovery progressing well.",
        "journey_events": json.dumps([
            {
                "segment": 1,
                "date": "2024-04-01",
                "time": "08:30",
                "description": "Emergency admission - chest pain and crushing sensation",
                "status": "completed"
            },
            {
                "segment": 2,
                "date": "2024-04-02",
                "time": "09:00",
                "description": "Post-surgery assessment - stable condition",
                "status": "completed"
            },
            {
                "segment": 3,
                "date": "2024-04-08",
                "time": "15:00",
                "description": "First week follow-up - medication compliance checked",
                "status": "completed"
            }
        ])
    },
    {
        "patient_id": "PAT-STROKE003",
        "name": "Takeshi Yamamoto",
        "age": 58,
        "sex": "Male",
        "blood_type": "B+",
        "phone": "+81-90-1234-5678",
        "street": "789 Sakura Street",
        "city": "Osaka",
        "postal_code": "530-0001",
        "primary_condition": "Stroke Recovery",
        "allergies": "Sulfa drugs",
        "medications": "Anticoagulants, Blood pressure medication",
        "medical_history": "Ischemic stroke on March 15th. Right side weakness.",
        "follow_up_notes": "Physical therapy ongoing. Speech therapy showing good results.",
        "clinical_notes": "Gradual improvement in motor function.",
        "journey_events": json.dumps([
            {
                "segment": 1,
                "date": "2024-03-15",
                "time": "11:20",
                "description": "Emergency admission - facial droop and slurred speech",
                "status": "completed"
            },
            {
                "segment": 2,
                "date": "2024-03-16",
                "time": "10:00",
                "description": "Initial assessment - began rehabilitation",
                "status": "completed"
            },
            {
                "segment": 3,
                "date": "2024-03-22",
                "time": "14:30",
                "description": "Week 1 progress - some improvement in speech",
                "status": "completed"
            }
        ])
    },
    {
        "patient_id": "PAT-RESP004",
        "name": "Emily Chen",
        "age": 34,
        "sex": "Female",
        "blood_type": "AB+",
        "phone": "+1-555-0789",
        "street": "321 Pine Road",
        "city": "Nagoya",
        "postal_code": "450-0001",
        "primary_condition": "Asthma Management",
        "allergies": "Pollen, Dust mites",
        "medications": "Inhaled corticosteroids, Bronchodilator",
        "medical_history": "Chronic asthma since childhood. Recent exacerbation.",
        "follow_up_notes": "Peak flow monitoring daily. Action plan reviewed.",
        "clinical_notes": "Asthma under control with current medication regimen.",
        "journey_events": json.dumps([
            {
                "segment": 1,
                "date": "2024-03-20",
                "time": "19:00",
                "description": "Asthma exacerbation - difficulty breathing",
                "status": "completed"
            },
            {
                "segment": 2,
                "date": "2024-03-27",
                "time": "16:00",
                "description": "Follow-up appointment - medication adjusted",
                "status": "completed"
            }
        ])
    },
    {
        "patient_id": "PAT-FALL005",
        "name": "Robert Johnson",
        "age": 71,
        "sex": "Male",
        "blood_type": "O-",
        "phone": "+1-555-0321",
        "street": "654 Maple Drive",
        "city": "Sapporo",
        "postal_code": "060-0001",
        "primary_condition": "Hip Fracture Recovery",
        "allergies": "Latex",
        "medications": "Pain management, Calcium supplements",
        "medical_history": "Fall at home resulting in hip fracture. Surgery performed.",
        "follow_up_notes": "Physical therapy ongoing. Home safety assessment completed.",
        "clinical_notes": "Post-operative recovery progressing as expected.",
        "journey_events": json.dumps([
            {
                "segment": 1,
                "date": "2024-04-10",
                "time": "13:45",
                "description": "Emergency admission - fall with hip pain",
                "status": "completed"
            },
            {
                "segment": 2,
                "date": "2024-04-11",
                "time": "08:00",
                "description": "Hip replacement surgery performed",
                "status": "completed"
            },
            {
                "segment": 3,
                "date": "2024-04-17",
                "time": "10:30",
                "description": "First week post-op - wound healing well",
                "status": "completed"
            }
        ])
    }
]

def seed_patients():
    """Seed the database with sample patients"""
    db_gen = get_patient_db()
    db = next(db_gen)
    
    try:
        count = 0
        for patient_data in SAMPLE_PATIENTS:
            # Check if patient already exists
            from app.services.patient_service import get_patient_by_id
            existing = get_patient_by_id(db, patient_data['patient_id'])
            
            if not existing:
                create_patient(db, patient_data)
                count += 1
                print(f"✓ Created patient: {patient_data['name']}")
            else:
                print(f"- Patient already exists: {patient_data['name']}")
        
        print(f"\n✓ Seed complete! Added {count} new patients.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding patient database...")
    seed_patients()
