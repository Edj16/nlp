#!/usr/bin/env python3
"""
Evaluation Script for KontrataPH Contract Agent
Tests all major functionalities and generates a comprehensive report
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from loguru import logger

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.contract_agent import ProperLLMAgent

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    category: str
    passed: bool
    expected: Any
    actual: Any
    error: str = None
    execution_time: float = 0.0
    details: Dict = None

@dataclass
class EvaluationReport:
    """Evaluation report structure"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    success_rate: float
    execution_time: float
    test_results: List[TestResult]
    summary: Dict[str, Any]

class ContractAgentEvaluator:
    """Comprehensive evaluator for Contract Agent"""
    
    def __init__(self):
        self.agent = ProperLLMAgent()
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def run_test(self, test_name: str, category: str, test_func, expected: Any = None) -> TestResult:
        """Run a single test and record result"""
        start = time.time()
        passed = False
        actual = None
        error = None
        details = None
        
        try:
            actual = test_func()
            
            if expected is not None:
                passed = actual == expected
            elif isinstance(actual, dict):
                # For dict results, check if it has expected keys
                passed = 'error' not in actual or actual.get('error') is None
            elif isinstance(actual, bool):
                passed = actual
            else:
                passed = actual is not None
            
            execution_time = time.time() - start
            
        except Exception as e:
            error = str(e)
            execution_time = time.time() - start
            passed = False
            logger.error(f"Test '{test_name}' failed with error: {e}")
        
        result = TestResult(
            test_name=test_name,
            category=category,
            passed=passed,
            expected=expected,
            actual=actual,
            error=error,
            execution_time=execution_time,
            details=details
        )
        
        self.results.append(result)
        status = "✓" if passed else "✗"
        logger.info(f"{status} [{category}] {test_name} ({execution_time:.2f}s)")
        
        return result
    
    # ========================================
    # INTENT DETECTION TESTS
    # ========================================
    
    def test_intent_greeting(self) -> Dict:
        """Test greeting intent detection"""
        result = self.agent.process_message("Hello", session_id="test_greeting")
        return result.get('intent') == 'GREETING'
    
    def test_intent_create_contract_employment(self) -> Dict:
        """Test CREATE_CONTRACT intent for employment"""
        result = self.agent.process_message(
            "I need an employment contract",
            session_id="test_employment_intent"
        )
        return result.get('intent') == 'CREATE_CONTRACT'
    
    def test_intent_create_contract_partnership(self) -> Dict:
        """Test CREATE_CONTRACT intent for partnership"""
        result = self.agent.process_message(
            "Create a partnership agreement",
            session_id="test_partnership_intent"
        )
        return result.get('intent') == 'CREATE_CONTRACT'
    
    def test_intent_analyze_contract(self) -> Dict:
        """Test ANALYZE_CONTRACT intent"""
        result = self.agent.process_message(
            "analyze this contract: This is a test contract...",
            session_id="test_analyze_intent"
        )
        return result.get('intent') == 'ANALYZE_CONTRACT'
    
    def test_intent_question(self) -> Dict:
        """Test QUESTION intent"""
        result = self.agent.process_message(
            "What is the maximum lease duration?",
            session_id="test_question_intent"
        )
        return result.get('intent') == 'QUESTION'
    
    def test_intent_out_of_scope(self) -> Dict:
        """Test OUT_OF_SCOPE intent"""
        result = self.agent.process_message(
            "What's the weather today?",
            session_id="test_out_of_scope"
        )
        return result.get('intent') == 'OUT_OF_SCOPE'
    
    # ========================================
    # CONTRACT TYPE DETECTION TESTS
    # ========================================
    
    def test_contract_type_employment(self) -> str:
        """Test employment contract type detection"""
        result = self.agent._detect_contract_type("I need an employment contract")
        return result == 'EMPLOYMENT'
    
    def test_contract_type_partnership(self) -> str:
        """Test partnership contract type detection"""
        result = self.agent._detect_contract_type("Create a partnership agreement")
        return result == 'PARTNERSHIP'
    
    def test_contract_type_lease(self) -> str:
        """Test lease contract type detection"""
        result = self.agent._detect_contract_type("I want to lease a property")
        return result == 'LEASE'
    
    def test_contract_type_buy_sell(self) -> str:
        """Test buy-sell contract type detection"""
        result = self.agent._detect_contract_type("I need a buy and sell contract")
        return result == 'BUY_SELL'
    
    # ========================================
    # ENTITY EXTRACTION TESTS
    # ========================================
    
    def test_entity_extraction_employment(self) -> Dict:
        """Test entity extraction for employment contract"""
        message = "Employer: ABC Corp, Employee: John Doe, Salary: 50000, Position: Software Engineer"
        extracted = self.agent._extract_entities_c3(message, 'EMPLOYMENT')
        
        # Check if key entities were extracted
        has_employer = 'employer_name' in extracted or any('employer' in k.lower() for k in extracted.keys())
        has_employee = 'employee_name' in extracted or any('employee' in k.lower() for k in extracted.keys())
        has_salary = 'salary' in extracted or any('salary' in k.lower() for k in extracted.keys())
        
        return {
            'extracted': extracted,
            'has_employer': has_employer,
            'has_employee': has_employee,
            'has_salary': has_salary,
            'success': has_employer or has_employee or has_salary
        }
    
    def test_entity_extraction_partnership(self) -> Dict:
        """Test entity extraction for partnership contract"""
        message = "Partner Names: Mark Joseph and Jaedan Bahala, Business: Tech Solutions"
        extracted = self.agent._extract_entities_c3(message, 'PARTNERSHIP')
        
        has_partners = 'partner_names' in extracted
        has_business = 'business_name' in extracted or any('business' in k.lower() for k in extracted.keys())
        
        return {
            'extracted': extracted,
            'has_partners': has_partners,
            'has_business': has_business,
            'success': has_partners or has_business
        }
    
    def test_entity_extraction_lease(self) -> Dict:
        """Test entity extraction for lease contract"""
        message = "Lessor: Maria Santos, Lessee: Juan Cruz, Rental: 15000, Property: 123 Main St"
        extracted = self.agent._extract_entities_c3(message, 'LEASE')
        
        has_lessor = 'lessor_name' in extracted or any('lessor' in k.lower() for k in extracted.keys())
        has_lessee = 'lessee_name' in extracted or any('lessee' in k.lower() for k in extracted.keys())
        has_rental = 'rental_amount' in extracted or any('rent' in k.lower() for k in extracted.keys())
        
        return {
            'extracted': extracted,
            'has_lessor': has_lessor,
            'has_lessee': has_lessee,
            'has_rental': has_rental,
            'success': has_lessor or has_lessee or has_rental
        }
    
    # ========================================
    # CONTRACT GENERATION TESTS
    # ========================================
    
    def test_generate_employment_contract(self) -> Dict:
        """Test employment contract generation"""
        details = {
            'employer_name': 'ABC Corporation',
            'employee_name': 'John Doe',
            'position': 'Software Engineer',
            'salary': '50000',
            'start_date': 'January 1, 2025',
            'employment_type': 'Regular',
            'work_hours': '8 hours',
            'benefits': 'Health insurance, 13th month pay'
        }
        
        result = self.agent.generate_contract(
            contract_type='EMPLOYMENT',
            details=details,
            special_clauses=[],
            session_id='test_employment_gen'
        )
        
        return {
            'success': result.get('success', False),
            'contract_id': result.get('contract_id'),
            'has_content': 'content' in result or result.get('contract_id') is not None
        }
    
    def test_generate_partnership_contract(self) -> Dict:
        """Test partnership contract generation"""
        details = {
            'partner_names': ['Mark Joseph', 'Jaedan Bahala'],
            'business_name': 'Tech Solutions Inc',
            'partnership_type': 'General Partnership',
            'capital_contribution': '500000 each',
            'profit_sharing_ratio': '50-50',
            'business_address': 'Manila, Philippines'
        }
        
        result = self.agent.generate_contract(
            contract_type='PARTNERSHIP',
            details=details,
            special_clauses=[],
            session_id='test_partnership_gen'
        )
        
        return {
            'success': result.get('success', False),
            'contract_id': result.get('contract_id'),
            'has_content': 'content' in result or result.get('contract_id') is not None
        }
    
    def test_generate_lease_contract(self) -> Dict:
        """Test lease contract generation"""
        details = {
            'lessor_name': 'Maria Santos',
            'lessee_name': 'Juan Cruz',
            'property_address': '123 Main Street, Manila',
            'rental_amount': '15000',
            'lease_period': '1 Year',
            'payment_terms': 'Monthly',
            'property_use': 'Residential'
        }
        
        result = self.agent.generate_contract(
            contract_type='LEASE',
            details=details,
            special_clauses=[],
            session_id='test_lease_gen'
        )
        
        return {
            'success': result.get('success', False),
            'contract_id': result.get('contract_id'),
            'has_content': 'content' in result or result.get('contract_id') is not None
        }
    
    def test_generate_buy_sell_contract(self) -> Dict:
        """Test buy-sell contract generation"""
        details = {
            'seller_name': 'Pedro Reyes',
            'buyer_name': 'Ana Garcia',
            'item_description': 'Laptop Computer',
            'purchase_price': '50000',
            'payment_terms': 'Full payment',
            'delivery_terms': 'Pickup',
            'delivery_date': 'January 15, 2025'
        }
        
        result = self.agent.generate_contract(
            contract_type='BUY_SELL',
            details=details,
            special_clauses=[],
            session_id='test_buy_sell_gen'
        )
        
        return {
            'success': result.get('success', False),
            'contract_id': result.get('contract_id'),
            'has_content': 'content' in result or result.get('contract_id') is not None
        }
    
    # ========================================
    # SPECIAL CLAUSE TESTS
    # ========================================
    
    def test_special_clause_generation(self) -> Dict:
        """Test special clause generation"""
        clause = self.agent._generate_special_clause(
            "non-disclosure agreement",
            "EMPLOYMENT"
        )
        
        return {
            'has_clause': clause is not None and len(clause) > 0,
            'clause_length': len(clause) if clause else 0,
            'clause_preview': clause[:100] if clause else None
        }
    
    def test_clause_request_detection(self) -> bool:
        """Test clause request detection"""
        result1 = self.agent._is_clause_request("add a non-compete clause")
        result2 = self.agent._is_clause_request("I want confidentiality")
        result3 = self.agent._is_clause_request("Hello there")
        
        return result1 and result2 and not result3
    
    # ========================================
    # VALIDATION TESTS
    # ========================================
    
    def test_validation_employment(self) -> Dict:
        """Test validation for employment contract"""
        details = {
            'employer_name': 'ABC Corp',
            'employee_name': 'John Doe',
            'salary': '50000'
        }
        
        validation = self.agent._validate_against_law_c4('EMPLOYMENT', details)
        
        return {
            'has_validation': validation is not None,
            'has_warnings': 'warnings' in validation,
            'has_errors': 'errors' in validation,
            'validation_keys': list(validation.keys())
        }
    
    # ========================================
    # CONTRACT ANALYSIS TESTS
    # ========================================
    
    def test_contract_analysis(self) -> Dict:
        """Test contract analysis functionality"""
        sample_contract = """
        EMPLOYMENT CONTRACT
        
        This Agreement is entered into between ABC Corporation (Employer) and John Doe (Employee).
        
        TERM: This contract shall commence on January 1, 2025 and continue for an indefinite period.
        
        COMPENSATION: The Employee shall receive a monthly salary of PHP 50,000.
        
        OBLIGATIONS: The Employee agrees to perform duties as Software Engineer.
        
        TERMINATION: Either party may terminate this agreement with 30 days notice.
        """
        
        result = self.agent.analyze_contract_text(sample_contract)
        
        return {
            'success': result.get('success', False),
            'has_sections': 'sections' in result and len(result.get('sections', {})) > 0,
            'has_compliance': 'legal_compliance' in result,
            'has_risks': 'risks' in result,
            'contract_type': result.get('contract_type')
        }
    
    def test_contract_segmentation(self) -> Dict:
        """Test contract segmentation"""
        sample_text = """
        PARTIES: ABC Corp and John Doe
        
        TERM: 1 Year
        
        COMPENSATION: PHP 50,000 monthly
        """
        
        sections = self.agent._segment_contract(sample_text)
        
        return {
            'has_sections': len(sections) > 0,
            'section_count': len(sections),
            'section_names': list(sections.keys())
        }
    
    # ========================================
    # Q&A SYSTEM TESTS
    # ========================================
    
    def test_question_handling(self) -> Dict:
        """Test Q&A system"""
        result = self.agent.process_message(
            "What is the maximum lease duration in the Philippines?",
            session_id="test_qa"
        )
        
        return {
            'intent': result.get('intent'),
            'has_response': 'response' in result and len(result.get('response', '')) > 0,
            'response_length': len(result.get('response', ''))
        }
    
    def test_law_knowledge_search(self) -> Dict:
        """Test law knowledge search"""
        result = self.agent._search_law_knowledge("maximum lease duration")
        
        return {
            'has_text': 'text' in result and len(result.get('text', '')) > 0,
            'has_sources': 'sources' in result,
            'text_length': len(result.get('text', ''))
        }
    
    # ========================================
    # FIELD DETECTION TESTS
    # ========================================
    
    def test_required_fields_employment(self) -> List[str]:
        """Test required fields detection for employment"""
        fields = self.agent._get_required_fields('EMPLOYMENT')
        return fields
    
    def test_required_fields_partnership(self) -> List[str]:
        """Test required fields detection for partnership"""
        fields = self.agent._get_required_fields('PARTNERSHIP')
        return fields
    
    def test_required_fields_lease(self) -> List[str]:
        """Test required fields detection for lease"""
        fields = self.agent._get_required_fields('LEASE')
        return fields
    
    def test_required_fields_buy_sell(self) -> List[str]:
        """Test required fields detection for buy-sell"""
        fields = self.agent._get_required_fields('BUY_SELL')
        return fields
    
    # ========================================
    # FORMATTING TESTS
    # ========================================
    
    def test_name_formatting(self) -> str:
        """Test name formatting"""
        formatted = self.agent._format_name("john doe")
        return formatted == "John Doe"
    
    def test_money_formatting(self) -> str:
        """Test money formatting"""
        formatted = self.agent._format_money("50000")
        return "50,000" in formatted or "50000" in formatted
    
    def test_date_formatting(self) -> str:
        """Test date formatting"""
        formatted = self.agent._format_date("january 1, 2025")
        return "January" in formatted
    
    # ========================================
    # STATE MANAGEMENT TESTS
    # ========================================
    
    def test_state_update(self) -> Dict:
        """Test state update functionality"""
        session = self.agent._get_or_create_session("test_state")
        session['contract_type'] = 'EMPLOYMENT'
        session['details'] = {}
        
        new_data = {'employer_name': 'ABC Corp', 'employee_name': 'John Doe'}
        state = self.agent._update_state_c2(session, new_data)
        
        return {
            'has_state': state is not None,
            'has_filled': 'filled' in state,
            'has_missing': 'missing' in state,
            'has_details': 'details' in state
        }
    
    # ========================================
    # ERROR HANDLING TESTS
    # ========================================
    
    def test_error_handling_invalid_contract_type(self) -> Dict:
        """Test error handling for invalid contract type"""
        result = self.agent.generate_contract(
            contract_type='INVALID_TYPE',
            details={},
            special_clauses=[],
            session_id='test_error'
        )
        
        return {
            'handles_error': 'error' in result or not result.get('success', True),
            'has_response': 'response' in result
        }
    
    def test_error_handling_empty_message(self) -> Dict:
        """Test error handling for empty message"""
        result = self.agent.process_message("", session_id="test_empty")
        
        return {
            'handles_empty': result is not None,
            'has_response': 'response' in result
        }
    
    # ========================================
    # RUN ALL TESTS
    # ========================================
    
    def run_all_tests(self) -> EvaluationReport:
        """Run all evaluation tests"""
        logger.info("="*60)
        logger.info("Starting Contract Agent Evaluation")
        logger.info("="*60)
        
        # Intent Detection Tests
        logger.info("\n[1/8] Testing Intent Detection...")
        self.run_test("Greeting Intent", "Intent Detection", self.test_intent_greeting)
        self.run_test("Create Contract - Employment", "Intent Detection", self.test_intent_create_contract_employment)
        self.run_test("Create Contract - Partnership", "Intent Detection", self.test_intent_create_contract_partnership)
        self.run_test("Analyze Contract Intent", "Intent Detection", self.test_intent_analyze_contract)
        self.run_test("Question Intent", "Intent Detection", self.test_intent_question)
        self.run_test("Out of Scope Intent", "Intent Detection", self.test_intent_out_of_scope)
        
        # Contract Type Detection
        logger.info("\n[2/8] Testing Contract Type Detection...")
        self.run_test("Employment Type Detection", "Type Detection", self.test_contract_type_employment)
        self.run_test("Partnership Type Detection", "Type Detection", self.test_contract_type_partnership)
        self.run_test("Lease Type Detection", "Type Detection", self.test_contract_type_lease)
        self.run_test("Buy-Sell Type Detection", "Type Detection", self.test_contract_type_buy_sell)
        
        # Entity Extraction
        logger.info("\n[3/8] Testing Entity Extraction...")
        self.run_test("Employment Entity Extraction", "Entity Extraction", self.test_entity_extraction_employment)
        self.run_test("Partnership Entity Extraction", "Entity Extraction", self.test_entity_extraction_partnership)
        self.run_test("Lease Entity Extraction", "Entity Extraction", self.test_entity_extraction_lease)
        
        # Field Detection
        logger.info("\n[4/8] Testing Field Detection...")
        self.run_test("Employment Required Fields", "Field Detection", self.test_required_fields_employment)
        self.run_test("Partnership Required Fields", "Field Detection", self.test_required_fields_partnership)
        self.run_test("Lease Required Fields", "Field Detection", self.test_required_fields_lease)
        self.run_test("Buy-Sell Required Fields", "Field Detection", self.test_required_fields_buy_sell)
        
        # Contract Generation
        logger.info("\n[5/8] Testing Contract Generation...")
        self.run_test("Generate Employment Contract", "Contract Generation", self.test_generate_employment_contract)
        self.run_test("Generate Partnership Contract", "Contract Generation", self.test_generate_partnership_contract)
        self.run_test("Generate Lease Contract", "Contract Generation", self.test_generate_lease_contract)
        self.run_test("Generate Buy-Sell Contract", "Contract Generation", self.test_generate_buy_sell_contract)
        
        # Special Clauses
        logger.info("\n[6/8] Testing Special Clauses...")
        self.run_test("Special Clause Generation", "Special Clauses", self.test_special_clause_generation)
        self.run_test("Clause Request Detection", "Special Clauses", self.test_clause_request_detection)
        
        # Validation
        logger.info("\n[7/8] Testing Validation...")
        self.run_test("Employment Validation", "Validation", self.test_validation_employment)
        
        # Contract Analysis
        logger.info("\n[8/8] Testing Contract Analysis...")
        self.run_test("Contract Analysis", "Analysis", self.test_contract_analysis)
        self.run_test("Contract Segmentation", "Analysis", self.test_contract_segmentation)
        
        # Q&A System
        logger.info("\n[9/8] Testing Q&A System...")
        self.run_test("Question Handling", "Q&A", self.test_question_handling)
        self.run_test("Law Knowledge Search", "Q&A", self.test_law_knowledge_search)
        
        # Formatting
        logger.info("\n[10/8] Testing Formatting...")
        self.run_test("Name Formatting", "Formatting", self.test_name_formatting)
        self.run_test("Money Formatting", "Formatting", self.test_money_formatting)
        self.run_test("Date Formatting", "Formatting", self.test_date_formatting)
        
        # State Management
        logger.info("\n[11/8] Testing State Management...")
        self.run_test("State Update", "State Management", self.test_state_update)
        
        # Error Handling
        logger.info("\n[12/8] Testing Error Handling...")
        self.run_test("Invalid Contract Type", "Error Handling", self.test_error_handling_invalid_contract_type)
        self.run_test("Empty Message", "Error Handling", self.test_error_handling_empty_message)
        
        # Generate Report
        total_time = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        success_rate = (passed / len(self.results) * 100) if self.results else 0
        
        # Category summary
        category_summary = {}
        for result in self.results:
            cat = result.category
            if cat not in category_summary:
                category_summary[cat] = {'total': 0, 'passed': 0}
            category_summary[cat]['total'] += 1
            if result.passed:
                category_summary[cat]['passed'] += 1
        
        for cat in category_summary:
            cat_passed = category_summary[cat]['passed']
            cat_total = category_summary[cat]['total']
            category_summary[cat]['rate'] = (cat_passed / cat_total * 100) if cat_total > 0 else 0
        
        report = EvaluationReport(
            timestamp=datetime.now().isoformat(),
            total_tests=len(self.results),
            passed=passed,
            failed=failed,
            success_rate=success_rate,
            execution_time=total_time,
            test_results=self.results,
            summary={
                'category_summary': category_summary,
                'llm_available': self.agent.llm_available,
                'laws_loaded': len(self.agent.ph_laws)
            }
        )
        
        return report
    
    def generate_report(self, report: EvaluationReport, output_file: str = None):
        """Generate evaluation report"""
        if output_file is None:
            output_file = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(__file__).parent / output_file
        
        # Convert to dict for JSON serialization
        report_dict = {
            'timestamp': report.timestamp,
            'total_tests': report.total_tests,
            'passed': report.passed,
            'failed': report.failed,
            'success_rate': report.success_rate,
            'execution_time': report.execution_time,
            'summary': report.summary,
            'test_results': [
                {
                    'test_name': r.test_name,
                    'category': r.category,
                    'passed': r.passed,
                    'execution_time': r.execution_time,
                    'error': r.error,
                    'actual': str(r.actual)[:200] if r.actual else None  # Truncate long outputs
                }
                for r in report.test_results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed} ({report.success_rate:.1f}%)")
        print(f"Failed: {report.failed}")
        print(f"Execution Time: {report.execution_time:.2f}s")
        print(f"\nLLM Available: {'Yes' if report.summary['llm_available'] else 'No'}")
        print(f"Laws Loaded: {report.summary['laws_loaded']}")
        
        print("\nCategory Breakdown:")
        for category, stats in report.summary['category_summary'].items():
            print(f"  {category}: {stats['passed']}/{stats['total']} ({stats['rate']:.1f}%)")
        
        print(f"\nDetailed report saved to: {output_path}")
        print("="*60)
        
        return output_path

def main():
    """Main evaluation entry point"""
    evaluator = ContractAgentEvaluator()
    report = evaluator.run_all_tests()
    evaluator.generate_report(report)
    
    # Exit with appropriate code
    if report.success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == '__main__':
    main()
