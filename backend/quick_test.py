#!/usr/bin/env python3
"""
Quick Test Script for Contract Agent
Runs a subset of critical tests for rapid development feedback
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.contract_agent import ProperLLMAgent

def quick_test():
    """Run quick tests"""
    print("="*60)
    print("QUICK TEST - Contract Agent")
    print("="*60)
    
    agent = ProperLLMAgent()
    
    print(f"\n✓ Agent initialized")
    print(f"  LLM Available: {'Yes' if agent.llm_available else 'No'}")
    print(f"  Laws Loaded: {len(agent.ph_laws)}")
    
    # Test 1: Intent Detection
    print("\n[1] Testing Intent Detection...")
    result = agent.process_message("Hello", session_id="quick_test")
    assert result.get('intent') == 'GREETING', "Greeting intent failed"
    print("  ✓ Greeting intent")
    
    result = agent.process_message("I need an employment contract", session_id="quick_test2")
    assert result.get('intent') == 'CREATE_CONTRACT', "Create contract intent failed"
    print("  ✓ Create contract intent")
    
    # Test 2: Contract Type Detection
    print("\n[2] Testing Contract Type Detection...")
    types = ['EMPLOYMENT', 'PARTNERSHIP', 'LEASE', 'BUY_SELL']
    messages = [
        "I need an employment contract",
        "Create a partnership agreement",
        "I want to lease a property",
        "I need a buy and sell contract"
    ]
    
    for msg, expected_type in zip(messages, types):
        detected = agent._detect_contract_type(msg)
        assert detected == expected_type, f"Type detection failed for {expected_type}"
        print(f"  ✓ {expected_type} detection")
    
    # Test 3: Entity Extraction
    print("\n[3] Testing Entity Extraction...")
    message = "Employer: ABC Corp, Employee: John Doe, Salary: 50000"
    extracted = agent._extract_entities_c3(message, 'EMPLOYMENT')
    assert len(extracted) > 0, "Entity extraction returned empty"
    print(f"  ✓ Extracted {len(extracted)} entities")
    
    # Test 4: Required Fields
    print("\n[4] Testing Required Fields Detection...")
    for contract_type in types:
        fields = agent._get_required_fields(contract_type)
        assert len(fields) > 0, f"No fields detected for {contract_type}"
        print(f"  ✓ {contract_type}: {len(fields)} fields")
    
    # Test 5: Formatting
    print("\n[5] Testing Formatting...")
    assert agent._format_name("john doe") == "John Doe", "Name formatting failed"
    print("  ✓ Name formatting")
    
    formatted_money = agent._format_money("50000")
    assert "50" in formatted_money, "Money formatting failed"
    print("  ✓ Money formatting")
    
    # Test 6: State Management
    print("\n[6] Testing State Management...")
    session = agent._get_or_create_session("quick_test_state")
    session['contract_type'] = 'EMPLOYMENT'
    state = agent._update_state_c2(session, {'employer_name': 'ABC Corp'})
    assert state is not None, "State update failed"
    print("  ✓ State management")
    
    print("\n" + "="*60)
    print("✓ ALL QUICK TESTS PASSED")
    print("="*60)
    return True

if __name__ == '__main__':
    try:
        quick_test()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
