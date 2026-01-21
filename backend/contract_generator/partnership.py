"""
Partnership Contract Generator
Generates partnership agreements compliant with Philippine law
"""
from typing import Dict, List
from datetime import datetime

class ContractGenerator:
    """Generate Partnership Contract"""
    
    def generate(
        self,
        details: Dict,
        special_clauses: List[str],
        applicable_laws: List[Dict]
    ) -> str:
        """
        Generate partnership contract content
        
        Required details:
        - partner_names: list of partner names
        - business_name: name of partnership
        - partnership_type: 'general' or 'limited'
        - capital_contribution: amount or dict of amounts
        - profit_sharing_ratio: e.g., "50:50"
        - business_address: address
        """
        
        # Extract details with defaults
        partners = details.get('partner_names', ['[FIRST PARTNER]', '[SECOND PARTNER]'])

        if isinstance(partners, str):
            if partners.startswith('[') and partners.endswith(']'):
                import ast
                try:
                    partners = ast.literal_eval(partners)
                except:
                    partners = [p.strip() for p in partners.strip('[]').replace("'", "").split(',')]
            else:
                partners = [partners]
        business_name = details.get('business_name', '[BUSINESS NAME]')
        partnership_type = details.get('partnership_type', 'general').title()
        capital = details.get('capital_contribution', '[CAPITAL AMOUNT]')
        profit_ratio = details.get('profit_sharing_ratio', '[RATIO]')
        address = details.get('business_address', '[BUSINESS ADDRESS]')
        date_signed = details.get('date', datetime.now().strftime('%B %d, %Y'))
        principal_office = details.get('principal_office', address)
        
        # Build contract content
        content = f"""PARTNERSHIP AGREEMENT

This {partnership_type} Partnership Agreement ("Agreement") is entered into on {date_signed}.

BETWEEN:

"""
        
        # Add all partners
        for i, partner in enumerate(partners, 1):
            content += f"{self._ordinal(i)} Party: {partner}\n"
        
        content += f"""
Hereinafter collectively referred to as the "Partners."

WHEREAS the Partners desire to enter into a partnership for the purpose of conducting business under the name "{business_name}";

NOW, THEREFORE, in consideration of the mutual covenants and agreements herein contained, the Partners agree as follows:

ARTICLE 1 - NAME, PRINCIPAL OFFICE, AND PLACE OF BUSINESS

1.1 The name of the partnership shall be "{business_name}".

1.2 The principal office of the partnership shall be located at:
{principal_office}

1.3 The principal place of business shall be located at:
{address}, or such other place as the Partners may determine.

ARTICLE 2 - PURPOSE AND NATURE OF BUSINESS

2.1 The partnership is formed for the purpose of {details.get('business_purpose', 'conducting lawful business activities')}.

2.2 This is a {partnership_type} Partnership as defined under Philippine law.

ARTICLE 3 - CAPITAL CONTRIBUTIONS

"""
        
        # Handle capital contributions
        if isinstance(capital, dict):
            for partner, amount in capital.items():
                content += f"3.1 {partner} shall contribute: PHP {amount}\n"
        else:
            content += f"3.1 Each Partner shall contribute capital totaling: PHP {capital}\n"
        
        content += f"""
3.2 Additional capital contributions may be required with the unanimous consent of all Partners.

ARTICLE 4 - PROFIT AND LOSS DISTRIBUTION

4.1 Profits and losses shall be shared among the Partners in the following ratio: {profit_ratio}

4.2 Distributions shall be made quarterly unless otherwise agreed by all Partners.

ARTICLE 5 - MANAGEMENT AND DUTIES

5.1 Each Partner shall have equal rights in the management of the partnership business.

5.2 Major decisions requiring unanimous consent include:
    a) Admission of new partners
    b) Sale of partnership assets
    c) Dissolution of partnership
    d) Amendment of this Agreement

5.3 All Partners shall devote reasonable time and effort to the partnership business.

ARTICLE 6 - BOOKS AND RECORDS

6.1 Proper books of account shall be maintained at the principal place of business.

6.2 Each Partner shall have access to inspect the books and records at reasonable times.

ARTICLE 7 - BANKING

7.1 The partnership shall maintain bank accounts in the partnership name.

7.2 All checks and withdrawals shall require signatures of at least two (2) Partners.

ARTICLE 8 - TERMINATION AND DISSOLUTION

8.1 The partnership may be dissolved:
    a) By mutual written consent of all Partners
    b) Upon completion of the partnership purpose
    c) By operation of law
    d) Upon death or incapacity of a Partner (unless otherwise agreed)

8.2 Upon dissolution, assets shall be liquidated and distributed according to capital contributions after payment of debts.

ARTICLE 9 - ADMISSION AND WITHDRAWAL OF PARTNERS

9.1 New partners may be admitted only with unanimous consent of existing Partners.

9.2 A Partner wishing to withdraw must provide sixty (60) days written notice.

"""
        
        # Add special clauses if any
        if special_clauses:
            content += "ARTICLE 10 - SPECIAL PROVISIONS\n\n"
            for i, clause in enumerate(special_clauses, 1):
                content += f"10.{i} {clause}\n\n"
        
        # Add applicable laws section
        content += "\nAPPLICABLE PHILIPPINE LAWS:\n\n"
        content += "This Agreement is governed by and construed in accordance with Philippine law, particularly:\n\n"
        
        for law in applicable_laws[:5]:  # Include top 5 relevant laws
            content += f"• Article {law.get('article', 'N/A')}: {law.get('rule', 'N/A')[:100]}...\n"
        
        content += """

ARTICLE 11 - MISCELLANEOUS

11.1 This Agreement constitutes the entire understanding between the Partners.

11.2 Any amendments must be in writing and signed by all Partners.

11.3 This Agreement shall be binding upon the heirs, executors, and assigns of the Partners.

11.4 If any provision is found invalid, the remaining provisions shall continue in effect.

11.5 This Agreement shall be governed by the laws of the Republic of the Philippines.

IN WITNESS WHEREOF, the Partners have executed this Agreement on the date first written above.

"""
        
        # Signature blocks
        for partner in partners:
            content += f"""
_________________________
{partner}
Partner

"""
        
        content += f"""
ACKNOWLEDGMENT

REPUBLIC OF THE PHILIPPINES  )
                             ) S.S.
{address.split(',')[-1].strip() if ',' in address else '[CITY/PROVINCE]'}  )

BEFORE ME, a Notary Public for and in the above jurisdiction, personally appeared:

"""
        
        for partner in partners:
            content += f"{partner} - with identification\n"
        
        content += f"""
known to me and to me known to be the same persons who executed the foregoing instrument and acknowledged to me that the same is their free and voluntary act and deed.

WITNESS MY HAND AND SEAL on this {date_signed}.


                                    _________________________
                                    NOTARY PUBLIC

Doc. No. _____
Page No. _____
Book No. _____
Series of {datetime.now().year}
"""
        
        return content
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"