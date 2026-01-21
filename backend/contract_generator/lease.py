"""Lease Contract Generator"""
from typing import Dict, List
from datetime import datetime

class ContractGenerator:
    def generate(self, details: Dict, special_clauses: List[str], applicable_laws: List[Dict]) -> str:
        lessor = details.get('lessor_name', '[LESSOR NAME]')
        lessee = details.get('lessee_name', '[LESSEE NAME]')
        property_addr = details.get('property_address', '[PROPERTY ADDRESS]')
        property_desc = details.get('property_description', '[PROPERTY DESCRIPTION]')
        rental = details.get('rental_amount', '[RENTAL AMOUNT]')
        period = details.get('lease_period', '[LEASE PERIOD]')
        payment_terms = details.get('payment_terms', 'monthly in advance')
        
        return f"""LEASE AGREEMENT

This Lease Agreement is entered into on {datetime.now().strftime('%B %d, %Y')}.

BETWEEN:
LESSOR: {lessor}
LESSEE: {lessee}

ARTICLE 1 - LEASED PROPERTY
The Lessor agrees to lease to the Lessee the property located at:
{property_addr}

ARTICLE 1.1 - PROPERTY DESCRIPTION
{property_desc}

ARTICLE 2 - LEASE PERIOD
The lease period shall be for {period}, commencing on the date hereof.

ARTICLE 3 - RENTAL AND PAYMENT
3.1 Monthly Rental: PHP {rental}
3.2 Payment Terms: {payment_terms}
3.3 Security Deposit: Equivalent to two (2) months rent

ARTICLE 4 - USE OF PROPERTY
The Lessee shall use the property for {details.get('property_use', 'residential/commercial')} purposes only.

ARTICLE 5 - MAINTENANCE AND REPAIRS
5.1 The Lessee shall maintain the property in good condition.
5.2 Major repairs shall be the responsibility of the Lessor.

ARTICLE 6 - TERMINATION
Either party may terminate with thirty (30) days written notice.

{chr(10).join([f'SPECIAL CLAUSE: {clause}' for clause in special_clauses]) if special_clauses else ''}

APPLICABLE LAWS:
{chr(10).join([f"• Article {law.get('article')}: {law.get('rule', '')[:80]}..." for law in applicable_laws[:3]])}

IN WITNESS WHEREOF:

_________________          _________________
{lessor}                   {lessee}
LESSOR                     LESSEE
"""