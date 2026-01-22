# Contract Agent Evaluation Script

## Overview

The `evaluate.py` script provides comprehensive testing and evaluation of the KontrataPH Contract Agent system. It tests all major functionalities including intent detection, entity extraction, contract generation, analysis, and more.

## Features

### Test Categories

1. **Intent Detection** - Tests detection of different user intents:
   - Greeting
   - Create Contract
   - Analyze Contract
   - Question
   - Out of Scope

2. **Contract Type Detection** - Tests detection of:
   - Employment
   - Partnership
   - Lease
   - Buy & Sell

3. **Entity Extraction** - Tests extraction of entities from user messages for all contract types

4. **Field Detection** - Tests dynamic detection of required fields for each contract type

5. **Contract Generation** - Tests generation of contracts for all types

6. **Special Clauses** - Tests special clause generation and detection

7. **Validation** - Tests Philippine law validation

8. **Contract Analysis** - Tests contract analysis and segmentation

9. **Q&A System** - Tests question answering and law knowledge search

10. **Formatting** - Tests data formatting (names, money, dates)

11. **State Management** - Tests dialogue state tracking

12. **Error Handling** - Tests error handling for edge cases

## Usage

### Basic Usage

```bash
cd backend
python evaluate.py
```

### Output

The script will:
1. Run all tests and display progress
2. Generate a JSON report with detailed results
3. Print a summary to the console
4. Exit with code 0 (success) if ≥80% tests pass, otherwise code 1

### Report Format

The evaluation report includes:
- Timestamp
- Total tests, passed, failed
- Success rate
- Execution time
- Category breakdown
- Detailed test results with execution times
- System status (LLM availability, laws loaded)

### Example Output

```
============================================================
Starting Contract Agent Evaluation
============================================================

[1/8] Testing Intent Detection...
✓ [Intent Detection] Greeting Intent (0.05s)
✓ [Intent Detection] Create Contract - Employment (0.12s)
...

============================================================
EVALUATION SUMMARY
============================================================
Total Tests: 35
Passed: 32 (91.4%)
Failed: 3
Execution Time: 45.23s

LLM Available: Yes
Laws Loaded: 4

Category Breakdown:
  Intent Detection: 6/6 (100.0%)
  Type Detection: 4/4 (100.0%)
  Entity Extraction: 3/3 (100.0%)
  ...

Detailed report saved to: evaluation_report_20250115_143022.json
============================================================
```

## Test Structure

Each test:
- Has a descriptive name and category
- Records execution time
- Captures errors if any
- Returns pass/fail status

## Customization

### Adding New Tests

1. Create a test method in `ContractAgentEvaluator`:
```python
def test_my_new_feature(self) -> Dict:
    """Test description"""
    result = self.agent.some_method()
    return {'success': result is not None}
```

2. Add it to `run_all_tests()`:
```python
self.run_test("My New Feature", "Category", self.test_my_new_feature)
```

### Modifying Test Data

Edit the test methods to use different test cases or expected values.

### Changing Success Threshold

Modify the threshold in `main()`:
```python
if report.success_rate >= 80:  # Change 80 to your threshold
```

## Requirements

- Python 3.7+
- All dependencies from `requirements.txt`
- Contract agent and related modules
- (Optional) Ollama running for LLM-powered tests

## Notes

- Tests that require LLM will still run but may have different results if Ollama is not available
- Some tests may take longer if LLM is enabled
- The script creates separate sessions for each test to avoid interference
- Failed tests include error messages in the report

## Integration

This script can be integrated into:
- CI/CD pipelines
- Pre-deployment checks
- Development workflow
- Quality assurance processes

Run before major releases to ensure system quality!
