import sqlite3
import random

DB_PATH = 'emergency_calls.db'

def fix_metadata():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all calls
    cursor.execute("SELECT call_id, soap_objective FROM emergency_calls")
    rows = cursor.fetchall()
    
    updated_count = 0
    
    for call_id, soap_objective in rows:
        # Check if already patched
        if soap_objective and "Name:" in soap_objective:
            continue
            
        # Only patch if it looks like a migrated call (or just patch all for now to be safe)
        # We'll use the call_id as the name if it's "Interview X" or similar
        fake_name = call_id.split('-')[0] if '-' in call_id else "Patient One"
        if "Interview" in call_id:
             fake_name = call_id.replace('-', ' ')
        
        # Determine fake details
        fake_phone = f"+44 7700 900{random.randint(100, 999)}"
        fake_blood = random.choice(['A+', 'O+', 'B+', 'AB+', 'O-'])
        fake_age = random.randint(25, 85)
        
        # Construct header
        header = f"""Name: {fake_name}
Age: {fake_age}
Address: London, UK
Phone: {fake_phone}
Blood type: {fake_blood}
Allergies: None reported
Medications: None reported

Timeline:
"""
        new_objective = header + (soap_objective if soap_objective else "")
        
        cursor.execute("UPDATE emergency_calls SET soap_objective = ? WHERE call_id = ?", (new_objective, call_id))
        updated_count += 1
        
    conn.commit()
    conn.close()
    print(f"✓ Successfully patched {updated_count} calls with metadata.")

if __name__ == "__main__":
    fix_metadata()
