#/backend/agents/llm_contract_agent.py
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger
import uuid
from datetime import datetime
import json
import re
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except:
    REQUESTS_AVAILABLE = False

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available - using fallback")

class ProperLLMAgent:
    """
    Contract Agent with:
    - Entity extraction
    - Dynamic field detection
    - Analysis
    - Q&A system
    - Special clause generation
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.sessions = {}
        self.contracts = {}
        self.model = "llama3.2"
        
        # Check LLM availability
        self.llm_available = self._check_ollama()
        
        # Load Philippine law JSON files
        self.ph_laws = self._load_law_files()
        
        # Contract-related keywords for scope restriction
        self.contract_keywords = {
            'contract', 'agreement', 'lease', 'rent', 'employment', 'job',
            'partnership', 'business', 'buy', 'sell', 'labor', 'worker',
            'salary', 'wage', 'clause', 'party', 'parties', 'term',
            'generate', 'create', 'analyze', 'review', 'legal', 'law',
            'what', 'how', 'when', 'maximum', 'minimum', 'ground', 'requirement'
        }
        
        logger.info(f"ProperLLMAgent initialized (Ollama: {'✓' if self.llm_available else '✗'}, Laws: {len(self.ph_laws)})")
    
    def _load_law_files(self) -> Dict:
        """Load Philippine law JSON files"""
        laws = {}
        law_dir = Path("data/laws")
        
        if law_dir.exists():
            for law_file in law_dir.glob("*.json"):
                try:
                    with open(law_file, 'r', encoding='utf-8') as f:
                        law_data = json.load(f)
                        laws[law_file.stem] = law_data
                        logger.info(f"Loaded law file: {law_file.name}")
                except Exception as e:
                    logger.error(f"Error loading {law_file}: {e}")
        
        return laws
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        if not REQUESTS_AVAILABLE:
            return False
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _call_llm(self, prompt: str, system_prompt: str = None, max_tokens: int = 500) -> str:
        """Call Ollama LLM"""
        if not self.llm_available:
            return None
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            
            return None
        
        except Exception as e:
            logger.error(f"LLM call error: {str(e)}")
            return None
    
    # ========================================
    # FIELD DETECTION
    # ========================================
    
    def _get_required_fields(self, contract_type: str) -> List[str]:
        """
        Dynamically detect ALL fields from contract generator
        Treats fields with placeholder defaults like '[EMPLOYER]' as required
        Only excludes fields with meaningful defaults
        """
        required = []
        
        try:
            import importlib
            import inspect
            import sys
            
            generators = {
                'EMPLOYMENT': 'contract_generator.employment',
                'PARTNERSHIP': 'contract_generator.partnership',
                'LEASE': 'contract_generator.lease',
                'BUY_SELL': 'contract_generator.buy_sell'
            }
            
            if contract_type not in generators:
                logger.warning(f"Unknown contract type: {contract_type}")
                return []
            
            # Reload module to get latest changes
            gen_module_name = generators[contract_type]
            
            if gen_module_name in sys.modules:
                gen_module = importlib.reload(sys.modules[gen_module_name])
            else:
                gen_module = importlib.import_module(gen_module_name)
            
            generator = gen_module.ContractGenerator()
            source = inspect.getsource(generator.generate)
            
            # Method 1: Find details.get('field_name', default)
            # Captures both field name and default value
            get_pattern = r"details\.get\(['\"]([a-z_]+)['\"](?:,\s*([^)]+))?\)"
            matches = re.findall(get_pattern, source)
            
            for field_name, default_value in matches:
                # Skip special system fields
                if field_name in ['special_clauses', 'applicable_laws']:
                    continue
                
                # Check if default is a placeholder (required) or meaningful (optional)
                is_required = self._is_field_required(field_name, default_value)
                
                if is_required:
                    required.append(field_name)
                    logger.info(f"  ✓ Required: {field_name} (default: {default_value[:30] if default_value else 'None'})")
                else:
                    logger.info(f"  ○ Optional: {field_name} (has meaningful default)")
            
            # Method 2: Find direct access details['field_name']
            direct_pattern = r"details\[(['\"])([a-z_]+)\1\]"
            direct_matches = re.findall(direct_pattern, source)
            for _, field_name in direct_matches:
                if field_name not in required and field_name not in ['special_clauses', 'applicable_laws']:
                    required.append(field_name)
            
            # Remove duplicates while preserving order
            required = list(dict.fromkeys(required))
            
            logger.info(f" Detected {len(required)} required fields for {contract_type}: {required}")
            return required
        
        except Exception as e:
            logger.error(f"Error detecting fields: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback
            fallback = {
                'EMPLOYMENT': ['employer_name', 'employee_name', 'position', 'salary', 'start_date', 
                            'employment_type', 'work_hours', 'benefits'],
                'PARTNERSHIP': ['partner_names', 'business_name', 'partnership_type', 
                            'capital_contribution', 'profit_sharing_ratio', 'business_address'],
                'LEASE': ['lessor_name', 'lessee_name', 'property_address', 'rental_amount', 
                        'lease_period', 'payment_terms', 'property_use'],
                'BUY_SELL': ['seller_name', 'buyer_name', 'item_description', 'purchase_price',
                            'payment_terms', 'delivery_terms', 'delivery_date']
            }
            return fallback.get(contract_type, [])

    def _is_field_required(self, field_name: str, default_value: str) -> bool:
        """
        Determine if a field is required based on its default value
        
        Required if:
        - No default value
        - Default is a placeholder like '[EMPLOYER]', '[POSITION]'
        - Default is datetime.now() (means no user input)
        
        Optional if:
        - Default is meaningful like 'Regular', 'As per company policy'
        """
        if not default_value:
            return True
        
        default_clean = default_value.strip().strip("'\"")
        
        # Placeholders (required)
        if default_clean.startswith('[') and default_clean.endswith(']'):
            return True
        
        # Datetime defaults (required - means we want user input)
        if 'datetime' in default_value or '.strftime' in default_value:
            return True
        
        # Meaningful defaults (optional)
        optional_defaults = [
            'as per', 'according to', 'per company policy',
            'regular', 'full payment', 'monthly', 'quarterly',
            'as agreed', 'to be determined', 'n/a', 'none'
        ]
        
        default_lower = default_clean.lower()
        if any(opt in default_lower for opt in optional_defaults):
            return False  # Optional - has meaningful default
        
        # Very short defaults are probably meaningful
        if len(default_clean) > 50:
            return True  # Long defaults are usually placeholders
        
        # If unsure, treat as required
        return True
    
    # ========================================
    # SCOPE RESTRICTION
    # ========================================
    
    def _is_in_scope(self, message: str) -> bool:
        """Check if message is about contracts/law"""
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in self.contract_keywords)
    
    # ========================================
    # LAYER C1: USER INTENT DETECTION
    # ========================================
    
    def _detect_intent_c1(self, message: str) -> Dict:
        """
        C1: FIXED User Intent Detection
        """
        msg = message.lower()
        
        logger.info(f"Detecting intent for: '{message}'")
        
        # Greeting - must check FIRST before other patterns
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(msg.strip().startswith(w) for w in greeting_words):
            # Only greeting if it's JUST a greeting
            other_words = msg.split()
            if len(other_words) <= 2:  # Just "hi" or "hello there"
                logger.info("  -> GREETING detected")
                return {"intent": "GREETING", "contract_type": None, "confidence": 1.0}
        
        # Analysis - check for "analyze this contract:" or similar
        analysis_patterns = [
            'analyze this contract',
            'analyze contract',
            'review this contract',
            'check this contract',
            'examine this contract',
            'look at this contract'
        ]
        if any(pattern in msg for pattern in analysis_patterns):
            logger.info("  -> ANALYZE_CONTRACT detected")
            return {"intent": "ANALYZE_CONTRACT", "contract_type": None, "confidence": 1.0}
        
        # Contract generation
        contract_type = self._detect_contract_type(message)
        
        generation_patterns = [
            'create', 'generate', 'make', 'need', 'want', 
            'draft', 'get', 'prepare', 'build', 'write'
        ]
        
        contract_words = ['contract', 'agreement', 'lease', 'employment', 'partnership']
        
        has_generation_word = any(kw in msg for kw in generation_patterns)
        has_contract_word = any(kw in msg for kw in contract_words)
        
        # Direct pattern: "create partnership contract", "I need employment contract"
        if has_generation_word and (has_contract_word or contract_type):
            logger.info(f"  -> CREATE_CONTRACT detected (type: {contract_type})")
            return {
                "intent": "CREATE_CONTRACT",
                "contract_type": contract_type,
                "confidence": 1.0
            }
        
        # Also detect contract type mentions even without generation words
        # E.g., "partnership contract", "employment agreement"
        if contract_type and has_contract_word:
            logger.info(f"  -> CREATE_CONTRACT detected (implicit, type: {contract_type})")
            return {
                "intent": "CREATE_CONTRACT",
                "contract_type": contract_type,
                "confidence": 0.9
            }
        
        # Question about laws/contracts
        question_words = ['what', 'how', 'when', 'where', 'why', 'can', 'is', 'are', 
                        'maximum', 'minimum', 'law', 'ground', 'requirement', 'tell me']
        if any(msg.strip().startswith(q) for q in question_words) or '?' in msg:
            if self._is_in_scope(message):
                logger.info("  -> QUESTION detected")
                return {"intent": "QUESTION", "contract_type": None, "confidence": 0.9}
        
        # Out of scope check
        if not self._is_in_scope(message):
            logger.info("  -> OUT_OF_SCOPE detected")
            return {"intent": "OUT_OF_SCOPE", "contract_type": None, "confidence": 1.0}
        
        # If we're already in a contract generation flow, this is probably providing info
        logger.info("  -> PROVIDING_INFO (default)")
        return {"intent": "PROVIDING_INFO", "contract_type": None, "confidence": 0.5}
    
    def _detect_contract_type(self, message: str) -> Optional[str]:
        """Detect contract type from message"""
        msg = message.lower()
        
        # More specific patterns to avoid false positives
        type_patterns = {
            'EMPLOYMENT': [
                r'\bemployment\b',
                r'\bemployee\b',
                r'\bjob\b',
                r'\bhire\b',
                r'\bwork\b',
                r'\bworker\b',
                r'\blabor\b',
                r'\blabour\b'
            ],
            'PARTNERSHIP': [
                r'\bpartnership\b',
                r'\bpartner\b',
                r'\bbusiness partner\b',
                r'\bjoint venture\b'
            ],
            'LEASE': [
                r'\blease\b',
                r'\brent\b',
                r'\brental\b',
                r'\bproperty\b',
                r'\blessor\b',
                r'\blessee\b'
            ],
            'BUY_SELL': [
                r'\bbuy\b',
                r'\bsell\b',
                r'\bpurchase\b',
                r'\bsale\b',
                r'\bbuyer\b',
                r'\bseller\b'
            ]
        }
        
        for contract_type, patterns in type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, msg):
                    logger.info(f"    Contract type: {contract_type} (matched: {pattern})")
                    return contract_type
        
        logger.info("    No contract type detected")
        return None
    
    # ========================================
    #  SPECIAL CLAUSE GENERATION
    # ========================================
    
    def _generate_special_clause(self, user_request: str, contract_type: str) -> str:
        """
        Generate a special clause based on user's natural language request
        
        Examples:
        - "non-disclosure agreement" → full NDA clause
        - "non-compete clause" → non-compete with reasonable restrictions
        - "confidentiality" → confidentiality clause
        """
        if not self.llm_available:
            # Fallback: return user's request as-is
            return user_request
        
        system_prompt = f"""You are a Philippine contract law expert. Generate ONLY the clause text.

CRITICAL RULES:
- Start directly with the clause title (e.g., "NON-DISCLOSURE AGREEMENT")
- NO preamble, NO "Here's a clause", NO disclaimers
- NO "I can't provide legal advice" or similar text
- Just the pure legal clause text
- Use proper Philippine contract formatting

Contract type: {contract_type}"""

        prompt = f"""Generate a complete {user_request} clause for a {contract_type.replace('_', ' ')} contract.

Output ONLY the clause text, starting with the clause title. No introduction, no explanation.

Example format:
NON-DISCLOSURE AGREEMENT

1. Definition of Confidential Information...
2. Obligations...

Now generate the clause:"""
        
        clause = self._call_llm(prompt, system_prompt, max_tokens=600)
        
        if clause:
            #  POST-PROCESSING: Remove common preamble patterns
            clause = self._clean_generated_clause(clause)
            logger.info(f"Generated special clause: {clause[:100]}...")
            return clause.strip()
        
        # Fallback
        return user_request
    
    def _clean_generated_clause(self, clause: str) -> str:
        """
        Remove preamble text from generated clauses
        
        Removes patterns like:
        - "I can't provide legal advice, but..."
        - "Here's a sample clause:"
        - "Here's the clause:"
        - etc.
        """
        original_clause = clause
        
        # Step 1: Remove everything up to and including common preamble phrases
        preamble_cutoffs = [
            r"^.*?I can't provide legal advice.*?(?:clause|agreement|provision):\s*",
            r"^.*?Here's a sample.*?(?:clause|agreement|provision):\s*",
            r"^.*?Here's the.*?:\s*",
            r"^.*?Below is.*?:\s*",
        ]
        
        for pattern in preamble_cutoffs:
            cleaned = re.sub(pattern, '', clause, flags=re.IGNORECASE | re.DOTALL)
            if len(cleaned) < len(clause):
                clause = cleaned
                break
        
        # Step 2: Find the first line that looks like a clause title (ALL CAPS or numbered)
        # and remove everything before it
        lines = clause.split('\n')
        clause_start_index = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this looks like a clause title
            # Pattern 1: ALL CAPS text (e.g., "NON-DISCLOSURE AGREEMENT")
            if line_stripped and line_stripped.isupper() and len(line_stripped) > 5:
                clause_start_index = i
                break
            
            # Pattern 2: Numbered clause (e.g., "1. Definition")
            if re.match(r'^\d+\.', line_stripped):
                clause_start_index = i
                break
            
            # Pattern 3: Text ending with "AGREEMENT" or "CLAUSE" (title case)
            if re.search(r'(AGREEMENT|CLAUSE|PROVISION)$', line_stripped):
                clause_start_index = i
                break
        
        # Reconstruct clause starting from the title
        if clause_start_index > 0:
            clause = '\n'.join(lines[clause_start_index:])
        
        # Step 3: Remove any remaining disclaimer patterns at the start
        disclaimer_patterns = [
            r'^.*?I can.*?advice.*?\n',
            r'^.*?sample.*?clause.*?\n',
            r'^.*?Please.*?note.*?\n',
            r'^.*?Disclaimer.*?\n',
        ]
        
        for pattern in disclaimer_patterns:
            clause = re.sub(pattern, '', clause, flags=re.IGNORECASE | re.MULTILINE)
        
        # Step 4: Clean up whitespace
        clause = clause.strip()
        
        # If we ended up with nothing, return original
        if not clause or len(clause) < 20:
            logger.warning("Clause cleaning removed too much, using original")
            return original_clause.strip()
        
        logger.info(f"Cleaned clause: {clause[:100]}...")
        return clause
    
    def _is_clause_request(self, message: str) -> bool:
        """Detect if user is requesting a specific type of clause to be generated"""
        msg_lower = message.lower()
        
        clause_keywords = [
            'non-disclosure', 'nda', 'confidentiality', 'non-compete',
            'non-solicitation', 'intellectual property', 'ip rights',
            'termination clause', 'penalty clause', 'arbitration',
            'force majeure', 'warranty', 'indemnity', 'liability'
        ]
        
        request_words = ['add', 'include', 'want', 'need', 'put in']
        
        has_clause_keyword = any(kw in msg_lower for kw in clause_keywords)
        has_request_word = any(kw in msg_lower for kw in request_words)
        
        # Short message mentioning a clause type
        if has_clause_keyword and (has_request_word or len(msg_lower.split()) <= 6):
            return True
        
        return False
    
    def process_message(
        self,
        message: str,
        session_id: str = 'default',
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        FIXED: Main entry point
        """
        try:
            session = self._get_or_create_session(session_id)
            
            session['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"\n{'='*60}")
            logger.info(f"PROCESSING MESSAGE: {message[:100]}")
            logger.info(f"Session in contract flow: {session.get('awaiting_details')}")
            logger.info(f"Session contract type: {session.get('contract_type')}")
            
            # If in contract generation flow, continue collecting info
            if session.get('awaiting_details'):
                logger.info("Continuing contract flow...")
                return self._handle_generation_flow(message, session, {})
            
            # C1: Detect Intent
            intent_result = self._detect_intent_c1(message)
            intent = intent_result['intent']
            
            logger.info(f"INTENT DETECTED: {intent}")
            logger.info(f"{'='*60}\n")
            
            # Handle out of scope
            if intent == "OUT_OF_SCOPE":
                response = "I'm KontrataPH, your contract assistant. I can help with:\n\n• Generating contracts (Employment, Partnership, Lease, Buy & Sell)\n• Analyzing contracts\n• Answering questions about Philippine contract law\n\nWhat would you like help with?"
                session['messages'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                return {"response": response, "intent": "OUT_OF_SCOPE"}
            
            # Handle greeting
            if intent == "GREETING":
                return self._handle_greeting(session)
            
            # Handle contract generation
            if intent == "CREATE_CONTRACT":
                return self._handle_generation_flow(message, session, intent_result)
            
            # Handle analysis - FIXED to handle text contracts
            if intent == "ANALYZE_CONTRACT":
                # Check if there's actual contract text in the message
                # Pattern: "analyze this contract: [contract text]"
                contract_text = None
                
                # Try to extract contract text after colon
                if ':' in message:
                    parts = message.split(':', 1)
                    if len(parts) > 1:
                        contract_text = parts[1].strip()
                
                # Or if the message is very long, assume it's all contract text
                elif len(message) > 500:
                    contract_text = message
                
                if contract_text:
                    logger.info(f"Analyzing text contract ({len(contract_text)} chars)")
                    # Analyze the text directly
                    analysis = self.analyze_contract_text(contract_text)
                    
                    response = " Contract analysis complete! Check the panel for details."
                    session['messages'].append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    return {
                        "response": response,
                        "intent": "ANALYZE_CONTRACT",
                        "analysis": analysis,
                        **analysis  # Include all analysis fields
                    }
                else:
                    return {
                        "response": "I can analyze your contract! Please either:\n\n1. Upload a file using the  button, OR\n2. Paste the contract text after 'analyze this contract:'\n\nExample: analyze this contract: [paste contract text here]",
                        "intent": "ANALYZE_CONTRACT"
                    }
            
            # Handle questions
            if intent == "QUESTION":
                return self._handle_question(message, session)
            
            # Providing info during generation
            if intent == "PROVIDING_INFO" and session.get('contract_type'):
                return self._handle_generation_flow(message, session, {})
            
            return {
                "response": "I can help you generate contracts, analyze contracts, or answer questions about Philippine law. What would you like to do?",
                "intent": "UNKNOWN"
            }
        
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": "I encountered an error. Please try again.",
                "error": str(e)
            }
    # ========================================
    # LAYER C2: DIALOGUE STATE TRACKING
    # ========================================
    
    def _update_state_c2(self, session: Dict, new_data: Dict) -> Dict:
        """
        C2: Dialogue State Tracking
        Track which fields are filled and which are still needed
        """
        contract_type = session.get('contract_type')
        if not contract_type:
            return {}
        
        # Get required fields dynamically from generator
        required = self._get_required_fields(contract_type)
        
        logger.info(f"Required fields for {contract_type}: {required}")
        
        # Update details with new data
        details = session.get('details', {})
        details.update(new_data)
        
        # Determine filled and missing
        # A field is "filled" if it has a value that's not empty/placeholder
        filled = []
        missing = []
        
        for field in required:
            value = details.get(field)
            
            # Check if field is actually filled
            if value and self._is_value_filled(value):
                filled.append(field)
            else:
                missing.append(field)
        
        logger.info(f"Filled: {filled}")
        logger.info(f"Missing: {missing}")
        
        state = {
            "contract_type": contract_type,
            "filled": filled,
            "missing": missing,
            "details": details,
            "completion": len(filled) / len(required) if required else 0
        }
        
        return state

    def _is_value_filled(self, value) -> bool:
        """
        Check if a value is actually filled (not empty or placeholder)
        """
        if not value:
            return False
        
        if isinstance(value, list):
        # List is filled if it has at least one non-empty item
            return len(value) > 0 and any(item and str(item).strip() for item in value)
    
        # Convert to string for checking
        value_str = str(value).strip()
        
        # Empty or whitespace
        if not value_str:
            return False
        
        # Placeholder patterns
        placeholder_patterns = [
            r'^\[.*\]$',  # [ANYTHING]
            r'^\.\.\.+$',  # ...
            r'^to be determined$',
            r'^tbd$',
            r'^n/?a$',
        ]
        
        value_lower = value_str.lower()
        for pattern in placeholder_patterns:
            if re.match(pattern, value_lower):
                return False
        
        # Value is filled
        return True
    
    # ========================================
    # LAYER C3: ENTITY EXTRACTION
    # ========================================
    
    def _extract_entities_c3(self, message: str, contract_type: str) -> Dict:
        """
        C3: Entity/Slot Extraction
        Uses multiple methods in priority order
        """
        extracted = {}
        
        # Get required fields for this contract type
        required_fields = self._get_required_fields(contract_type)
        
        if contract_type == 'PARTNERSHIP' and 'partner_names' in required_fields:
            partners = self._extract_partner_names(message)
            if partners:
                extracted['partner_names'] = partners

        # Method 1: LLM extraction (most accurate)
        if self.llm_available:
            llm_extracted = self._llm_extraction(message, contract_type, required_fields)
            for key, value in llm_extracted.items():
                if key not in extracted:
                    extracted[key] = value
        
        # Method 2: Enhanced regex patterns
        regex_extracted = self._regex_extraction(message, required_fields)
        # Only add regex results if LLM didn't extract them
        for key, value in regex_extracted.items():
            if key not in extracted:
                extracted[key] = value
        
        # Method 3: spaCy NER (if available)
        if SPACY_AVAILABLE:
            spacy_extracted = self._spacy_extraction(message, required_fields)
            for key, value in spacy_extracted.items():
                if key not in extracted:
                    extracted[key] = value
        
        return extracted
    
    def _llm_extraction(self, message: str, contract_type: str, required_fields: List[str]) -> Dict:
        """LLM extraction with field hints"""
        
        fields_list = "\n".join([f"- {field}" for field in required_fields])
        
        system_prompt = f"""You are extracting contract information from a user's message.

Contract type: {contract_type}

Expected fields:
{fields_list}

Extract ONLY information that is EXPLICITLY mentioned. Return as JSON.
Use exact field names from the list above.

SPECIAL RULES:
- For "partner_names": ALWAYS return as array ["Name 1", "Name 2"]
- For fields with multiple values separated by "and", "," or similar, return as array

Example:
If user says "Partner Names: Mark Joseph and Jaedan Bahala"
Return: {{"partner_names": ["Mark Joseph", "Jaedan Bahala"]}}

If user says "Employer: ABC Corp, Employee: John Doe, Salary: 50000"
Return: {{"employer_name": "ABC Corp", "employee_name": "John Doe", "salary": "50000"}}

IMPORTANT:
- Only include fields that are present in the message
- Use exact values from the message
- Capitalize names properly
- For money, extract just the number
- For dates, keep the format from message
"""

        prompt = f'User message: "{message}"\n\nExtract information as JSON with only the fields present in the message:'
        
        llm_response = self._call_llm(prompt, system_prompt, max_tokens=400)
        
        if llm_response:
            try:
                # Try to find JSON in response
                json_match = re.search(r'\{[^\}]+\}', llm_response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())

                    if contract_type == 'PARTNERSHIP' and 'partner_names' in data:
                        # Ensure it's a list
                        if isinstance(data['partner_names'], str):
                            # Try to split by common separators
                            partners_str = data['partner_names']
                            if ' and ' in partners_str:
                                data['partner_names'] = [p.strip() for p in partners_str.split(' and ')]
                            elif ',' in partners_str:
                                data['partner_names'] = [p.strip() for p in partners_str.split(',')]
                            else:
                                # Just one partner mentioned?
                                data['partner_names'] = [partners_str.strip()]
                    
                    # Filter out empty/placeholder values
                    return {k: v for k, v in data.items() 
                        if v and v not in ['...', 'N/A', 'null', 'None', '']}
            except Exception as e:
                logger.error(f"LLM extraction parse error: {e}")
        
        return {}
    
    def _regex_extraction(self, message: str, required_fields: List[str]) -> Dict:
        """regex extraction based on required fields"""
        extracted = {}
        msg_lower = message.lower()
        
        # Generic patterns that work for any field
        for field in required_fields:
            # Pattern: "field_name: value" or "field name: value"
            field_variants = [
                field,
                field.replace('_', ' '),
                field.replace('_', '-')
            ]
            
            for variant in field_variants:
                # Try colon separator
                pattern = rf"{re.escape(variant)}\s*[:\-]\s*([^,\n]+?)(?:,|\.|\n|$)"
                match = re.search(pattern, msg_lower, re.IGNORECASE)
                
                if match:
                    value = match.group(1).strip()
                    
                    # Clean up value
                    value = value.strip('•').strip()
                    
                    # Remove common prefixes
                    value = re.sub(r'^(php|usd)\s*', '', value, flags=re.IGNORECASE)
                    
                    # Capitalize if it's a name field
                    if 'name' in field:
                        value = ' '.join(word.capitalize() for word in value.split())
                    
                    extracted[field] = value
                    break
        
        return extracted
    
    def _spacy_extraction(self, message: str, required_fields: List[str]) -> Dict:
        """spaCy extraction"""
        extracted = {}
        doc = nlp(message)
        
        # Map entities to fields
        name_fields = [f for f in required_fields if 'name' in f]
        money_fields = [f for f in required_fields if 'salary' in f or 'rent' in f or 'price' in f or 'amount' in f]
        date_fields = [f for f in required_fields if 'date' in f]
        
        for ent in doc.ents:
            if ent.label_ == "PERSON" and name_fields:
                # Assign to first unfilled name field
                for field in name_fields:
                    if field not in extracted:
                        extracted[field] = ent.text
                        break
            
            elif ent.label_ == "MONEY" and money_fields:
                amount = re.sub(r'[^\d]', '', ent.text)
                for field in money_fields:
                    if field not in extracted:
                        extracted[field] = amount
                        break
            
            elif ent.label_ == "DATE" and date_fields:
                for field in date_fields:
                    if field not in extracted:
                        extracted[field] = ent.text
                        break
        
        return extracted
    
    def _extract_partner_names(self, message: str) -> List[str]:
        """Extract partner names from message"""
        msg_lower = message.lower()
        partners = []
        
        # Pattern 1: "Partner Names: X and Y"
        match = re.search(r'partner\s*names?\s*:\s*([^,\n]+?)(?:,|\n|$)', msg_lower, re.IGNORECASE)
        if match:
            names_str = match.group(1).strip()
            # Split by 'and'
            if ' and ' in names_str:
                partners = [n.strip().title() for n in names_str.split(' and ')]
            # Split by comma
            elif ',' in names_str:
                partners = [n.strip().title() for n in names_str.split(',')]
            else:
                partners = [names_str.strip().title()]
        
        # Pattern 2: "Partner A: X, Partner B: Y"
        partner_pattern = r'partner\s*[a-z]?\s*:\s*([^,\n]+?)(?:,|partner|\n|$)'
        matches = re.findall(partner_pattern, message, re.IGNORECASE)
        if matches and not partners:
            partners = [m.strip().title() for m in matches]
        
        return partners
    # ========================================
    # LAYER C4: PHILIPPINE LAW VALIDATION
    # ========================================
    
    def _validate_against_law_c4(self, contract_type: str, details: Dict) -> Dict:
        """C4: Philippine Law Validation"""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "applied_defaults": []
        }
        
        law_key = contract_type.lower()
        if law_key not in self.ph_laws:
            validation["warnings"].append(f"No Philippine law file loaded for {contract_type}")
            return validation
        
        laws = self.ph_laws[law_key]
        
        # Validate required clauses
        if 'required_clauses' in laws:
            for clause in laws['required_clauses']:
                clause_name = clause.get('name')
                if clause_name not in details or not details[clause_name]:
                    if 'default' in clause:
                        details[clause_name] = clause['default']
                        validation["applied_defaults"].append(
                            f"{clause_name.replace('_', ' ').title()}: {clause['default']}"
                        )
                    elif clause.get('mandatory', False):
                        validation["errors"].append(
                            f"Missing required: {clause_name.replace('_', ' ').title()}"
                        )
                        validation["valid"] = False
        
        # Validate constraints
        if 'constraints' in laws:
            for field, constraint in laws['constraints'].items():
                if field in details and details[field]:
                    value = details[field]
                    
                    try:
                        if 'min' in constraint or 'max' in constraint:
                            if isinstance(value, str):
                                value_num = float(value.replace(',', ''))
                            else:
                                value_num = float(value)
                            
                            if 'min' in constraint and value_num < constraint['min']:
                                validation["errors"].append(
                                    f"{field.replace('_', ' ').title()}: Below minimum of {constraint['min']}"
                                )
                                validation["valid"] = False
                            
                            if 'max' in constraint and value_num > constraint['max']:
                                validation["warnings"].append(
                                    f"{field.replace('_', ' ').title()}: Above maximum of {constraint['max']}"
                                )
                    except (ValueError, TypeError):
                        pass
        
        return validation
    
    # ========================================
    # Q&A SYSTEM
    # ========================================
    
    def _handle_question(self, message: str, session: Dict) -> Dict:
        """Handle questions about Philippine contract law using RAG"""
        
        # Search through law files for relevant info
        relevant_info = self._search_law_knowledge(message)
        
        if not relevant_info:
            return {
                "response": "I couldn't find specific information about that in my Philippine law database. Could you rephrase your question or ask about:\n\n• Employment law requirements\n• Lease duration limits\n• Partnership formation grounds\n• Buy and sell requirements",
                "intent": "QUESTION"
            }
        
        # Use LLM to generate answer if available
        if self.llm_available:
            answer = self._generate_law_answer(message, relevant_info)
            if answer:
                session['messages'].append({
                    'role': 'assistant',
                    'content': answer,
                    'timestamp': datetime.now().isoformat()
                })
                return {
                    "response": answer,
                    "intent": "QUESTION",
                    "sources": relevant_info['sources']
                }
        
        # Fallback: Just return the relevant info
        response = "Based on Philippine law:\n\n"
        response += relevant_info['text']
        
        if relevant_info['sources']:
            response += f"\n\nSource: {', '.join(relevant_info['sources'])}"
        
        return {
            "response": response,
            "intent": "QUESTION"
        }
    
    def _search_law_knowledge(self, question: str) -> Dict:
        """Search law JSON files for relevant information"""
        question_lower = question.lower()
        relevant = {"text": "", "sources": []}
        
        # Keywords to match
        keywords = {
            'maximum': ['max', 'maximum', 'limit', 'ceiling'],
            'minimum': ['min', 'minimum', 'floor'],
            'duration': ['duration', 'term', 'period', 'year', 'month'],
            'wage': ['wage', 'salary', 'pay', 'compensation'],
            'ground': ['ground', 'basis', 'reason', 'requirement'],
            'termination': ['termination', 'end', 'terminate', 'cancel']
        }
        
        # Determine what user is asking about
        topic = None
        for key, variants in keywords.items():
            if any(v in question_lower for v in variants):
                topic = key
                break
        
        # Search through law files
        for law_name, law_data in self.ph_laws.items():
            contract_type = law_data.get('contract_type', '')
            
            # Check if question is about this contract type
            if contract_type.lower() not in question_lower and law_name not in question_lower:
                # Check if it's a general question
                if not any(word in question_lower for word in ['what', 'general', 'all']):
                    continue
            
            # Search constraints
            if 'constraints' in law_data and topic in ['maximum', 'minimum', 'duration']:
                for field, constraint in law_data['constraints'].items():
                    if topic == 'maximum' and 'max' in constraint:
                        relevant['text'] += f"• {field.replace('_', ' ').title()}: Maximum {constraint['max']}\n"
                        if 'description' in constraint:
                            relevant['text'] += f"  ({constraint['description']})\n"
                        relevant['sources'].append(law_data.get('law_name', law_name))
                    
                    elif topic == 'minimum' and 'min' in constraint:
                        relevant['text'] += f"• {field.replace('_', ' ').title()}: Minimum {constraint['min']}\n"
                        if 'description' in constraint:
                            relevant['text'] += f"  ({constraint['description']})\n"
                        relevant['sources'].append(law_data.get('law_name', law_name))
            
            # Search required clauses
            if 'required_clauses' in law_data and topic == 'ground':
                relevant['text'] += f"\n{contract_type} Requirements:\n"
                for clause in law_data['required_clauses'][:5]:  # Limit to 5
                    if clause.get('mandatory'):
                        relevant['text'] += f"• {clause.get('description', clause['name'])}\n"
                relevant['sources'].append(law_data.get('law_name', law_name))
        
        # Deduplicate sources
        relevant['sources'] = list(set(relevant['sources']))
        
        return relevant
    
    def _generate_law_answer(self, question: str, context: Dict) -> str:
        """Generate answer using LLM with law context"""
        
        system_prompt = """You are a helpful Philippine contract law assistant.
Answer the user's question based on the provided law information.

Guidelines:
- Be clear and concise
- Use simple language for non-experts
- Cite the law source
- If asked for specific numbers (maximum, minimum), provide them clearly
- Explain WHY the law exists (purpose)
"""

        prompt = f"""Question: {question}

Law Information:
{context['text']}

Sources: {', '.join(context['sources'])}

Provide a clear, helpful answer for someone not expert in contracts:"""
        
        answer = self._call_llm(prompt, system_prompt, max_tokens=300)
        
        if answer:
            # Add sources at the end
            if context['sources']:
                answer += f"\n\n Legal basis: {', '.join(context['sources'])}"
            return answer.strip()
        
        return None
    
    # ========================================
    # MAIN PROCESS MESSAGE
    # ========================================
    
    def process_message(
        self,
        message: str,
        session_id: str = 'default',
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Main entry point"""
        try:
            session = self._get_or_create_session(session_id)
            
            session['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # If in contract generation flow
            if session.get('awaiting_details'):
                return self._handle_generation_flow(message, session, {})
            
            # C1: Detect Intent
            intent_result = self._detect_intent_c1(message)
            intent = intent_result['intent']
            
            logger.info(f"Intent: {intent}")
            
            # Handle out of scope
            if intent == "OUT_OF_SCOPE":
                response = "I'm KontrataPH, your contract assistant. I can help with:\n\n• Generating contracts (Employment, Partnership, Lease, Buy & Sell)\n• Analyzing contracts\n• Answering questions about Philippine contract law\n\nWhat would you like help with?"
                session['messages'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                return {"response": response, "intent": "OUT_OF_SCOPE"}
            
            # Handle greeting
            if intent == "GREETING":
                return self._handle_greeting(session)
            
            # Handle contract generation
            if intent == "CREATE_CONTRACT":
                return self._handle_generation_flow(message, session, intent_result)
            
            # Handle analysis
            if intent == "ANALYZE_CONTRACT":
                return {
                    "response": "I can analyze your contract! Please upload the file using the  button.",
                    "intent": "ANALYZE_CONTRACT"
                }
            
            # Handle questions
            if intent == "QUESTION":
                return self._handle_question(message, session)
            
            # Providing info during generation
            if intent == "PROVIDING_INFO" and session.get('contract_type'):
                return self._handle_generation_flow(message, session, {})
            
            return {
                "response": "I can help you generate contracts, analyze contracts, or answer questions about Philippine law. What would you like to do?",
                "intent": "UNKNOWN"
            }
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": "I encountered an error. Please try again.",
                "error": str(e)
            }
    
    def _handle_generation_flow(self, message: str, session: Dict, intent_result: Dict) -> Dict:
        """Handle contract generation flow with special clauses"""
        
        # Determine contract type
        if not session.get('contract_type'):
            contract_type = intent_result.get('contract_type')
            if not contract_type:
                return {
                    "response": "What type of contract do you need?\n\n• Employment (includes labor contracts)\n• Partnership\n• Lease\n• Buy and Sell",
                    "intent": "CREATE_CONTRACT"
                }
            session['contract_type'] = contract_type
            session['details'] = {}
            session['special_clauses'] = []
            session['asked_special_clauses'] = False
        else:
            # Check if requesting NEW contract
            msg_lower = message.lower()
            if any(kw in msg_lower for kw in ['new', 'another', 'different']):
                new_type = intent_result.get('contract_type')
                if new_type:
                    session['contract_type'] = new_type
                    session['details'] = {}
                    session['filled'] = []
                    session['missing'] = []
                    session['special_clauses'] = []
                    session['asked_special_clauses'] = False
                    session['awaiting_details'] = True
        
        contract_type = session['contract_type']
        
        # C3: Extract entities
        extracted = self._extract_entities_c3(message, contract_type)
        logger.info(f"Extracted: {extracted}")
        
        # C2: Update state
        state = self._update_state_c2(session, extracted)
        
        session['details'] = state['details']
        session['filled'] = state['filled']
        session['missing'] = state['missing']
        
        # Check if all required fields are filled
        if state['missing']:
            session['awaiting_details'] = True
            missing_nice = [f.replace('_', ' ').title() for f in state['missing']]
            
            response = f"Great! I'm collecting details for your {contract_type.replace('_', ' ').title()} contract.\n\n"
            if state['filled']:
                response += f" I have: {', '.join(f.replace('_', ' ').title() for f in state['filled'])}\n\n"
            response += f" I still need:\n" + "\n".join(f"  • {f}" for f in missing_nice)
            
            return {
                "response": response,
                "intent": "CREATE_CONTRACT",
                "requires_action": True,
                "contract_type": contract_type,
                "state": state
            }
        
        #  All required fields filled - now ask about special clauses
        if not session.get('asked_special_clauses'):
            session['asked_special_clauses'] = True
            session['awaiting_special_clauses'] = True
            
            response = f" All required information collected!\n\n"
            response += " Would you like to add any special clauses?\n\n"
            response += "Examples:\n"
            response += "  • 'Add a non-disclosure agreement'\n"
            response += "  • 'Include a non-compete clause'\n"
            response += "  • 'Add confidentiality terms'\n"
            response += "  • Or type your own custom clause\n\n"
            response += " I can generate standard clauses for you, or you can provide your own text.\n"
            response += "Type 'none' or 'skip' to continue without special clauses."
            
            return {
                "response": response,
                "intent": "CREATE_CONTRACT",
                "awaiting_special_clauses": True,
                "contract_type": contract_type
            }
        
        #  Handle special clauses input
        if session.get('awaiting_special_clauses'):
            msg_lower = message.lower().strip()
            
            # User wants to skip special clauses
            if msg_lower in ['none', 'skip', 'no', 'nothing', "i don't have any", "i don't have", "no thanks"]:
                session['awaiting_special_clauses'] = False
                session['awaiting_details'] = False
                # Proceed to validation and generation
            
            # User is done adding clauses
            elif msg_lower in ['done', 'finish', 'finished', 'complete', "that's all", "that's it"]:
                session['awaiting_special_clauses'] = False
                session['awaiting_details'] = False
                # Proceed to validation and generation
            
            #  User is requesting a specific clause type OR providing their own
            else:
                if 'special_clauses' not in session:
                    session['special_clauses'] = []
                
                # Check if this is a clause request (e.g., "add a non-compete clause")
                if self._is_clause_request(message):
                    # Generate the clause using LLM
                    generated_clause = self._generate_special_clause(message, contract_type)
                    session['special_clauses'].append(generated_clause)
                    
                    response = f" Generated and added special clause #{len(session['special_clauses'])}\n\n"
                    response += f" Preview:\n{generated_clause[:200]}{'...' if len(generated_clause) > 200 else ''}\n\n"
                else:
                    # User provided their own clause text
                    session['special_clauses'].append(message)
                    response = f" Added custom clause #{len(session['special_clauses'])}\n\n"
                
                response += f" Total clauses: {len(session['special_clauses'])}\n\n"
                response += f" Add more clauses, or type 'done' to finish."
                
                return {
                    "response": response,
                    "intent": "CREATE_CONTRACT",
                    "awaiting_special_clauses": True,
                    "contract_type": contract_type
                }
        
        #  All fields collected, special clauses handled - validate and generate
        session['awaiting_details'] = False
        session['awaiting_special_clauses'] = False
        
        validation = self._validate_against_law_c4(contract_type, session['details'])
        
        if not validation['valid']:
            return {
                "response": f"️ Validation errors:\n" + "\n".join(f"• {e}" for e in validation['errors']),
                "intent": "CREATE_CONTRACT",
                "validation": validation,
                "contract_type": contract_type
            }
        
        return self._generate_contract_c5c6(
            contract_type, 
            session['details'], 
            validation, 
            session,
            session.get('special_clauses', [])
        )
    
    def _format_contract_inputs(self, contract_type: str, details: Dict) -> Dict:
        """
        Format and clean all input fields before contract generation
        - Capitalize names properly
        - Clean monetary values
        - Standardize dates
        - Remove typos/extra characters
        """
        formatted = {}
        
        for field, value in details.items():
            if not value or value in ['[', ']', 'N/A', 'null', 'None']:
                continue
            
            # ⭐ SPECIAL: partner_names must stay as a list
            if field == 'partner_names':
                if isinstance(value, list):
                    # Format each partner name properly
                    formatted[field] = [self._format_name(name) for name in value]
                elif isinstance(value, str):
                    # If it's a string, try to convert it back to a list
                    # Handle case where it might be string representation of a list
                    if value.startswith('[') and value.endswith(']'):
                        # It's a string representation like "['Name1', 'Name2']"
                        try:
                            import ast
                            parsed = ast.literal_eval(value)
                            if isinstance(parsed, list):
                                formatted[field] = [self._format_name(name) for name in parsed]
                            else:
                                formatted[field] = [self._format_name(value)]
                        except:
                            # Failed to parse, treat as single name
                            formatted[field] = [self._format_name(value)]
                    else:
                        # Regular string, make it a single-item list
                        formatted[field] = [self._format_name(value)]
                continue
                
            # 1. NAME FIELDS - Proper capitalization
            if 'name' in field.lower():
                formatted[field] = self._format_name(value)
            
            # 2. ADDRESS FIELDS - Capitalize each word
            elif 'address' in field.lower():
                formatted[field] = self._format_address(value)
            
            # 3. MONETARY FIELDS - Clean and format
            elif any(money_word in field.lower() for money_word in ['salary', 'price', 'rent', 'amount', 'deposit', 'fee']):
                formatted[field] = self._format_money(value)
            
            # 4. DATE FIELDS - Standardize format
            elif 'date' in field.lower():
                formatted[field] = self._format_date(value)
            
            # 5. DURATION/PERIOD FIELDS - Clean typos
            elif any(duration_word in field.lower() for duration_word in ['duration', 'period', 'term']):
                formatted[field] = self._format_duration(value)
            
            # 6. DESCRIPTION FIELDS - Capitalize first letter
            elif 'description' in field.lower():
                formatted[field] = self._format_description(value)
            
            # 7. POSITION/TITLE FIELDS - Title case
            elif 'position' in field.lower() or 'title' in field.lower():
                formatted[field] = self._format_title(value)
            
            # 8. Everything else - Basic cleanup
            else:
                formatted[field] = self._basic_cleanup(value)
        
        logger.info(f"Formatted inputs: {formatted}")
        return formatted

    def _format_name(self, name: str) -> str:
        """Format person names: 'mark neypes' -> 'Mark Neypes'"""
        if not isinstance(name, str):
            return str(name)
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        # Handle all caps or all lowercase
        # Split by space and capitalize each word
        words = name.split()
        formatted_words = []
        
        for word in words:
            # Handle name particles (de, dela, san, etc.)
            if word.lower() in ['de', 'del', 'dela', 'delos', 'las', 'los', 'san', 'jr', 'sr', 'ii', 'iii', 'iv']:
                formatted_words.append(word.lower() if word.lower() != 'jr' and word.lower() != 'sr' else word.upper() + '.')
            else:
                # Capitalize first letter, lowercase rest
                formatted_words.append(word.capitalize())
        
        return ' '.join(formatted_words)

    def _format_address(self, address: str) -> str:
        """Format addresses: Capitalize appropriately"""
        if not isinstance(address, str):
            return str(address)
        
        # Remove extra spaces
        address = ' '.join(address.split())
        
        # Capitalize each word except small words after first word
        words = address.split()
        formatted_words = []
        
        for i, word in enumerate(words):
            # Always capitalize first word
            if i == 0:
                formatted_words.append(word.capitalize())
            # Small words stay lowercase unless they're first
            elif word.lower() in ['of', 'and', 'the', 'in', 'at', 'to']:
                formatted_words.append(word.lower())
            else:
                formatted_words.append(word.capitalize())
        
        return ' '.join(formatted_words)

    def _format_money(self, value: str) -> str:
        """Format money: '3,000' or 'PHP 3,000' or '3000' -> '3,000'"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove 'PHP', '$', spaces
        clean = re.sub(r'[^\d,.]', '', value)
        
        # Remove existing commas
        clean = clean.replace(',', '')
        
        # If it's a valid number, format with commas
        try:
            amount = float(clean)
            # Format with commas
            return f"{amount:,.2f}".rstrip('0').rstrip('.')
        except:
            return value

    def _format_date(self, date_str: str) -> str:
        """Format dates consistently: 'january 1, 2026' -> 'January 1, 2026'"""
        if not isinstance(date_str, str):
            return str(date_str)
        
        # Try to parse and reformat common date formats
        date_str = date_str.strip()
        
        # Already well formatted (Month DD, YYYY)
        if re.match(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$', date_str):
            return date_str
        
        # Fix capitalization for month names
        months = {
            'january': 'January', 'february': 'February', 'march': 'March',
            'april': 'April', 'may': 'May', 'june': 'June',
            'july': 'July', 'august': 'August', 'september': 'September',
            'october': 'October', 'november': 'November', 'december': 'December'
        }
        
        for month_lower, month_proper in months.items():
            date_str = re.sub(
                rf'\b{month_lower}\b',
                month_proper,
                date_str,
                flags=re.IGNORECASE
            )
        
        return date_str

    def _format_duration(self, duration: str) -> str:
        """Format duration: '9 Yearssss' -> '9 Years'"""
        if not isinstance(duration, str):
            return str(duration)
        
        # Remove repeated characters (Yearssss -> Years)
        # Match word with 3+ repeated final characters
        duration = re.sub(r'(\w)\1{2,}', r'\1', duration)
        
        # Capitalize time units properly
        time_units = {
            'year': 'Year', 'years': 'Years',
            'month': 'Month', 'months': 'Months',
            'day': 'Day', 'days': 'Days',
            'week': 'Week', 'weeks': 'Weeks'
        }
        
        for unit_lower, unit_proper in time_units.items():
            duration = re.sub(
                rf'\b{unit_lower}\b',
                unit_proper,
                duration,
                flags=re.IGNORECASE
            )
        
        return duration.strip()

    def _format_description(self, desc: str) -> str:
        """Format descriptions: 'idk bla bla bla' -> 'Idk bla bla bla'"""
        if not isinstance(desc, str):
            return str(desc)
        
        # Capitalize first letter of sentence
        desc = desc.strip()
        if desc:
            desc = desc[0].upper() + desc[1:]
        
        return desc

    def _format_title(self, title: str) -> str:
        """Format job titles/positions: 'software engineer' -> 'Software Engineer'"""
        if not isinstance(title, str):
            return str(title)
        
        # Title case
        return ' '.join(word.capitalize() for word in title.split())

    def _basic_cleanup(self, value: str) -> str:
        """Basic cleanup: remove extra spaces, fix obvious typos"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove extra whitespace
        value = ' '.join(value.split())
        
        # Remove repeated punctuation
        value = re.sub(r'([.,!?])\1+', r'\1', value)
        
        return value.strip()

    def _generate_contract_c5c6(self, contract_type: str, details: Dict, validation: Dict, session: Dict, special_clauses: List[str] = None) -> Dict:
        """ FIXED: Generate contract with contract_type in response"""
        try:
            contract_id = str(uuid.uuid4())[:8]
            
            if special_clauses is None:
                special_clauses = []
            
            #  FORMAT INPUTS BEFORE GENERATION
            formatted_details = self._format_contract_inputs(contract_type, details)
            
            logger.info(f"Original details: {details}")
            logger.info(f"Formatted details: {formatted_details}")
            logger.info(f"Special clauses: {special_clauses}")
            
            # Map to generator
            generators = {
                'EMPLOYMENT': 'contract_generator.employment',
                'PARTNERSHIP': 'contract_generator.partnership',
                'LEASE': 'contract_generator.lease',
                'BUY_SELL': 'contract_generator.buy_sell'
            }
            
            generator_module = generators.get(contract_type)
            if not generator_module:
                return {"response": f"Unknown contract type: {contract_type}", "success": False}
            
            import importlib
            gen_module = importlib.import_module(generator_module)
            generator = gen_module.ContractGenerator()
            
            #  Pass special clauses to generator
            content = generator.generate(formatted_details, special_clauses, [])
            
            # Save contract with BOTH original and formatted details
            self.contracts[contract_id] = {
                'id': contract_id,
                'type': contract_type,
                'content': content,
                'details': formatted_details,
                'original_details': details,
                'special_clauses': special_clauses,
                'validation': validation,
                'created_at': datetime.now().isoformat()
            }
            
            # Create DOCX
            try:
                from utils.docx_generator import DOCXGenerator
                docx = DOCXGenerator()
                file_path = docx.generate(contract_id, contract_type, content)
            except Exception as e:
                logger.error(f"DOCX error: {e}")
                file_path = None
            
            # Reset session
            session['awaiting_details'] = False
            session['awaiting_special_clauses'] = False
            session['asked_special_clauses'] = False
            session['contract_type'] = None
            session['details'] = {}
            session['filled'] = []
            session['missing'] = []
            session['special_clauses'] = []
            
            # Build response
            response = f" Your {contract_type.replace('_', ' ').title()} contract has been generated!\n\n"
            response += f" Contract ID: {contract_id}\n"
            
            if special_clauses:
                response += f"\n Included {len(special_clauses)} special clause(s)\n"
            
            if validation.get('applied_defaults'):
                response += "\n Applied defaults:\n" + "\n".join(f"  • {d}" for d in validation['applied_defaults'])
            
            if validation.get('warnings'):
                response += "\n️ Warnings:\n" + "\n".join(f"  • {w}" for w in validation['warnings'])
            
            response += "\n\n Click the download button!\n Need another contract? Just ask!"
            
            return {
                "response": response,
                "intent": "CREATE_CONTRACT",
                "contract_id": contract_id,
                "contract_type": contract_type,  #  FIX: Include contract_type in response
                "file_path": file_path,
                "success": True,
                "validation": validation
            }
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            import traceback
            traceback.print_exc()
            return {"response": f" Error: {str(e)}", "success": False}
        
    def _handle_greeting(self, session: Dict) -> Dict:
        """Handle greeting"""
        response = "Hello! I'm KontrataPH, your Philippine contract assistant. I can help you:\n\n• Generate law-compliant contracts\n• Analyze existing contracts\n• Answer questions about Philippine contract law\n\nWhat would you like to do?"
        
        session['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return {"response": response, "intent": "GREETING"}
    
    def _get_or_create_session(self, session_id: str) -> Dict:
        """Get or create session with special clauses support"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'messages': [],
                'awaiting_details': False,
                'awaiting_special_clauses': False,
                'asked_special_clauses': False,
                'contract_type': None,
                'details': {},
                'special_clauses': [],
                'filled': [],
                'missing': []
            }
        return self.sessions[session_id]
    
    # ========================================
    # ANALYSIS (A1-A6)
    # ========================================
    
    def analyze_contract_file(self, file) -> Dict[str, Any]:
        """Analyze uploaded contract file"""
        try:
            from utils.pdf_processor import PDFProcessor
            pdf = PDFProcessor()
            text = pdf.extract_text(file)
            return self.analyze_contract_text(text)
        except Exception as e:
            logger.error(f"File analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_contract_text(self, contract_text: str, contract_type: Optional[str] = None) -> Dict[str, Any]:
        """contract analysis with better segmentation and insights"""
        analysis_id = str(uuid.uuid4())[:8]
        
        # Detect contract type if not provided
        if not contract_type:
            contract_type = self._detect_contract_type(contract_text) or "Unknown"
        
        if not self._is_valid_contract(contract_text):
            return {
                "success": False,
                "error": "This doesn't appear to be a contract document. Please upload a valid contract (Employment, Partnership, Lease, or Buy & Sell agreement)."
            }
    
        # A1: Better segmentation
        sections = self._segment_contract(contract_text)
        
        # A2: Summarize each section
        summaries = {}
        key_points = []
        if self.llm_available and sections:
            for section_name, content in sections.items():
                if content and len(content) > 50:  # Only summarize substantial content
                    summary = self._summarize_section(section_name, content)
                    if summary:
                        summaries[section_name] = summary
                        key_points.append(f"**{section_name.title()}**: {summary}")
        
        # A3: Check compliance
        legal_compliance = self._check_compliance(sections, contract_type)
        
        # A4: Risk analysis
        risks = self._analyze_risks(sections, legal_compliance, contract_text)
        
        # A6: Generate user-friendly summary
        executive_summary = self._generate_user_friendly_summary(
            contract_type, key_points, legal_compliance, risks
        )
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "contract_type": contract_type,
            "sections": sections,
            "summaries": summaries,
            "legal_compliance": legal_compliance,
            "risks": risks,
            "summary": {
                "executive_summary": executive_summary,
                "key_points": key_points
            }
        }

    def _is_valid_contract(self, text: str) -> bool:
        """Check if text is actually a contract"""
        text_lower = text.lower()
        
        # Must have contract-related keywords
        contract_indicators = [
            'agreement', 'contract', 'party', 'parties',
            'whereas', 'terms and conditions', 'obligations',
            'undertakes', 'hereby', 'witnesseth'
        ]
        
        # Count how many indicators are present
        indicator_count = sum(1 for indicator in contract_indicators if indicator in text_lower)
        
        # Need at least 3 indicators to be a contract
        if indicator_count < 3:
            return False
        
        # Must have reasonable length (contracts are usually >500 chars)
        if len(text) < 500:
            return False
        
        return True
    
    def _segment_contract(self, text: str) -> Dict:
        """contract segmentation"""
        sections = {}
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Common section headers
        headers = {
            'parties': r'(?:parties|between|employer and employee)',
            'recitals': r'(?:whereas|recitals|background)',
            'scope': r'(?:scope|nature|description of work)',
            'term': r'(?:term|duration|period)',
            'compensation': r'(?:compensation|payment|salary|rent|price)',
            'obligations': r'(?:obligations|duties|responsibilities)',
            'termination': r'(?:termination|cancellation|end)',
            'confidentiality': r'(?:confidentiality|non-disclosure)',
            'warranties': r'(?:warranties|representations)',
            'dispute': r'(?:dispute|arbitration|governing law)'
        }
        
        current_section = None
        section_content = []
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Check if paragraph is a header
            matched_section = None
            for section_name, pattern in headers.items():
                if re.search(pattern, para_lower):
                    matched_section = section_name
                    break
            
            if matched_section:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = '\n\n'.join(section_content)
                
                # Start new section
                current_section = matched_section
                section_content = [para]
            elif current_section:
                section_content.append(para)
            else:
                # No section yet, might be preamble
                if 'preamble' not in sections:
                    sections['preamble'] = para
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n\n'.join(section_content)
        
        return sections
    
    def _summarize_section(self, section_name: str, content: str) -> str:
        """Summarize a contract section in user-friendly language"""
        
        system_prompt = """You are explaining a contract section to someone who is NOT a lawyer.

Use simple, clear language. Explain:
1. What this section means in plain English
2. Why it matters to the person
3. Any important numbers, dates, or obligations

Be concise (2-3 sentences max)."""

        prompt = f"""Section: {section_name}

Content: {content[:800]}

Explain this section simply:"""
        
        summary = self._call_llm(prompt, system_prompt, max_tokens=150)
        return summary.strip() if summary else None
    
    def _check_compliance(self, sections: Dict, contract_type: str) -> Dict:
        """compliance checking"""
        compliance = {
            "compliant": True,
            "violations": [],
            "recommendations": [],
            "score": 100
        }
        
        law_key = contract_type.lower()
        if law_key not in self.ph_laws:
            compliance["warnings"] = ["No specific law file for this contract type"]
            return compliance
        
        laws = self.ph_laws[law_key]
        
        # Check required clauses
        if 'required_clauses' in laws:
            for clause in laws['required_clauses']:
                if clause.get('mandatory', True):
                    clause_name = clause['name']
                    # Check if clause exists in any section
                    found = False
                    for section_content in sections.values():
                        if clause_name.replace('_', ' ') in section_content.lower():
                            found = True
                            break
                    
                    if not found:
                        violation = f"Missing required clause: {clause.get('description', clause_name)}"
                        compliance["violations"].append(violation)
                        compliance["score"] -= 10
                        compliance["compliant"] = False
        
        compliance["score"] = max(0, compliance["score"])
        return compliance
    
    def _analyze_risks(self, sections: Dict, compliance: Dict, full_text: str) -> Dict:
        """risk analysis"""
        risks = []
        
        # Add compliance violations as high risks
        for violation in compliance.get('violations', []):
            risks.append({
                "severity": "high",
                "category": "Legal Compliance",
                "description": violation,
                "recommendation": "Add the missing clause to ensure legal compliance"
            })
        
        # Check for unfair terms (if LLM available)
        if self.llm_available:
            unfair_terms = self._detect_unfair_terms(full_text)
            risks.extend(unfair_terms)
        
        # Calculate risk score
        risk_score = min(1.0, len(risks) * 0.15)
        
        return {
            "risk_score": risk_score,
            "risk_level": "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low",
            "risks": risks,
            "total_risks": len(risks)
        }
    
    def _detect_unfair_terms(self, text: str) -> List[Dict]:
        """Use LLM to detect potentially unfair terms"""
        system_prompt = """You are reviewing a contract for unfair or one-sided terms.

Look for:
- Unreasonable penalties
- One-sided termination clauses
- Excessive restrictions
- Unclear obligations

Return JSON array of concerns."""

        prompt = f"""Contract text: {text[:2000]}

Find any unfair terms. Return JSON array like:
[{{"severity": "medium", "category": "Unfair Term", "description": "...", "recommendation": "..."}}]

Only include real concerns. If none, return []:"""
        
        response = self._call_llm(prompt, system_prompt, max_tokens=400)
        
        if response:
            try:
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    risks = json.loads(json_match.group())
                    return risks
            except:
                pass
        
        return []
    
    def _generate_user_friendly_summary(self, contract_type: str, key_points: List[str], 
                                       compliance: Dict, risks: Dict) -> str:
        """Generate a summary that non-experts can understand"""
        
        summary = f"## {contract_type.replace('_', ' ').title()} Contract Analysis\n\n"
        
        # Overall assessment
        if risks['risk_level'] == "Low" and compliance['compliant']:
            summary += " **Overall: This contract looks good!**\n\n"
        elif risks['risk_level'] == "Medium":
            summary += "️ **Overall: Some concerns found**\n\n"
        else:
            summary += " **Overall: Significant issues detected**\n\n"
        
        # Key points
        if key_points:
            summary += "### What This Contract Says:\n\n"
            for point in key_points[:5]:  # Limit to top 5
                summary += f"{point}\n\n"
        
        # Compliance
        summary += f"### Legal Compliance: {compliance['score']}%\n\n"
        if compliance['violations']:
            summary += "**Missing required clauses:**\n"
            for v in compliance['violations'][:3]:
                summary += f"- {v}\n"
            summary += "\n"
        
        # Risks
        if risks['risks']:
            summary += f"### Risks Found: {len(risks['risks'])} ({risks['risk_level']} Risk)\n\n"
            for risk in risks['risks'][:3]:
                summary += f"**[{risk['severity'].upper()}]** {risk['description']}\n"
                summary += f"→ *{risk['recommendation']}*\n\n"
        else:
            summary += "###  No significant risks detected\n\n"
        
        # Recommendation
        if not compliance['compliant'] or risks['risk_level'] != "Low":
            summary += "###  Recommendation\n\n"
            summary += "Consider having a lawyer review this contract before signing, especially the issues highlighted above.\n"
        
        return summary
    
    # Other required methods
    def generate_contract(self, contract_type: str, details: Dict, 
                         special_clauses: List[str], session_id: str = 'default') -> Dict[str, Any]:
        """API endpoint for direct generation"""
        session = self._get_or_create_session(session_id)
        session['contract_type'] = contract_type
        validation = self._validate_against_law_c4(contract_type, details)
        return self._generate_contract_c5c6(contract_type, details, validation, session, special_clauses)
    
    def get_contract_file(self, contract_id: str) -> Optional[str]:
        """Get file path"""
        from utils.docx_generator import DOCXGenerator
        docx = DOCXGenerator()
        return docx.get_file_path(contract_id)