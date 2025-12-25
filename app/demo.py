# demo_interactive.py
import time

class KontrataDemo:
    def __init__(self):
        self.contract_data = {}
        
    def generate_contract_flow(self):
        print("🤖 KontrataPH: Hello! I can help you create a partnership contract.")
        print("   Let me gather some information.\n")
        time.sleep(1)
        
        # Collect information
        questions = {
            'party1_name': "What is the name of the first party?",
            'party2_name': "What is the name of the second party?",
            'business_nature': "What is the nature of your partnership business?",
            'duration': "What is the contract duration? (e.g., '1 year', '2 years')",
            'capital_contribution': "What are the capital contributions? (e.g., 'Party A: 500,000 PHP, Party B: 500,000 PHP')",
            'profit_sharing': "How will profits be shared? (e.g., '50-50', '60-40')"
        }
        
        for key, question in questions.items():
            print(f"🤖 KontrataPH: {question}")
            self.contract_data[key] = input("👤 You: ").strip()
            
            # Validation example
            if key == 'duration' and not any(word in self.contract_data[key].lower() for word in ['year', 'month']):
                print("\n⚠️  KontrataPH: Invalid duration format. Please specify in years or months (e.g., '1 year').")
                self.contract_data[key] = input("👤 You: ").strip()
            print()
        
        # Ask about special conditions
        print("🤖 KontrataPH: Do you have any special conditions? (yes/no)")
        special = input("👤 You: ").strip().lower()
        
        if special == 'yes':
            print("🤖 KontrataPH: Please describe the special conditions:")
            self.contract_data['special_conditions'] = input("👤 You: ").strip()
        
        # Generate contract
        print("\n" + "="*60)
        print("📄 GENERATING CONTRACT...")
        print("="*60 + "\n")
        time.sleep(2)
        
        self.display_contract()
        self.display_legal_protection()
    
    def display_contract(self):
        contract = f"""
PARTNERSHIP AGREEMENT

This Partnership Agreement is entered into on {self.get_current_date()}

BETWEEN:
    {self.contract_data['party1_name']} (hereinafter "Party A")
AND:
    {self.contract_data['party2_name']} (hereinafter "Party B")

1. NATURE OF PARTNERSHIP
   The parties agree to enter into a partnership for {self.contract_data['business_nature']}

2. DURATION
   This partnership shall be effective for {self.contract_data['duration']} from the date hereof.

3. CAPITAL CONTRIBUTION
   {self.contract_data['capital_contribution']}

4. PROFIT AND LOSS SHARING
   Profits and losses shall be shared: {self.contract_data['profit_sharing']}

5. MANAGEMENT
   Both parties shall have equal management rights unless otherwise agreed.

6. DISSOLUTION
   This partnership may be dissolved by mutual written consent or as provided by law.
"""
        
        if 'special_conditions' in self.contract_data:
            contract += f"\n7. SPECIAL CONDITIONS\n   {self.contract_data['special_conditions']}\n"
        
        contract += """
IN WITNESS WHEREOF, the parties have executed this agreement.

_________________                    _________________
Party A Signature                    Party B Signature
"""
        print(contract)
    
    def display_legal_protection(self):
        print("\n" + "="*60)
        print("⚖️  LEGAL PROTECTION ANALYSIS")
        print("="*60 + "\n")
        
        protections = [
            {
                'scenario': 'If one party fails to contribute the agreed capital',
                'law': 'Article 1786, Civil Code of the Philippines',
                'protection': 'The other party may dissolve the partnership or compel contribution through legal action.'
            },
            {
                'scenario': 'If one party mismanages partnership funds',
                'law': 'Article 1794, Civil Code of the Philippines',
                'protection': 'Partners are bound to contribute losses and cannot exempt themselves from liability for fraud or willful misconduct.'
            },
            {
                'scenario': 'If partnership duration expires',
                'law': 'Article 1785, Civil Code of the Philippines',
                'protection': f'Partnership automatically dissolves after {self.contract_data["duration"]} unless renewed by mutual agreement.'
            }
        ]
        
        for i, p in enumerate(protections, 1):
            print(f"✅ Scenario {i}: {p['scenario']}")
            print(f"   📜 Protected by: {p['law']}")
            print(f"   🛡️  Protection: {p['protection']}\n")
    
    def get_current_date(self):
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

if __name__ == "__main__":
    demo = KontrataDemo()
    demo.generate_contract_flow()