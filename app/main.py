"""
KontrataPH - Intelligent Contract Analysis and Generation Platform
Main application file
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_loader import load_law
from app.validator import validate_inputs
from app.prompt_builder import build_contract_prompt, build_analysis_prompt
from app.contract_generator import generate_contract
from app.pdf_parser import extract_text

def generate_contract_flow():
    """
    Flow for generating a new contract
    """
    print("="*60)
    print("KontrataPH - Contract Generation")
    print("="*60)
    
    # Load law data
    print("\n📚 Loading Philippine Civil Code (Partnership)...")
    law = load_law("data/laws/civil_code_partnership.json")
    print(f"✓ Loaded {len(law['articles'])} articles")
    
    # Example user inputs (in real app, get from user input/form)
    print("\n📝 User Input:")
    user_inputs = {
        "partners": "Juan dela Cruz and Maria Santos",
        "capital_contribution": "60/40",
        "profit_sharing": "60/40",
        "duration": "5 years",
        "business_purpose": "Software Development Services"
    }
    
    for key, value in user_inputs.items():
        print(f"   {key}: {value}")
    
    # Validate inputs
    print("\n🔍 Validating inputs against legal requirements...")
    errors = validate_inputs(user_inputs, law)
    
    if errors:
        print("\n❌ Invalid inputs found:")
        for e in errors:
            print(f"   • Field '{e['field']}': {e['reason']}")
        return
    
    print("✓ All inputs are valid!")
    
    # Generate contract
    print("\n⚙️  Generating contract with LLM...")
    prompt = build_contract_prompt("Partnership", user_inputs, law)
    
    # Uncomment when you have the model loaded:
    # contract = generate_contract(prompt)
    
    # For now, show the prompt (remove this in production)
    print("\n" + "="*60)
    print("GENERATED PROMPT FOR LLM:")
    print("="*60)
    print(prompt[:500] + "...\n[truncated for display]")
    
    # In production, replace the above with:
    # print("\n" + "="*60)
    # print("GENERATED CONTRACT:")
    # print("="*60)
    # print(contract)


def analyze_contract_flow(contract_path=None):
    """
    Flow for analyzing an existing contract
    """
    print("="*60)
    print("KontrataPH - Contract Analysis")
    print("="*60)
    
    # Load law data
    print("\n📚 Loading Philippine Civil Code (Partnership)...")
    law = load_law("data/laws/civil_code_partnership.json")
    print(f"✓ Loaded {len(law['articles'])} articles")
    
    # Extract text from PDF or use sample
    if contract_path and contract_path.endswith('.pdf'):
        print(f"\n📄 Extracting text from: {contract_path}")
        contract_text = extract_text(contract_path)
    else:
        # Sample contract for testing
        contract_text = """
        PARTNERSHIP AGREEMENT
        
        This Partnership Agreement is entered into by Juan dela Cruz and Maria Santos.
        
        The partners agree to contribute capital in the ratio of 70/30.
        All profits shall be distributed to Juan dela Cruz only.
        The partnership shall last indefinitely.
        
        Signed this 1st day of January 2024.
        """
    
    print("\n✓ Contract text extracted")
    print(f"   Length: {len(contract_text)} characters")
    
    # Build analysis prompt
    print("\n🔍 Analyzing contract for legal compliance...")
    prompt = build_analysis_prompt(contract_text, law)
    
    # Uncomment when you have the model loaded:
    # analysis = generate_contract(prompt)
    
    # For now, show the prompt structure
    print("\n" + "="*60)
    print("ANALYSIS PROMPT SENT TO LLM:")
    print("="*60)
    print(prompt[:500] + "...\n[truncated for display]")
    
    # In production, replace with:
    # print("\n" + "="*60)
    # print("CONTRACT ANALYSIS:")
    # print("="*60)
    # print(analysis)


def main():
    """
    Main application entry point
    """
    print("\n🇵🇭 KontrataPH - Intelligent Contract Platform\n")
    
    # Demonstrate both flows
    mode = input("Choose mode:\n1. Generate Contract\n2. Analyze Contract\nEnter (1 or 2): ").strip()
    
    if mode == "1":
        generate_contract_flow()
    elif mode == "2":
        pdf_path = input("Enter path to contract PDF (or press Enter for sample): ").strip()
        analyze_contract_flow(pdf_path if pdf_path else None)
    else:
        print("Invalid option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()