#!/usr/bin/env python3
"""
Test script for evaluated_text_data.py
Validates the structure and content of the EVALUATED_CALLS dataset
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.text.evaluated_text_data import EVALUATED_CALLS

# ANSI color codes for better output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")

def test_data_structure():
    """Test the overall data structure"""
    print("\n" + "="*70)
    print("TESTING DATA STRUCTURE")
    print("="*70)
    
    # Test 1: Check if EVALUATED_CALLS is a list
    if not isinstance(EVALUATED_CALLS, list):
        print_error("EVALUATED_CALLS is not a list")
        return False
    print_success(f"EVALUATED_CALLS is a list with {len(EVALUATED_CALLS)} calls")
    
    # Test 2: Check if list is not empty
    if len(EVALUATED_CALLS) == 0:
        print_error("EVALUATED_CALLS is empty")
        return False
    print_success(f"Dataset contains {len(EVALUATED_CALLS)} emergency calls")
    
    return True

def test_call_structure():
    """Test each call's structure"""
    print("\n" + "="*70)
    print("TESTING INDIVIDUAL CALL STRUCTURES")
    print("="*70)
    
    required_fields = [
        'call_id',
        'text',
        'expected_urgency',
        'expected_type',
        'expected_location',
        'expected_agent',
        'expected_soap'
    ]
    
    soap_fields = ['subjective', 'objective', 'assessment', 'plan']
    
    all_passed = True
    
    for i, call in enumerate(EVALUATED_CALLS):
        call_id = call.get('call_id', f'UNKNOWN_{i}')
        print(f"\n{BLUE}Testing {call_id}...{RESET}")
        
        # Check required fields
        for field in required_fields:
            if field not in call:
                print_error(f"  Missing field: {field}")
                all_passed = False
            elif not call[field]:
                print_warning(f"  Empty field: {field}")
            else:
                print_success(f"  Has {field}")
        
        # Check SOAP structure
        if 'expected_soap' in call:
            soap = call['expected_soap']
            if isinstance(soap, dict):
                for soap_field in soap_fields:
                    if soap_field not in soap:
                        print_error(f"  Missing SOAP field: {soap_field}")
                        all_passed = False
                    elif not soap[soap_field]:
                        print_warning(f"  Empty SOAP field: {soap_field}")
                    else:
                        print_success(f"  Has SOAP.{soap_field}")
            else:
                print_error(f"  expected_soap is not a dictionary")
                all_passed = False
    
    return all_passed

def test_urgency_levels():
    """Test urgency level values"""
    print("\n" + "="*70)
    print("TESTING URGENCY LEVELS")
    print("="*70)
    
    valid_urgencies = ['critical', 'high', 'medium', 'low']
    urgency_counts = {level: 0 for level in valid_urgencies}
    invalid_count = 0
    
    for call in EVALUATED_CALLS:
        urgency = call.get('expected_urgency', '')
        if urgency in valid_urgencies:
            urgency_counts[urgency] += 1
        else:
            invalid_count += 1
            print_error(f"{call.get('call_id')}: Invalid urgency '{urgency}'")
    
    print("\nUrgency Distribution:")
    for level, count in urgency_counts.items():
        print(f"  {level.capitalize()}: {count} calls")
    
    if invalid_count == 0:
        print_success("All urgency levels are valid")
        return True
    else:
        print_error(f"Found {invalid_count} invalid urgency levels")
        return False

def test_call_types():
    """Test call type values"""
    print("\n" + "="*70)
    print("TESTING CALL TYPES")
    print("="*70)
    
    valid_types = ['medical', 'fire', 'police']
    type_counts = {t: 0 for t in valid_types}
    invalid_count = 0
    
    for call in EVALUATED_CALLS:
        call_type = call.get('expected_type', '')
        if call_type in valid_types:
            type_counts[call_type] += 1
        else:
            invalid_count += 1
            print_error(f"{call.get('call_id')}: Invalid type '{call_type}'")
    
    print("\nCall Type Distribution:")
    for ctype, count in type_counts.items():
        print(f"  {ctype.capitalize()}: {count} calls")
    
    if invalid_count == 0:
        print_success("All call types are valid")
        return True
    else:
        print_error(f"Found {invalid_count} invalid call types")
        return False

def test_text_content():
    """Test text content quality"""
    print("\n" + "="*70)
    print("TESTING TEXT CONTENT QUALITY")
    print("="*70)
    
    all_passed = True
    
    for call in EVALUATED_CALLS:
        call_id = call.get('call_id', 'UNKNOWN')
        text = call.get('text', '')
        
        # Check minimum length
        if len(text) < 100:
            print_warning(f"{call_id}: Text is very short ({len(text)} chars)")
        
        # Check if it starts with "911"
        if not text.strip().startswith('911'):
            print_warning(f"{call_id}: Text doesn't start with '911'")
        
        # Check for dialogue format
        if '[' not in text or ']' not in text:
            print_warning(f"{call_id}: Text may not have proper dialogue format")
    
    print_success(f"Analyzed text content for {len(EVALUATED_CALLS)} calls")
    return all_passed

def test_location_data():
    """Test location data"""
    print("\n" + "="*70)
    print("TESTING LOCATION DATA")
    print("="*70)
    
    locations_found = 0
    missing_locations = []
    
    for call in EVALUATED_CALLS:
        call_id = call.get('call_id', 'UNKNOWN')
        location = call.get('expected_location', '')
        
        if location and len(location) > 0:
            locations_found += 1
        else:
            missing_locations.append(call_id)
    
    print(f"Calls with location: {locations_found}/{len(EVALUATED_CALLS)}")
    
    if missing_locations:
        print_warning(f"Missing locations in: {', '.join(missing_locations)}")
    else:
        print_success("All calls have location data")
    
    return len(missing_locations) == 0

def generate_summary():
    """Generate a summary report"""
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    print(f"\nTotal Calls: {len(EVALUATED_CALLS)}")
    
    # Call IDs
    call_ids = [call.get('call_id', 'UNKNOWN') for call in EVALUATED_CALLS]
    print(f"\nCall IDs: {', '.join(call_ids)}")
    
    # Urgency breakdown
    urgencies = {}
    for call in EVALUATED_CALLS:
        urgency = call.get('expected_urgency', 'unknown')
        urgencies[urgency] = urgencies.get(urgency, 0) + 1
    
    print("\nUrgency Breakdown:")
    for urgency, count in sorted(urgencies.items()):
        percentage = (count / len(EVALUATED_CALLS)) * 100
        print(f"  {urgency.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Average text length
    avg_length = sum(len(call.get('text', '')) for call in EVALUATED_CALLS) / len(EVALUATED_CALLS)
    print(f"\nAverage Call Text Length: {avg_length:.0f} characters")
    
    # SOAP completeness
    complete_soap = sum(1 for call in EVALUATED_CALLS 
                       if all(field in call.get('expected_soap', {}) 
                             for field in ['subjective', 'objective', 'assessment', 'plan']))
    print(f"\nCalls with Complete SOAP Notes: {complete_soap}/{len(EVALUATED_CALLS)}")

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*70}")
    print("EVALUATED_TEXT_DATA.PY TEST SUITE")
    print(f"{'='*70}{RESET}\n")
    
    tests = [
        ("Data Structure", test_data_structure),
        ("Call Structure", test_call_structure),
        ("Urgency Levels", test_urgency_levels),
        ("Call Types", test_call_types),
        ("Text Content", test_text_content),
        ("Location Data", test_location_data),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Generate summary
    generate_summary()
    
    # Final results
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BLUE}Overall: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{'='*70}")
        print("ALL TESTS PASSED! ✓")
        print(f"{'='*70}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'='*70}")
        print(f"SOME TESTS FAILED ({total - passed} failures)")
        print(f"{'='*70}{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
