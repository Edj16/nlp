"""
contract_generator/employment.py - FIXED VERSION
All fields properly use details.get() so they're auto-detected
"""
from typing import Dict, List
from datetime import datetime

class ContractGenerator:
    def generate(self, details: Dict, special_clauses: List[str], applicable_laws: List[Dict]) -> str:
        # Extract all fields from details
        employer = details.get('employer_name', '[EMPLOYER]')
        employee = details.get('employee_name', '[EMPLOYEE]')
        position = details.get('position', '[POSITION]')
        salary = details.get('salary', '[SALARY]')
        start_date = details.get('start_date', datetime.now().strftime('%B %d, %Y'))
        employment_type = details.get('employment_type', 'Regular')
        work_hours = details.get('work_hours', '8 hours per day, Monday to Friday')
        benefits = details.get('benefits', 'As per company policy')
        place_of_work = details.get('place_of_work', '[WORK LOCATION]')  # ✅ Now detectable!
        
        contract = f"""EMPLOYMENT CONTRACT

This Employment Contract is entered into on {datetime.now().strftime('%B %d, %Y')}.

BETWEEN:
EMPLOYER: {employer}
EMPLOYEE: {employee}

ARTICLE 1 - POSITION AND DUTIES
The Employee is hired for the position of {position}, with duties to be performed faithfully and efficiently, in accordance with Article 1709 of the Civil Code and Book III of the Labor Code. Place of Work: {place_of_work}.

ARTICLE 2 - COMPENSATION
2.1 Basic Salary: PHP {salary} per month, subject to minimum wage laws under Article 124 of the Labor Code and Regional Tripartite Wages and Productivity Boards (RTWPBs) per RA 6727.

2.2 13th Month Pay: As mandated by Presidential Decree No. 851, equivalent to 1/12 of the annual basic salary, due on or before December 24.

2.3 Other benefits: {benefits}, including mandatory contributions to SSS (RA 11199), PhilHealth (RA 11223), and Pag-IBIG (RA 9679). Overtime pay at 125% for regular days and 130% for rest days/holidays (Article 87 of the Labor Code).

ARTICLE 3 - EMPLOYMENT PERIOD
Employment Type: {employment_type} (Regular under Article 280 of the Labor Code unless probationary or project-based). Start Date: {start_date}. Probationary period shall not exceed 6 months (Article 281).

ARTICLE 4 - WORKING HOURS
Standard working hours: {work_hours}, not to exceed 8 hours per day or 48 hours per week (Article 83 of the Labor Code). At least 24 consecutive hours rest per week (Article 91).

ARTICLE 5 - LEAVES
5.1 Service Incentive Leave: 5 days per year after 1 year of service (Article 95 of the Labor Code).

5.2 Maternity Leave: 105 days (120 for solo parents) under RA 11210.

5.3 Paternity Leave: 7 days for married male employees under RA 8187.

5.4 Other leaves: Parental leave for solo parents (7 days under RA 8972), special leave for women (2 days under RA 9710), and VAWC leave (10 days under RA 9262).

ARTICLE 6 - TERMINATION
6.1 Just Causes: Serious misconduct, gross neglect, fraud, or analogous causes (Article 297 of the Labor Code), requiring due process (two written notices and hearing).

6.2 Authorized Causes: Redundancy, retrenchment, closure, or disease (Article 298), with 30 days notice to employee and DOLE, plus separation pay (1 month per year of service).

6.3 Security of Tenure: Regular employees cannot be dismissed without just or authorized cause (Article 294).

ARTICLE 7 - SPECIAL PROTECTIONS
7.1 Non-Diminution of Benefits: Benefits cannot be reduced once granted (Article 100).

7.2 Equal Pay for Equal Work: No discrimination in wages (Article 135).

7.3 Anti-Discrimination: Protection against age, sex, religion, or other discrimination (Article 135, RA 10911).

7.4 Data Privacy: Employee personal data protected (RA 10173).

7.5 Anti-Sexual Harassment: Workplace free from harassment (RA 7877, RA 11313).

"""

        # Add special clauses if any
        if special_clauses:
            contract += "\nARTICLE 8 - SPECIAL PROVISIONS\n\n"
            for i, clause in enumerate(special_clauses, 1):
                contract += f"8.{i} {clause}\n\n"

        # Add applicable laws
        if applicable_laws:
            contract += "\nAPPLICABLE LABOR LAWS:\n"
            for law in applicable_laws[:3]:
                contract += f"• Article {law.get('article', 'N/A')}: {law.get('rule', 'N/A')[:80]}...\n"

        # Signature block
        contract += f"""

IN WITNESS WHEREOF, the parties have executed this Contract on the date first written above.

_________________          _________________
{employer}                 {employee}
EMPLOYER                   EMPLOYEE

Disclaimer: This template is for informational purposes only and does not constitute legal advice. It is recommended to consult a qualified attorney to ensure compliance with applicable laws and to tailor the contract to your specific circumstances.
"""
        
        return contract