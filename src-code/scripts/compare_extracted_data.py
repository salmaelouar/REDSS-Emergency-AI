#!/usr/bin/env python3
"""
Comparison script to validate system extraction against expected evaluation data.
"""

import sys
import os
import re
import time
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import data
try:
    from data.text.evaluated_text_data import EVALUATED_CALLS
except ImportError:
    print("Error: Could not import EVALUATED_CALLS. Make sure you are in the project root.")
    sys.exit(1)

# Import services
try:
    from app.services.soap_extractor import SOAPExtractor, soap_extractor
    from app.services.urgency_classifier import HybridUrgencyClassifier, urgency_classifier
    print("✓ Services imported successfully")
except ImportError as e:
    print(f"Error importing services: {e}")
    # Fallback if instances aren't exported
    from app.services.soap_extractor import SOAPExtractor
    from app.services.urgency_classifier import HybridUrgencyClassifier
    soap_extractor = SOAPExtractor()
    urgency_classifier = HybridUrgencyClassifier()

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def extract_metadata_from_soap(soap: Dict[str, str]) -> Dict[str, str]:
    """Extract patient name and location from SOAP Objective section"""
    objective = soap.get('objective', '')
    
    # Extract Name
    name = "Unknown"
    name_match = re.search(r'(?:Name|氏名)[:：]\s*(.+?)(?:\n|$)', objective, re.IGNORECASE)
    if name_match:
        val = name_match.group(1).strip()
        if val.lower() not in ['[not provided]', '[不明]', 'unknown', 'n/a']:
            name = val
            
    # Extract Location/Address
    location = "Unknown"
    addr_match = re.search(r'(?:Address|Location|住所)[:：]\s*(.+?)(?:\n|$)', objective, re.IGNORECASE)
    if addr_match:
        val = addr_match.group(1).strip()
        if val.lower() not in ['[not provided]', '[不明]', 'unknown', 'n/a']:
            location = val
            
    return {
        'name': name,
        'location': location
    }

def normalize_text(text: str) -> str:
    """Normalize text for rough comparison"""
    if not text: return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def main():
    print(f"\n{BOLD}STARTING EVALUATION OF {len(EVALUATED_CALLS)} CALLS{RESET}")
    print("=" * 70)
    
    results = []
    
    for i, call_data in enumerate(EVALUATED_CALLS):
        call_id = call_data['call_id']
        transcript = call_data['text']
        
        print(f"\nProcessing {i+1}/{len(EVALUATED_CALLS)}: {BLUE}{call_id}{RESET}...")
        
        start_time = time.time()
        
        # 1. Extract SOAP
        try:
            soap = soap_extractor.extract(transcript)
        except Exception as e:
            print(f"{RED}SOAP Extraction failed: {e}{RESET}")
            soap = {'subjective': '', 'objective': '', 'assessment': '', 'plan': ''}
            
        # 2. Classify Urgency
        try:
            urgency_result = urgency_classifier.classify(transcript, soap)
            urgency_level = urgency_result['level'].lower()
        except Exception as e:
            print(f"{RED}Urgency Classification failed: {e}{RESET}")
            urgency_level = "error"
            
        # 3. Extract Metadata
        metadata = extract_metadata_from_soap(soap)
        
        duration = time.time() - start_time
        
        # COMPARE
        expected_urgency = call_data.get('expected_urgency', '').lower()
        expected_name = call_data.get('expected_agent', '').lower()
        expected_location = call_data.get('expected_location', '').lower()
        
        extracted_name = metadata['name'].lower()
        extracted_location = metadata['location'].lower()
        
        # Fuzzy match for name and location (contains)
        name_match = expected_name in extracted_name or extracted_name in expected_name
        # Remove "unknown" false positives
        if expected_name == "unknown" and extracted_name == "unknown": name_match = True
        
        # Location fuzzy match
        # Often location is "123 Main St" vs "123 Main St, Apt 4"
        loc_match = False
        if expected_location and extracted_location:
            # Check overlap
            if expected_location in extracted_location or extracted_location in expected_location:
                loc_match = True
            # Check simplified (remove punctuation)
            norm_exp = re.sub(r'[^\w\s]', '', expected_location)
            norm_ext = re.sub(r'[^\w\s]', '', extracted_location)
            if norm_exp in norm_ext or norm_ext in norm_exp:
                loc_match = True
        elif not expected_location and not extracted_location:
            loc_match = True

        # Urgency match
        urgency_match = urgency_level == expected_urgency
        
        result = {
            'call_id': call_id,
            'urgency': {
                'expected': expected_urgency,
                'actual': urgency_level,
                'match': urgency_match
            },
            'name': {
                'expected': call_data.get('expected_agent', 'N/A'),
                'actual': metadata['name'],
                'match': name_match
            },
            'location': {
                'expected': call_data.get('expected_location', 'N/A'),
                'actual': metadata['location'],
                'match': loc_match
            },
            'duration': duration
        }
        results.append(result)
        
        # Print immediate status
        status_icon = f"{GREEN}✓{RESET}" if (urgency_match and name_match and loc_match) else f"{RED}✗{RESET}"
        print(f"  {status_icon} Urgency: {expected_urgency} vs {urgency_level} | Time: {duration:.1f}s")
        if not urgency_match:
            print(f"    {RED}Urgency Mismatch!{RESET} Expected: {expected_urgency}, Got: {urgency_level}")
        if not name_match:
            print(f"    {YELLOW}Name Mismatch:{RESET} Exp '{call_data.get('expected_agent')}' vs Act '{metadata['name']}'")
        if not loc_match:
            print(f"    {YELLOW}Loc Mismatch:{RESET} Exp '{call_data.get('expected_location')}' vs Act '{metadata['location']}'")

    # FINAL REPORT
    print("\n" + "=" * 70)
    print(f"{BOLD}EVALUATION SUMMARY{RESET}")
    print("=" * 70)
    
    total = len(results)
    urgency_correct = sum(1 for r in results if r['urgency']['match'])
    name_correct = sum(1 for r in results if r['name']['match'])
    location_correct = sum(1 for r in results if r['location']['match'])
    
    print(f"Total Calls:      {total}")
    print(f"Urgency Accuracy: {urgency_correct}/{total} ({urgency_correct/total*100:.1f}%)")
    print(f"Name Extraction:  {name_correct}/{total} ({name_correct/total*100:.1f}%)")
    print(f"Location Ex.:     {location_correct}/{total} ({location_correct/total*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print(f"{BOLD}DETAILED MISMATCHES{RESET}")
    print("=" * 70)
    
    for r in results:
        if not (r['urgency']['match'] and r['name']['match'] and r['location']['match']):
            print(f"\n{BOLD}{r['call_id']}{RESET}")
            if not r['urgency']['match']:
                print(f"  {RED}Urgency:{RESET} Expected {r['urgency']['expected']} != {r['urgency']['actual']}")
            if not r['name']['match']:
                print(f"  {YELLOW}Name:{RESET}    Expected {r['name']['expected']} != {r['name']['actual']}")
            if not r['location']['match']:
                print(f"  {YELLOW}Location:{RESET} Expected {r['location']['expected']} != {r['location']['actual']}")

if __name__ == "__main__":
    main()
