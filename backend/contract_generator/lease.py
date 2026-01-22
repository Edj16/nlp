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
The Lessor agrees to lease to the Lessee the property located at: {property_addr}. Property Description: {property_desc}. The property is determinate and fit for lease, in accordance with Article 1643 of the Civil Code.

ARTICLE 1.1 - PROPERTY DESCRIPTION
{property_desc}

ARTICLE 2 - LEASE PERIOD
The lease period shall be for {period}, commencing on the date hereof, subject to Article 1670 of the Civil Code regarding tacit renewal. No lease may exceed 99 years (Article 1643).

ARTICLE 3 - RENTAL AND PAYMENT
3.1 Monthly Rental: PHP {rental}, payable in accordance with Article 1657 of the Civil Code.

3.2 Payment Terms: {payment_terms}. Payment shall be at the Lessor's residence or place of business unless otherwise stipulated.

3.3 Security Deposit: Equivalent to two (2) months rent, to be returned upon termination as per Article 1676 of the Civil Code. For rent-controlled residential units under RA 9653, security deposit and advance rent shall not exceed one month.

3.4 Rent Increases: For residential leases under RA 9653, annual increases shall not exceed 7% if the tenant remains in possession (Section 4).

ARTICLE 4 - USE OF PROPERTY
The Lessee shall use the property for {details.get('property_use', 'residential/commercial')} purposes only, and shall not sublease without written consent (Article 1650) or use for illegal purposes.

ARTICLE 5 - MAINTENANCE AND REPAIRS
5.1 The Lessee shall maintain the property in good condition and make minor repairs, pursuant to Article 1654 of the Civil Code.

5.2 Major repairs shall be the responsibility of the Lessor, as required under Article 1654. The Lessee may suspend rent if the Lessor fails to make necessary repairs (Article 1658).

ARTICLE 6 - LESSOR OBLIGATIONS
6.1 Deliver the property fit for intended use (Article 1654).

6.2 Make necessary repairs to maintain the property (Article 1654).

6.3 Maintain the Lessee in peaceful enjoyment (Article 1654).

6.4 Answer for warranty against hidden defects (Article 1654).

ARTICLE 7 - LESSEE OBLIGATIONS
7.1 Pay the rent at agreed time and place (Article 1657).

7.2 Use the property as a diligent father of a family (Article 1657).

7.3 Pay for expenses of the deed of lease (Article 1657).

7.4 Return the property upon termination (Article 1665).

7.5 Inform the Lessor of urgent repairs needed (Article 1654).

ARTICLE 8 - TERMINATION
8.1 Expiration of fixed term (Article 1669).

8.2 Non-payment of rent (Article 1673).

8.3 Violation of contract conditions (Article 1673).

8.4 Use for illegal/immoral purpose (Article 1673).

8.5 Imminent danger to life or health (Article 1660).

8.6 For rent-controlled units, legitimate need of owner or sale (RA 9653, Section 9), with 3 months notice.

{chr(10).join([f'SPECIAL CLAUSE: {clause}' for clause in special_clauses]) if special_clauses else ''}

APPLICABLE LAWS:
{chr(10).join([f"• Article {law.get('article')}: {law.get('rule', '')[:80]}..." for law in applicable_laws[:3]])}

IN WITNESS WHEREOF:

_________________          _________________
{lessor}                   {lessee}
LESSOR                     LESSEE

Disclaimer: This template is for informational purposes only and does not constitute legal advice. It is recommended to consult a qualified attorney to ensure compliance with applicable laws and to tailor the contract to your specific circumstances.
"""