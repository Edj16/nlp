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
The Employee is hired for the position of {position}.
Place of Work: {place_of_work}

ARTICLE 2 - COMPENSATION
2.1 Basic Salary: PHP {salary} per month
2.2 13th Month Pay as mandated by Philippine law
2.3 Other benefits: {benefits}

ARTICLE 3 - EMPLOYMENT PERIOD
Employment Type: {employment_type}
Start Date: {start_date}

ARTICLE 4 - WORKING HOURS
Standard working hours: {work_hours}

ARTICLE 5 - LEAVES
5.1 Vacation Leave: As per Labor Code
5.2 Sick Leave: As per Labor Code
5.3 Other leaves as mandated by law

ARTICLE 6 - TERMINATION
6.1 By either party with thirty (30) days notice
6.2 Just causes as defined in the Labor Code
"""

        # Add special clauses if any
        if special_clauses:
            contract += "\nARTICLE 7 - SPECIAL PROVISIONS\n\n"
            for i, clause in enumerate(special_clauses, 1):
                contract += f"7.{i} {clause}\n\n"

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
"""
        
        return contract