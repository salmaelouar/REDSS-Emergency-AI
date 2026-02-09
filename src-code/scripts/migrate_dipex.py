import pandas as pd
import sqlite3
import datetime
import random
import os

# Paths
EXCEL_PATH = 'Dipex Visualization/Dipex_Interview_Segment_Output_gpt-3.5-turbo_041225.xlsx'
DB_PATH = 'emergency_calls.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Reading {EXCEL_PATH}...")
    xls = pd.ExcelFile(EXCEL_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM emergency_calls")
    print("Cleared existing calls.")

    # Process English sheet
    df = xls.parse('English')
    
    for idx, row in df.iterrows():
        interview_name = row['Interview'] # e.g. "Interview 1"
        segment_summary = row['Segment Summary']
        # Store raw Timeline string in soap_objective for display
        dipex_timeline = str(row['Timeline'])
        
        # ID generation
        call_id = f"{interview_name}-{idx+1}"
        
        # Simple urgency heuristic
        text_lower = str(segment_summary).lower()
        if any(w in text_lower for w in ['pain', 'blood', 'died', 'emergency', 'cancer', 'severe']):
            urgency = 'CRITICAL'
            score = 90.0
        elif any(w in text_lower for w in ['worry', 'scared', 'concern', 'doubt']):
            urgency = 'HIGH'
            score = 75.0
        else:
            urgency = 'MEDIUM'
            score = 50.0
            
        # Timestamp (staggered)
        created_at = datetime.datetime.now() - datetime.timedelta(hours=idx)
        
        cursor.execute("""
            INSERT INTO emergency_calls (
                call_id, transcript, soap_subjective, soap_objective, urgency_level, 
                urgency_score, urgency_reasoning, audio_duration, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_id,                # Unique ID
            f"[{interview_name}] {segment_summary}", # Prefix transcript
            segment_summary,        # soap_subjective
            # Inject structured header for DNP parsing
            f"Name: {interview_name}\nAge: {random.randint(25, 80)}\nAddress: London, UK\nPhone: +44 7700 900{idx:03d}\nBlood type: {random.choice(['A+', 'O+', 'B+', 'AB+'])}\nAllergies: None reported\nMedications: None reported\n\nTimeline:\n{dipex_timeline}",
            urgency,
            score,
            f"Imported from Dipex Excel", 
            random.randint(120, 600), # duration
            created_at
        ))
        
    conn.commit()
    conn.close()
    print(f"Migrated {len(df)} records from English sheet.")

if __name__ == "__main__":
    migrate()
