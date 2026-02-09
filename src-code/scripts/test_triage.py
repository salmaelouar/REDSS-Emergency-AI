
import os
import sys
import json

# Add current directory to path
sys.path.append(os.getcwd())

from data.text.evaluated_text_data import EVALUATED_CALLS
from data.text.custom_test_scripts import CUSTOM_CALLS
from app.services.urgency_classifier import urgency_classifier

def test_triage_accuracy():
    all_calls = CUSTOM_CALLS + EVALUATED_CALLS
    results = []
    
    print(f"Testing triage accuracy for {len(all_calls)} calls...")
    
    # Header for markdown table
    print("\n### Triage Validation Results\n")
    print("| Call ID | Expected Triage | AI Triage | Match | Reasoning Snippet |")
    print("| :--- | :--- | :--- | :---: | :--- |")
    
    for call in all_calls:
        call_id = call.get('call_id')
        text = call.get('text', '')
        soap = call.get('expected_soap', {})
        expected = call.get('expected_urgency', 'MEDIUM').upper()
        
        # Normalize expected for comparison
        if expected == "最優先": expected = "CRITICAL" 
        expected = expected.upper()
        
        # Determine language
        language = "ja" if "CALL_JA" in call_id else "en"
        
        # Classify
        try:
            classification = urgency_classifier.classify(text, soap, language)
            ai_result = classification.get('level', 'LOW')
            
            # Match check
            match = "✅" if ai_result == expected else "❌"
            
            reasoning = classification.get('reasoning', '').replace('\n', ' ')
            snippet = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
            
            print(f"| {call_id} | {expected} | {ai_result} | {match} | {snippet} |")
        except Exception as e:
            print(f"| {call_id} | {expected} | ERROR | ❌ | {str(e)} |")

if __name__ == "__main__":
    test_triage_accuracy()
