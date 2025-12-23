from flask import Flask, render_template, request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)

# ============================================
# CRITICAL FIX 1: Configuration & Security
# ============================================
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'doc', 'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Validate file extension for security"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ============================================
# Simulate Entity Extraction (3.1 Input Module)
# ============================================
def extract_entities(filename):
    """Extract entities from uploaded contract"""
    return {
        'parties': ['ABC Corporation', 'John Dela Cruz'],
        'dates': ['January 1, 2025', 'December 31, 2025'],
        'amounts': ['₱50,000.00', '₱5,000.00'],  # Fixed encoding
        'obligations': [
            'Deliver software within 90 days',
            'Monthly maintenance support',
            'Payment within 30 days'
        ]
    }

# ============================================
# Simulate Contract Analysis (3.4 Contract Analysis Module)
# ============================================
def analyze_contract():
    """Analyze contract for risks and compliance"""
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

# ============================================
# Simulate Contract Generation (3.3 Contract Generation Module)
# ============================================
def generate_contract(user_input):
    """Generate contract based on user input"""
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

# ============================================
# ROUTES WITH ERROR HANDLING
# ============================================

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload with validation and error handling
    CRITICAL FIX: Added file validation and error handling
    """
    try:
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        # Validate file selection
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Simulate processing delay
        time.sleep(1.5)
        
        # Extract entities
        entities = extract_entities(filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'entities': entities
        })
        
    except Exception as e:
        # Log error in production, you'd use proper logging
        print(f"Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your file. Please try again.'
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze contract with error handling
    CRITICAL FIX: Added try-catch for robust error handling
    """
    try:
        # Simulate processing delay
        time.sleep(2)
        
        # Perform analysis
        analysis = analyze_contract()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during contract analysis. Please try again.'
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Generate contract with input validation
    CRITICAL FIX: Added input validation and sanitization
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'input' not in data:
            return jsonify({
                'success': False,
                'error': 'No input provided'
            }), 400
        
        user_input = data.get('input', '').strip()
        
        # Validate input length
        if len(user_input) < 10:
            return jsonify({
                'success': False,
                'error': 'Please provide more details about the contract (at least 10 characters)'
            }), 400
        
        if len(user_input) > 5000:
            return jsonify({
                'success': False,
                'error': 'Input too long. Please limit to 5000 characters.'
            }), 400
        
        # Simulate processing delay
        time.sleep(2)
        
        # Generate contract
        contract = generate_contract(user_input)
        
        return jsonify({
            'success': True,
            'contract': contract
        })
        
    except Exception as e:
        print(f"Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating the contract. Please try again.'
        }), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        metrics = {
            'precision': 0.92,
            'recall': 0.88,
            'errorRate': 0.05,
            'processingTime': 2.3
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        print(f"Metrics error: {str(e)}")
        return jsonify({
            'error': 'Unable to fetch metrics'
        }), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback with validation
    CRITICAL FIX: Added input validation
    """
    try:
        data = request.get_json()
        
        if not data or 'ratings' not in data:
            return jsonify({
                'success': False,
                'error': 'No ratings provided'
            }), 400
        
        ratings = data.get('ratings', {})
        
        # Validate ratings (1-5 range)
        valid_ratings = {}
        for key, value in ratings.items():
            if isinstance(value, (int, float)) and 0 <= value <= 5:
                valid_ratings[key] = value
            else:
                valid_ratings[key] = 0
        
        # Calculate average
        avg_score = sum(valid_ratings.values()) / len(valid_ratings) if valid_ratings else 0
        
        return jsonify({
            'success': True,
            'averageScore': avg_score,
            'ratings': valid_ratings
        })
        
    except Exception as e:
        print(f"Feedback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to submit feedback. Please try again.'
        }), 500

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again later.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)