"""
KontrataPH System Evaluation Script
====================================
Evaluates the contract agent system across multiple dimensions:
1. Intent Detection (Precision, Recall, F1)
2. Entity Extraction (Accuracy, Field Coverage)
3. Contract Generation Quality
4. Analysis Accuracy
5. Response Time Performance
"""

import json
import time
from typing import Dict, List, Tuple
from pathlib import Path
import sys
from pathlib import Path

# Add backend to path (assuming this script is in evaluation/ folder)
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from agents.contract_agent import ProperLLMAgent
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, classification_report
import numpy as np


class SystemEvaluator:
    """Comprehensive evaluation of the contract system"""
    
    def __init__(self):
        self.agent = ProperLLMAgent()
        self.results = {
            'intent_detection': {},
            'entity_extraction': {},
            'contract_generation': {},
            'analysis': {},
            'performance': {}
        }
    
    # ========================================
    # 1. INTENT DETECTION EVALUATION
    # ========================================
    
    def evaluate_intent_detection(self):
        """
        Test intent detection with ground truth labels
        Metrics: Precision, Recall, F1-Score, Accuracy
        """
        print("\n" + "="*60)
        print("EVALUATING INTENT DETECTION")
        print("="*60)
        
        # Test cases with ground truth
        test_cases = [
            # Greetings
            ("hello", "GREETING"),
            ("hi there", "GREETING"),
            ("good morning", "GREETING"),
            
            # Contract Creation
            ("create employment contract", "CREATE_CONTRACT"),
            ("I need a partnership agreement", "CREATE_CONTRACT"),
            ("generate lease contract", "CREATE_CONTRACT"),
            ("make a buy and sell contract", "CREATE_CONTRACT"),
            ("employment contract please", "CREATE_CONTRACT"),
            
            # Analysis
            ("analyze this contract", "ANALYZE_CONTRACT"),
            ("review this contract", "ANALYZE_CONTRACT"),
            ("check this contract", "ANALYZE_CONTRACT"),
            
            # Questions
            ("what is the maximum lease duration", "QUESTION"),
            ("how much is minimum wage", "QUESTION"),
            ("what are the grounds for termination", "QUESTION"),
            ("can you tell me about partnership requirements", "QUESTION"),
            
            # Out of Scope
            ("what's the weather today", "OUT_OF_SCOPE"),
            ("how do I bake a cake", "OUT_OF_SCOPE"),
            ("tell me a joke", "OUT_OF_SCOPE"),
            
            # Providing Info (during flow)
            ("employer name is ABC Corp", "PROVIDING_INFO"),
            ("the salary is 50000", "PROVIDING_INFO"),
        ]
        
        y_true = []
        y_pred = []
        
        for message, expected_intent in test_cases:
            result = self.agent._detect_intent_c1(message)
            predicted_intent = result['intent']
            
            y_true.append(expected_intent)
            y_pred.append(predicted_intent)
            
            match = "✓" if predicted_intent == expected_intent else "✗"
            print(f"{match} '{message[:40]}...' -> Expected: {expected_intent}, Got: {predicted_intent}")
        
        # Calculate metrics
        intent_labels = list(set(y_true + y_pred))
        
        precision = precision_score(y_true, y_pred, average='weighted', labels=intent_labels, zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', labels=intent_labels, zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', labels=intent_labels, zero_division=0)
        accuracy = accuracy_score(y_true, y_pred)
        
        self.results['intent_detection'] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'accuracy': accuracy,
            'total_cases': len(test_cases),
            'correct': sum(1 for t, p in zip(y_true, y_pred) if t == p)
        }
        
        print(f"\n📊 INTENT DETECTION METRICS:")
        print(f"   Accuracy:  {accuracy:.3f} ({self.results['intent_detection']['correct']}/{len(test_cases)})")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall:    {recall:.3f}")
        print(f"   F1-Score:  {f1:.3f}")
        
        # Detailed classification report
        print(f"\n📋 Classification Report:")
        print(classification_report(y_true, y_pred, labels=intent_labels, zero_division=0))
    
    # ========================================
    # 2. ENTITY EXTRACTION EVALUATION
    # ========================================
    
    def evaluate_entity_extraction(self):
        """
        Test entity extraction accuracy
        Metrics: Field-level accuracy, Coverage, Extraction rate
        """
        print("\n" + "="*60)
        print("EVALUATING ENTITY EXTRACTION")
        print("="*60)
        
        test_cases = [
            {
                'message': "Employer: ABC Corporation, Employee: John Doe, Position: Software Engineer, Salary: 50000",
                'contract_type': 'EMPLOYMENT',
                'expected': {
                    'employer_name': 'ABC Corporation',
                    'employee_name': 'John Doe',
                    'position': 'Software Engineer',
                    'salary': '50000'
                }
            },
            {
                'message': "Partner Names: Mark Joseph and Jaedan Bahala, Business: Tech Startup, Capital: 500000",
                'contract_type': 'PARTNERSHIP',
                'expected': {
                    'partner_names': ['Mark Joseph', 'Jaedan Bahala'],
                    'business_name': 'Tech Startup',
                    'capital_contribution': '500000'
                }
            },
            {
                'message': "Lessor: Jane Smith, Lessee: Bob Johnson, Property: 123 Main St, Rent: 15000, Period: 1 year",
                'contract_type': 'LEASE',
                'expected': {
                    'lessor_name': 'Jane Smith',
                    'lessee_name': 'Bob Johnson',
                    'property_address': '123 Main St',
                    'rental_amount': '15000',
                    'lease_period': '1 year'
                }
            }
        ]
        
        total_fields = 0
        correct_extractions = 0
        partial_matches = 0
        
        for test in test_cases:
            extracted = self.agent._extract_entities_c3(test['message'], test['contract_type'])
            expected = test['expected']
            
            print(f"\n📝 Test: {test['contract_type']}")
            print(f"   Message: {test['message'][:60]}...")
            
            for field, expected_value in expected.items():
                total_fields += 1
                extracted_value = extracted.get(field)
                
                if isinstance(expected_value, list):
                    # For lists (like partner_names)
                    if extracted_value == expected_value:
                        correct_extractions += 1
                        print(f"   ✓ {field}: {extracted_value}")
                    elif extracted_value and set(extracted_value) & set(expected_value):
                        partial_matches += 1
                        print(f"   ⚠ {field}: {extracted_value} (partial match)")
                    else:
                        print(f"   ✗ {field}: Expected {expected_value}, Got {extracted_value}")
                else:
                    # For strings
                    if extracted_value and str(expected_value).lower() in str(extracted_value).lower():
                        correct_extractions += 1
                        print(f"   ✓ {field}: {extracted_value}")
                    elif extracted_value:
                        partial_matches += 1
                        print(f"   ⚠ {field}: {extracted_value} (partial)")
                    else:
                        print(f"   ✗ {field}: Expected {expected_value}, Got {extracted_value}")
        
        extraction_accuracy = correct_extractions / total_fields if total_fields > 0 else 0
        coverage = (correct_extractions + partial_matches) / total_fields if total_fields > 0 else 0
        
        self.results['entity_extraction'] = {
            'accuracy': extraction_accuracy,
            'coverage': coverage,
            'total_fields': total_fields,
            'correct': correct_extractions,
            'partial': partial_matches,
            'missed': total_fields - correct_extractions - partial_matches
        }
        
        print(f"\n📊 ENTITY EXTRACTION METRICS:")
        print(f"   Accuracy:  {extraction_accuracy:.3f} ({correct_extractions}/{total_fields})")
        print(f"   Coverage:  {coverage:.3f}")
        print(f"   Partial:   {partial_matches}")
        print(f"   Missed:    {total_fields - correct_extractions - partial_matches}")
    
    # ========================================
    # 3. CONTRACT GENERATION QUALITY
    # ========================================
    
    def evaluate_contract_generation(self):
        """
        Test contract generation completeness and quality
        Metrics: Completeness, Field inclusion, Legal compliance
        """
        print("\n" + "="*60)
        print("EVALUATING CONTRACT GENERATION")
        print("="*60)
        
        test_cases = [
            {
                'type': 'EMPLOYMENT',
                'details': {
                    'employer_name': 'Tech Corp',
                    'employee_name': 'John Doe',
                    'position': 'Developer',
                    'salary': '50000',
                    'start_date': 'January 1, 2026',
                    'employment_type': 'Regular',
                    'work_hours': '40 hours per week',
                    'benefits': 'SSS, PhilHealth, Pag-IBIG'
                }
            },
            {
                'type': 'LEASE',
                'details': {
                    'lessor_name': 'Jane Smith',
                    'lessee_name': 'Bob Johnson',
                    'property_address': '123 Main Street',
                    'property_description': '2-bedroom apartment',
                    'rental_amount': '15000',
                    'lease_period': '1 Year',
                    'payment_terms': 'Monthly in advance',
                    'property_use': 'Residential'
                }
            }
        ]
        
        generation_scores = []
        
        for test in test_cases:
            print(f"\n📄 Testing {test['type']} Contract Generation...")
            
            # Generate contract
            result = self.agent.generate_contract(
                contract_type=test['type'],
                details=test['details'],
                special_clauses=[],
                session_id='eval_test'
            )
            
            if result.get('success'):
                contract_content = self.agent.contracts[result['contract_id']]['content']
                
                # Check completeness
                checks = {
                    'has_parties': False,
                    'has_terms': False,
                    'has_obligations': False,
                    'has_termination': False,
                    'has_signature': False,
                    'all_fields_included': True
                }
                
                content_lower = contract_content.lower()
                
                # Check for key sections
                checks['has_parties'] = any(party.lower() in content_lower for party in test['details'].values() if isinstance(party, str))
                checks['has_terms'] = 'article' in content_lower or 'section' in content_lower
                checks['has_obligations'] = 'obligation' in content_lower or 'responsibilit' in content_lower
                checks['has_termination'] = 'termination' in content_lower
                checks['has_signature'] = 'witness' in content_lower or 'signature' in content_lower
                
                # Check if all input fields appear in contract
                for field, value in test['details'].items():
                    if value and str(value).lower() not in content_lower:
                        checks['all_fields_included'] = False
                        print(f"   ⚠ Missing field: {field} = {value}")
                
                score = sum(checks.values()) / len(checks)
                generation_scores.append(score)
                
                print(f"   Completeness: {score:.2%}")
                for check_name, passed in checks.items():
                    symbol = "✓" if passed else "✗"
                    print(f"   {symbol} {check_name.replace('_', ' ').title()}")
            else:
                print(f"   ✗ Generation failed: {result.get('error', 'Unknown error')}")
                generation_scores.append(0)
        
        avg_score = np.mean(generation_scores) if generation_scores else 0
        
        self.results['contract_generation'] = {
            'average_completeness': avg_score,
            'total_contracts_tested': len(test_cases),
            'successful_generations': sum(1 for s in generation_scores if s > 0),
            'scores': generation_scores
        }
        
        print(f"\n📊 CONTRACT GENERATION METRICS:")
        print(f"   Average Completeness: {avg_score:.3f}")
        print(f"   Success Rate: {sum(1 for s in generation_scores if s > 0)}/{len(test_cases)}")
    
    # ========================================
    # 4. ANALYSIS ACCURACY
    # ========================================
    
    def evaluate_analysis(self):
        """
        Test contract analysis capabilities
        Metrics: Section detection, Compliance detection, Risk identification
        """
        print("\n" + "="*60)
        print("EVALUATING CONTRACT ANALYSIS")
        print("="*60)
        
        # Sample contract text for testing
        sample_contract = """
        EMPLOYMENT AGREEMENT
        
        This agreement is between ABC Corporation (Employer) and John Doe (Employee).
        
        ARTICLE 1 - POSITION
        Employee shall serve as Software Developer.
        
        ARTICLE 2 - COMPENSATION
        Monthly salary of PHP 30,000.
        
        ARTICLE 3 - TERM
        Employment commences January 1, 2026 for indefinite period.
        
        ARTICLE 4 - TERMINATION
        Either party may terminate with 30 days notice.
        
        Signed this 1st day of January 2026.
        """
        
        print("\n🔍 Analyzing sample contract...")
        analysis = self.agent.analyze_contract_text(sample_contract, 'EMPLOYMENT')
        
        if analysis.get('success'):
            metrics = {
                'sections_detected': len(analysis.get('sections', {})),
                'has_compliance_check': 'legal_compliance' in analysis,
                'has_risk_analysis': 'risks' in analysis,
                'has_summary': 'summary' in analysis
            }
            
            print(f"   ✓ Analysis completed")
            print(f"   Sections detected: {metrics['sections_detected']}")
            print(f"   Compliance check: {'✓' if metrics['has_compliance_check'] else '✗'}")
            print(f"   Risk analysis: {'✓' if metrics['has_risk_analysis'] else '✗'}")
            print(f"   Summary generated: {'✓' if metrics['has_summary'] else '✗'}")
            
            # Check specific sections
            sections = analysis.get('sections', {})
            expected_sections = ['parties', 'compensation', 'term', 'termination']
            found_sections = sum(1 for sect in expected_sections if any(sect in s.lower() for s in sections.keys()))
            
            section_detection_rate = found_sections / len(expected_sections) if expected_sections else 0
            
            self.results['analysis'] = {
                'section_detection_rate': section_detection_rate,
                'sections_found': found_sections,
                'sections_expected': len(expected_sections),
                'has_compliance': metrics['has_compliance_check'],
                'has_risks': metrics['has_risk_analysis'],
                'has_summary': metrics['has_summary']
            }
            
            print(f"\n📊 ANALYSIS METRICS:")
            print(f"   Section Detection: {section_detection_rate:.3f} ({found_sections}/{len(expected_sections)})")
        else:
            print(f"   ✗ Analysis failed: {analysis.get('error')}")
            self.results['analysis'] = {'error': analysis.get('error')}
    
    # ========================================
    # 5. PERFORMANCE EVALUATION
    # ========================================
    
    def evaluate_performance(self):
        """
        Test system response times
        Metrics: Average response time, Intent detection speed, Generation speed
        """
        print("\n" + "="*60)
        print("EVALUATING PERFORMANCE")
        print("="*60)
        
        # Test intent detection speed
        messages = [
            "hello",
            "create employment contract",
            "what is the maximum lease duration",
            "analyze this contract"
        ]
        
        intent_times = []
        for msg in messages:
            start = time.time()
            self.agent._detect_intent_c1(msg)
            duration = time.time() - start
            intent_times.append(duration)
        
        # Test entity extraction speed
        extraction_msg = "Employer: ABC Corp, Employee: John Doe, Position: Developer, Salary: 50000"
        start = time.time()
        self.agent._extract_entities_c3(extraction_msg, 'EMPLOYMENT')
        extraction_time = time.time() - start
        
        # Test generation speed
        start = time.time()
        self.agent.generate_contract(
            contract_type='EMPLOYMENT',
            details={
                'employer_name': 'Test Corp',
                'employee_name': 'Test User',
                'position': 'Tester',
                'salary': '40000',
                'start_date': 'January 1, 2026',
                'employment_type': 'Regular',
                'work_hours': '40 hours',
                'benefits': 'Standard'
            },
            special_clauses=[],
            session_id='perf_test'
        )
        generation_time = time.time() - start
        
        avg_intent_time = np.mean(intent_times)
        
        self.results['performance'] = {
            'avg_intent_detection_ms': avg_intent_time * 1000,
            'entity_extraction_ms': extraction_time * 1000,
            'contract_generation_ms': generation_time * 1000,
            'total_avg_response_ms': (avg_intent_time + extraction_time + generation_time) * 1000
        }
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"   Intent Detection:     {avg_intent_time*1000:.2f} ms")
        print(f"   Entity Extraction:    {extraction_time*1000:.2f} ms")
        print(f"   Contract Generation:  {generation_time*1000:.2f} ms")
        print(f"   Total Avg Response:   {self.results['performance']['total_avg_response_ms']:.2f} ms")
    
    # ========================================
    # COMPREHENSIVE REPORT
    # ========================================
    
    def generate_report(self):
        """Generate comprehensive evaluation report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE EVALUATION REPORT")
        print("="*60)
        
        print("\n📊 SUMMARY OF ALL METRICS:\n")
        
        # Intent Detection
        if 'intent_detection' in self.results:
            id_metrics = self.results['intent_detection']
            print(f"1. INTENT DETECTION")
            print(f"   Accuracy:  {id_metrics.get('accuracy', 0):.3f}")
            print(f"   Precision: {id_metrics.get('precision', 0):.3f}")
            print(f"   Recall:    {id_metrics.get('recall', 0):.3f}")
            print(f"   F1-Score:  {id_metrics.get('f1_score', 0):.3f}")
            print()
        
        # Entity Extraction
        if 'entity_extraction' in self.results:
            ee_metrics = self.results['entity_extraction']
            print(f"2. ENTITY EXTRACTION")
            print(f"   Accuracy:  {ee_metrics.get('accuracy', 0):.3f}")
            print(f"   Coverage:  {ee_metrics.get('coverage', 0):.3f}")
            print()
        
        # Contract Generation
        if 'contract_generation' in self.results:
            cg_metrics = self.results['contract_generation']
            print(f"3. CONTRACT GENERATION")
            print(f"   Completeness: {cg_metrics.get('average_completeness', 0):.3f}")
            print(f"   Success Rate: {cg_metrics.get('successful_generations', 0)}/{cg_metrics.get('total_contracts_tested', 0)}")
            print()
        
        # Analysis
        if 'analysis' in self.results:
            an_metrics = self.results['analysis']
            if 'error' not in an_metrics:
                print(f"4. CONTRACT ANALYSIS")
                print(f"   Section Detection: {an_metrics.get('section_detection_rate', 0):.3f}")
                print(f"   Has Compliance: {an_metrics.get('has_compliance', False)}")
                print(f"   Has Risks: {an_metrics.get('has_risks', False)}")
                print()
        
        # Performance
        if 'performance' in self.results:
            perf_metrics = self.results['performance']
            print(f"5. PERFORMANCE")
            print(f"   Avg Response Time: {perf_metrics.get('total_avg_response_ms', 0):.2f} ms")
            print()
        
        # Save to JSON
        output_file = 'evaluation_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Full results saved to: {output_file}")
        print("="*60)
    
    def run_all_evaluations(self):
        """Run all evaluation tests"""
        print("\n🚀 Starting Comprehensive System Evaluation...\n")
        
        self.evaluate_intent_detection()
        self.evaluate_entity_extraction()
        self.evaluate_contract_generation()
        self.evaluate_analysis()
        self.evaluate_performance()
        
        self.generate_report()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    evaluator = SystemEvaluator()
    evaluator.run_all_evaluations()