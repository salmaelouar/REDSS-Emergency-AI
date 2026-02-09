
import sqlite3
import os

DB_PATH = "emergency_calls.db"

if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        print(f"Connected to {DB_PATH}")
        print("Checking if column 'patient_id' exists in 'emergency_calls'...")
        
        # Check columns
        c.execute("PRAGMA table_info(emergency_calls)")
        columns = [row[1] for row in c.fetchall()]
        print(f"Current columns: {columns}")
        
        if "patient_id" not in columns:
            print("Adding 'patient_id' column...")
            c.execute("ALTER TABLE emergency_calls ADD COLUMN patient_id VARCHAR(50)")
            conn.commit()
            print("✓ Column added successfully.")
        else:
            print("✓ Column 'patient_id' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error migrating DB: {e}")
else:
    print(f"Database {DB_PATH} not found, skipping migration.")
