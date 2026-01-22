#backend/app.py
"""
KontrataPH Flask Application - OLLAMA LLM VERSION
FREE LLM-powered contract generation and analysis
"""
import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from loguru import logger
import sys
from pathlib import Path

from config import (
    FLASK_DEBUG, FLASK_HOST, FLASK_PORT, 
    LOG_FILE, LOG_LEVEL,
    OUT_OF_SCOPE_MESSAGE
)

from agents.contract_agent import ProperLLMAgent as LLMContractAgent
from utils.validators import validate_file_upload

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="10 MB", level=LOG_LEVEL)

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize LLM Contract Agent (Ollama)
contract_agent = LLMContractAgent()

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    llm_status = "✓ Connected" if contract_agent.llm_available else "✗ Not running"
    
    return jsonify({
        "service": "KontrataPH API - LLM VERSION",
        "version": "1.0.0 (FREE LLM)",
        "description": "Intelligent Contract Analysis & Generation Platform",
        "mode": "LLM-Powered (Ollama)",
        "llm_status": llm_status,
        "model": contract_agent.model if contract_agent.llm_available else "N/A",
        "status": "running"
    })

@app.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "KontrataPH API",
        "version": "1.0.0",
        "mode": "LLM (Ollama)",
        "llm_available": contract_agent.llm_available,
        "model": contract_agent.model if contract_agent.llm_available else None,
        "cors": "enabled"
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@cross_origin()
def chat():
    """Main chat endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        context = data.get('context', {})
        
        logger.info(f"Chat request - Session: {session_id}, Message: {user_message[:100]}")
        
        # Process message through LLM agent
        response = contract_agent.process_message(
            message=user_message,
            session_id=session_id,
            context=context
        )
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred processing your request",
            "details": str(e)
        }), 500

@app.route('/api/generate-contract', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_contract():
    """Generate contract endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        if not data or 'contract_type' not in data:
            return jsonify({
                "error": "Missing 'contract_type' in request body"
            }), 400
        
        contract_type = data['contract_type']
        details = data.get('details', {})
        special_clauses = data.get('special_clauses', [])
        session_id = data.get('session_id', 'default')
        
        logger.info(f"Contract generation - Type: {contract_type}")
        
        # Generate contract through LLM agent
        response = contract_agent.generate_contract(
            contract_type=contract_type,
            details=details,
            special_clauses=special_clauses,
            session_id=session_id
        )
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in generate-contract endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred generating the contract",
            "details": str(e)
        }), 500

@app.route('/api/analyze-contract', methods=['POST', 'OPTIONS'])
@cross_origin()
def analyze_contract():
    """Analyze contract endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            
            # Validate file
            is_valid, message = validate_file_upload(file)
            if not is_valid:
                return jsonify({"error": message}), 400
            
            # Process file through agent
            response = contract_agent.analyze_contract_file(file)
            
        # Handle text input
        elif request.is_json:
            data = request.get_json()
            
            if 'text' not in data:
                return jsonify({
                    "error": "Missing 'text' or 'file' in request"
                }), 400
            
            contract_text = data['text']
            contract_type = data.get('contract_type')
            
            # Process text through agent
            response = contract_agent.analyze_contract_text(
                contract_text=contract_text,
                contract_type=contract_type
            )
        else:
            return jsonify({
                "error": "Invalid request format. Use multipart/form-data or JSON"
            }), 400
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze-contract endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred analyzing the contract",
            "details": str(e)
        }), 500

@app.route('/api/download-contract/<contract_id>', methods=['GET'])
@cross_origin()
def download_contract(contract_id):
    """Download generated contract as DOCX"""
    try:
        file_path = contract_agent.get_contract_file(contract_id)
        
        if not file_path or not Path(file_path).exists():
            return jsonify({
                "error": "Contract not found"
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"contract_{contract_id}.docx"
        )
        
    except Exception as e:
        logger.error(f"Error in download-contract endpoint: {str(e)}")
        return jsonify({
            "error": "An error occurred downloading the contract",
            "details": str(e)
        }), 500

@app.route('/api/contract-types', methods=['GET'])
@cross_origin()
def get_contract_types():
    """Get available contract types"""
    from config import CONTRACT_TYPES, REQUIRED_FIELDS
    
    return jsonify({
        "contract_types": CONTRACT_TYPES,
        "required_fields": REQUIRED_FIELDS
    })

@app.route('/api/get-contract-content/<contract_id>', methods=['GET'])
@cross_origin()
def get_contract_content(contract_id):
    try:
        # Get contract from agent's memory
        if contract_id not in contract_agent.contracts:
            return jsonify({'error': 'Contract not found'}), 404
        
        contract_data = contract_agent.contracts[contract_id]
        
        # Extract the contract content (text version)
        content = contract_data.get('content', '')
        
        if not content:
            return jsonify({'error': 'No content available'}), 404
        
        return jsonify({
            'success': True,
            'content': content,
            'contract_id': contract_id
        })
        
    except Exception as e:
        logger.error(f"Error in get-contract-content: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "Visit / for API documentation"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    logger.info(f"Starting KontrataPH LLM API server on {FLASK_HOST}:{FLASK_PORT}")
    
    print(f"\n{'='*60}")
    print(f" KontrataPH API Server Starting...")
    print(f"{'='*60}")
    print(f" MODE: LLM-Powered (Ollama)")
    print(f" Server URL: http://localhost:{FLASK_PORT}")
    print(f" API Docs:   http://localhost:{FLASK_PORT}/")
    print(f" Health:     http://localhost:{FLASK_PORT}/health")
    print(f" CORS:       Enabled")
    
    # Check LLM status
    if contract_agent.llm_available:
        print(f"\nLLM Status: CONNECTED")
        print(f"Model: {contract_agent.model}")
        print(f"Ollama URL: {contract_agent.ollama_url}")
    else:
        print(f"\nLLM Status: NOT CONNECTED")
        print(f"Ollama not running or not installed")
        print(f"\nTo enable LLM:")
        print(f"   1. Install Ollama: https://ollama.com/download")
        print(f"   2. Run: ollama pull llama3.2")
        print(f"   3. Restart this server")
        print(f"\n Running in fallback mode (rule-based)")
    
    print(f"\nAvailable Endpoints:")
    print(f"   POST /api/chat              - Chat interface (LLM-powered)")
    print(f"   POST /api/generate-contract - Generate contracts")
    print(f"   POST /api/analyze-contract  - Analyze contracts (LLM)")
    print(f"   GET  /api/contract-types    - Get contract types")
    
    print(f"\nFrontend:")
    print(f"   Open index.html in your browser")
    
    print(f"\n{'='*60}\n")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )