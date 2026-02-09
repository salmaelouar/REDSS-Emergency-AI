
import requests
import json

API_URL = "http://localhost:8000"

def refresh_dashboard():
    # 1. Get all calls
    response = requests.get(f"{API_URL}/api/calls?limit=100")
    if response.status_code != 200:
        print("Failed to fetch calls")
        return
    
    calls = response.json().get("calls", [])
    print(f"Refreshing {len(calls)} calls...")
    
    for call in calls:
        call_id = call.get("call_id")
        # Trigger quality metrics recalculation (this updates the cache/smart match)
        q_res = requests.get(f"{API_URL}/api/calls/{call_id}/quality")
        if q_res.status_code == 200:
            print(f"✓ Refreshed Quality Metrics for {call_id}: {q_res.json().get('note')}")
        else:
            print(f"✗ Failed to refresh {call_id}")

    # 2. Trigger Journey Sync (Links patients)
    s_res = requests.post(f"{API_URL}/api/patients/import-from-emergency-calls")
    if s_res.status_code == 200:
        print(f"✓ Journey Database Sync complete: {s_res.json().get('message')}")
    else:
        print(f"✗ Journey Sync failed")

if __name__ == "__main__":
    refresh_dashboard()
