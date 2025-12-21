from flask import Flask, render_template, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# Simulate Entity Extraction (3.1 Input Module)
def extract_entities(filename):
    return {
        'parties': ['ABC Corporation', 'John Dela Cruz'],
        'dates': ['January 1, 2025', 'December 31, 2025'],
        'amounts': ['₱50,000.00', '₱5,000.00'],
        'obligations': [
            'Deliver software within 90 days',
            'Monthly maintenance support',
            'Payment within 30 days'
        ]
    }

# Simulate Contract Analysis (3.4 Contract Analysis Module)
def analyze_contract():
    return {
        'riskLevel': 'medium',
        'missingClauses': [
            'Termination clause not clearly defined',
            'No dispute resolution mechanism specified',
            'Intellectual property rights unclear'
        ],
        'ambiguousTerms': [
            'Payment terms lack specific due dates',
            'Scope of work needs more detail'
        ],
        'complianceIssues': [
            'Duration exceeds standard labor contract limits (Labor Code Article 280)',
            'Missing mandatory provisions under Civil Code Article 1305'
        ],
        'recommendations': [
            'Add specific termination conditions with notice periods',
            'Include arbitration clause for dispute resolution',
            'Clarify IP ownership and license terms',
            'Specify exact payment schedule with penalties for late payment'
        ],
        'legalReasoning': 'Under Philippine law, employment contracts must comply with Labor Code provisions. The current contract lacks clear termination clauses which may lead to disputes. Articles 282-284 of the Labor Code require specific grounds for termination.'
    }

# Simulate Contract Generation (3.3 Contract Generation Module)
def generate_contract(user_input):
    return {
        'title': 'Service Agreement Contract',
        'content': '''SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on January 15, 2025, by and between:

PARTY A: ABC Corporation
Address: Makati City, Metro Manila

PARTY B: John Dela Cruz  
Address: Quezon City, Metro Manila

WHEREAS, Party A requires professional services;
WHEREAS, Party B agrees to provide said services;

NOW, THEREFORE, the parties agree as follows:

1. SCOPE OF SERVICES
   Party B shall provide software development services as specified.

2. COMPENSATION
   Party A shall pay Party B the sum of ₱50,000.00 monthly.
   
3. TERM
   This Agreement shall commence on February 1, 2025 and continue for 12 months.

4. TERMINATION
   Either party may terminate with 30 days written notice.

5. DISPUTE RESOLUTION
   Disputes shall be resolved through arbitration under Philippine law.

6. GOVERNING LAW
   This Agreement is governed by Philippine law.

COMPLIANCE STATUS: ✓ Civil Code compliant
                   ✓ Labor Code compliant  
                   ✓ Required clauses present''',
        'complianceChecks': {
            'requiredClauses': True,
            'legalCompliance': True,
            'durationValid': True,
            'amountsValid': True
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filename = file.filename
    
    # Simulate processing delay
    time.sleep(1.5)
    
    # Extract entities
    entities = extract_entities(filename)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'entities': entities
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # Simulate processing delay
    time.sleep(2)
    
    # Perform analysis
    analysis = analyze_contract()
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('input', '')
    
    # Simulate processing delay
    time.sleep(2)
    
    # Generate contract
    contract = generate_contract(user_input)
    
    return jsonify({
        'success': True,
        'contract': contract
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    metrics = {
        'precision': 0.92,
        'recall': 0.88,
        'errorRate': 0.05,
        'processingTime': 2.3
    }
    
    return jsonify(metrics)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    ratings = data.get('ratings', {})
    
    avg_score = (
        ratings.get('easeOfUse', 0) +
        ratings.get('clarityOfSuggestions', 0) +
        ratings.get('outputQuality', 0) +
        ratings.get('overallSatisfaction', 0)
    ) / 4
    
    return jsonify({
        'success': True,
        'averageScore': avg_score,
        'ratings': ratings
    })

if __name__ == '__main__':
    app.run(debug=True)