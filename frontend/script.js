//script.js - FIXED VERSION

const API_URL = 'http://localhost:5000/api';
let currentContractId = null;
let currentFile = null;
let sessionId = 'web-session-' + Date.now();
let contractHistory = [];

console.log(' KontrataPH initialized');
console.log(' Session ID:', sessionId);

// Load history from localStorage
loadHistory();

// ============================================
// Message Handling
// ============================================

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message && !currentFile) return;
    
    // Add user message
    if (message) {
        addMessage('user', message);
        input.value = '';
        autoResizeTextarea(input);
    }
    
    setSendButtonState(false);
    const loadingId = addLoadingMessage();

    handleChatMessage(message, loadingId);
}

async function handleChatMessage(message, loadingId) {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        console.log(' Response:', data);
        
        removeLoadingMessage(loadingId);
        addMessage('assistant', data.response || 'No response');
        
        //  FIX: Handle contract generation with contract_type
        if (data.contract_id) {
            currentContractId = data.contract_id;
            
            // Ensure we have contract_type in the data
            if (!data.contract_type && data.validation) {
                data.contract_type = data.validation.contract_type;
            }
            
            console.log(' Contract generated:', data.contract_id, 'Type:', data.contract_type);
            
            displayContractGenerated(data);
            addToHistory('generated', data);
            openSidebar('preview');
        }
        // Handle contract analysis
        else if (data.analysis || data.summary || data.legal_compliance) {
            displayContractAnalysis(data);
            addToHistory('analyzed', data);
            openSidebar('preview');
        }
        
    } catch (error) {
        console.error(' Error:', error);
        removeLoadingMessage(loadingId);
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        setSendButtonState(true);
    }
}

async function handleFileUpload(file, loadingId) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_URL}/analyze-contract`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        removeLoadingMessage(loadingId);
        
        if (response.ok && data.success) {
            addMessage('assistant', ' Analysis complete! Check the preview panel →');
            displayContractAnalysis(data);
            addToHistory('analyzed', data);
            openSidebar('preview');
        } else {
            const errorMsg = data.error || 'Failed to analyze';
            addMessage('assistant', ` ${errorMsg}`);
        }
        
        clearFile();
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessage('assistant', `Error: ${error.message}`);
        clearFile();
    } finally {
        setSendButtonState(true);
    }
}

// ============================================
// UI Functions
// ============================================

function addMessage(role, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = `message ${role}`;
    
    const avatarSrc = role === 'user' ? 'images/user-avatar.jpg' : 'images/bot-avatar.jpg';
    
    messageDiv.innerHTML = `
        <div class="message-avatar"><img src="${avatarSrc}" alt="${role}"></div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addLoadingMessage() {
    const messagesDiv = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message assistant loading';
    loadingDiv.innerHTML = `
        <div class="message-avatar"><img src="images/bot-avatar.jpg" alt="Bot"></div>
        <div class="message-content">Thinking...</div>
    `;
    
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) loadingDiv.remove();
}

function setSendButtonState(enabled) {
    document.getElementById('sendBtn').disabled = !enabled;
}

// ============================================
// Textarea Auto-resize
// ============================================

const messageInput = document.getElementById('messageInput');
messageInput.addEventListener('input', function() {
    autoResizeTextarea(this);
});

messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// ============================================
// File Handling
// ============================================

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ];
    
    if (!validTypes.includes(file.type)) {
        alert('Please upload PDF, DOCX, or TXT file');
        event.target.value = '';
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File must be less than 10MB');
        event.target.value = '';
        return;
    }
    
    currentFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileIndicator').style.display = 'flex';
    
    addMessage('user', ` Uploaded: ${file.name}`);
    setSendButtonState(false);
    const loadingId = addLoadingMessage();
    handleFileUpload(file, loadingId);
}

function clearFile() {
    currentFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileIndicator').style.display = 'none';
}

// ============================================
// Sidebar Controls
// ============================================

function toggleSidebar(tab) {
    const sidebar = document.getElementById('sidebar');
    const isOpen = sidebar.classList.contains('open');
    
    if (isOpen) {
        const currentTab = document.querySelector('.sidebar-tab.active').textContent.trim().toLowerCase();
        if (currentTab === tab) {
            closeSidebar();
        } else {
            switchTab(tab);
        }
    } else {
        openSidebar(tab);
    }
}

function openSidebar(tab) {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.add('open');
    switchTab(tab);
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('open');
}

function switchTab(tab) {
    // Update tabs
    document.getElementById('previewTab').classList.remove('active');
    document.getElementById('historyTab').classList.remove('active');
    
    // Update content
    document.getElementById('previewContent').style.display = 'none';
    document.getElementById('historyContent').style.display = 'none';
    
    if (tab === 'preview') {
        document.getElementById('previewTab').classList.add('active');
        document.getElementById('previewContent').style.display = 'block';
        document.getElementById('sidebarTitle').textContent = 'Contract Preview';
    } else {
        document.getElementById('historyTab').classList.add('active');
        document.getElementById('historyContent').style.display = 'block';
        document.getElementById('sidebarTitle').textContent = 'History';
        renderHistory();
    }
}

// ============================================
// Contract Display - GENERATED
// ============================================

async function displayContractGenerated(data) {
    const previewDiv = document.getElementById('previewContent');
    
    //  FIX: Get contract type from multiple possible sources
    const contractType = data.contract_type || 
                        data.validation?.contract_type || 
                        (data.validation && data.validation.applied_defaults ? 'Contract': 'Unknown');
    
    console.log('Display contract type:', contractType);
    
    // Show loading state first
    previewDiv.innerHTML = `
        <div class="contract-header">
            <div class="contract-type"> ${contractType.replace(/_/g, ' ')} Contract</div>
            <div class="contract-id">Contract ID: ${data.contract_id}</div>
            <button class="download-btn" onclick="downloadContract('${data.contract_id}')">
                Download DOCX
            </button>
        </div>
        <div class="contract-section">
            <div class="section-content" style="text-align: center; padding: 40px;">
                <div style="font-size: 24px; margin-bottom: 12px;"></div>
                <div>Loading contract content...</div>
            </div>
        </div>
    `;
    
    // Fetch the full contract content
    try {
        const response = await fetch(`${API_URL}/get-contract-content/${data.contract_id}`);
        if (!response.ok) throw new Error('Failed to fetch contract content');
        
        const contentData = await response.json();
        
        let html = `
            <div class="contract-header">
                <div class="contract-type"> ${contractType.replace(/_/g, ' ')} Contract</div>
                <div class="contract-id">Contract ID: ${data.contract_id}</div>
                <button class="download-btn" onclick="downloadContract('${data.contract_id}')">
                    ️ Download DOCX
                </button>
            </div>
        `;
        
        // Display the full contract content
        if (contentData.content) {
            html += `
                <div class="contract-section contract-document">
                    <div class="section-title"> Contract Document</div>
                    <div class="contract-content">${formatContractContent(contentData.content)}</div>
                </div>
            `;
        }
        
        // Validation info (collapsed by default)
        if (data.validation) {
            let validationHtml = '<div class="contract-section collapsible">';
            validationHtml += '<div class="section-title" onclick="toggleSection(this)">✓ Validation Info <span class="toggle-icon">▼</span></div>';
            validationHtml += '<div class="section-content" style="display: none;">';
            validationHtml += ' Contract validated successfully\n\n';
            
            if (data.validation.applied_defaults && data.validation.applied_defaults.length > 0) {
                validationHtml += ' Applied Defaults:\n';
                data.validation.applied_defaults.forEach(d => {
                    validationHtml += `  • ${d}\n`;
                });
            }
            
            if (data.validation.warnings && data.validation.warnings.length > 0) {
                validationHtml += '\n️ Warnings:\n';
                data.validation.warnings.forEach(w => {
                    validationHtml += `  • ${w}\n`;
                });
            }
            
            validationHtml += '</div></div>';
            html += validationHtml;
        }
        
        // Summary (collapsed by default)
        if (data.summary && data.summary.executive_summary) {
            html += `
                <div class="contract-section collapsible">
                    <div class="section-title" onclick="toggleSection(this)"> Executive Summary <span class="toggle-icon">▼</span></div>
                    <div class="section-content" style="display: none;">${escapeHtml(data.summary.executive_summary)}</div>
                </div>
            `;
        }
        
        previewDiv.innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load contract content:', error);
        // Fallback to original display without content
        let html = `
            <div class="contract-header">
                <div class="contract-type"> ${contractType.replace(/_/g, ' ')} Contract</div>
                <div class="contract-id">Contract ID: ${data.contract_id}</div>
                <button class="download-btn" onclick="downloadContract('${data.contract_id}')">
                    ️ Download DOCX
                </button>
            </div>
            <div class="contract-section">
                <div class="section-content" style="color: #f44336;">
                    ️ Could not load contract content preview. You can still download the document.
                </div>
            </div>
        `;
        previewDiv.innerHTML = html;
    }
}

// ============================================
// Contract Display - ANALYSIS
// ============================================

function displayContractAnalysis(data) {
    const previewDiv = document.getElementById('previewContent');
    
    const contractType = data.contract_type || 'Unknown';
    
    let html = `
        <div class="contract-header">
            <div class="contract-type"> ${contractType.replace(/_/g, ' ')} Analysis</div>
            <div class="contract-id">Analysis ID: ${data.analysis_id || 'N/A'}</div>
        </div>
    `;
    
    // Executive Summary
    if (data.summary && data.summary.executive_summary) {
        html += `
            <div class="contract-section">
                <div class="section-title"> Executive Summary</div>
                <div class="section-content">${formatMarkdown(data.summary.executive_summary)}</div>
            </div>
        `;
    }
    
    // Risk Assessment
    if (data.risks) {
        let riskHtml = '<div class="contract-section">';
        riskHtml += '<div class="section-title">️ Risk Assessment</div>';
        riskHtml += '<div class="section-content">';
        
        const riskLevel = data.risks.risk_level || 'Unknown';
        const riskClass = riskLevel.toLowerCase();
        riskHtml += `<span class="risk-badge risk-${riskClass}">${riskLevel.toUpperCase()} RISK</span>\n\n`;
        
        riskHtml += `Risk Score: ${(data.risks.risk_score * 100).toFixed(0)}%\n\n`;
        
        if (data.risks.risks && data.risks.risks.length > 0) {
            riskHtml += 'Issues Found:\n';
            data.risks.risks.forEach(risk => {
                riskHtml += `\n[${risk.severity.toUpperCase()}] ${risk.description}\n`;
                if (risk.recommendation) {
                    riskHtml += ` ${risk.recommendation}\n`;
                }
            });
        } else {
            riskHtml += ' No significant risks detected';
        }
        
        riskHtml += '</div></div>';
        html += riskHtml;
    }
    
    // Legal Compliance
    if (data.legal_compliance) {
        const comp = data.legal_compliance;
        let compHtml = '<div class="contract-section">';
        compHtml += '<div class="section-title">️ Legal Compliance</div>';
        compHtml += '<div class="section-content">';
        
        compHtml += comp.compliant ? ' Compliant\n\n' : '️ Issues Detected\n\n';
        
        if (comp.score !== undefined) {
            compHtml += `Compliance Score: ${comp.score}%\n\n`;
        }
        
        if (comp.violations && comp.violations.length > 0) {
            compHtml += 'Violations:\n';
            comp.violations.forEach(v => {
                compHtml += `  ✗ ${v}\n`;
            });
        }
        
        if (comp.recommendations && comp.recommendations.length > 0) {
            compHtml += '\nRecommendations:\n';
            comp.recommendations.forEach(r => {
                compHtml += `  → ${r}\n`;
            });
        }
        
        compHtml += '</div></div>';
        html += compHtml;
    }
    
    // Key Points
    if (data.summary && data.summary.key_points && data.summary.key_points.length > 0) {
        html += '<div class="contract-section">';
        html += '<div class="section-title"> Key Points</div>';
        html += '<div class="section-content">';
        data.summary.key_points.forEach(point => {
            html += formatMarkdown(point) + '\n\n';
        });
        html += '</div></div>';
    }
    
    previewDiv.innerHTML = html;
}

// ============================================
// Download Contract
// ============================================

async function downloadContract(contractId) {
    if (!contractId) {
        alert('No contract to download');
        return;
    }
    
    try {
        console.log('️ Downloading:', contractId);
        
        const response = await fetch(`${API_URL}/download-contract/${contractId}`);
        
        if (!response.ok) throw new Error('Download failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `contract_${contractId}.docx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        console.log(' Downloaded!');
        addMessage('assistant', ` Contract downloaded: contract_${contractId}.docx`);
    } catch (error) {
        console.error(' Download error:', error);
        alert('Error: ' + error.message);
    }
}

// ============================================
// History Management - FIXED
// ============================================

function addToHistory(type, data) {
    //  FIX: Ensure contract_type is properly captured
    const contractType = data.contract_type || 
                        data.validation?.contract_type ||
                        (type === 'generated' ? 'contract' : 'Unknown');
    
    const historyItem = {
        id: data.contract_id || data.analysis_id || Date.now().toString(),
        type: type, // 'generated' or 'analyzed'
        contractType: contractType,  //  Use the extracted contract type
        timestamp: new Date().toISOString(),
        data: data
    };
    
    console.log('Adding to history:', historyItem);
    
    contractHistory.unshift(historyItem);
    
    // Keep only last 20 items
    if (contractHistory.length > 20) {
        contractHistory = contractHistory.slice(0, 20);
    }
    
    saveHistory();
}

function saveHistory() {
    try {
        localStorage.setItem('kontrata_history', JSON.stringify(contractHistory));
    } catch (e) {
        console.error('Failed to save history:', e);
    }
}

function loadHistory() {
    try {
        const saved = localStorage.getItem('kontrata_history');
        if (saved) {
            contractHistory = JSON.parse(saved);
            console.log('Loaded history:', contractHistory.length, 'items');
        }
    } catch (e) {
        console.error('Failed to load history:', e);
        contractHistory = [];
    }
}

function renderHistory() {
    const historyDiv = document.getElementById('historyContent');
    
    if (contractHistory.length === 0) {
        historyDiv.innerHTML = `
            <div class="empty-history">
                <div style="font-size: 48px; margin-bottom: 12px;"></div>
                <div>No history yet</div>
                <div style="font-size: 12px; margin-top: 8px;">Your contracts will appear here</div>
            </div>
        `;
        return;
    }
    
    let html = '<div class="history-list">';
    
    contractHistory.forEach(item => {
        const date = new Date(item.timestamp);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        const icon = item.type === 'generated' ? '' : '';
        const typeLabel = item.type === 'generated' ? 'Generated' : 'Analyzed';
        
        //  FIX: Display contract type properly
        const contractTypeDisplay = item.contractType ? 
            item.contractType.replace(/_/g, ' ') : 
            'Unknown';
        
        html += `
            <div class="history-item" onclick='loadHistoryItem(${JSON.stringify(item).replace(/'/g, "&#39;")})'>
                <div class="history-item-header">
                    <div class="history-item-type">${icon} ${typeLabel}</div>
                    <div class="history-item-date">${dateStr}</div>
                </div>
                <div class="history-item-id">${contractTypeDisplay}</div>
                <div class="history-item-preview">ID: ${item.id}</div>
            </div>
        `;
    });
    
    html += '</div>';
    
    historyDiv.innerHTML = html;
}

function loadHistoryItem(item) {
    console.log('Loading history item:', item);
    
    if (item.type === 'generated') {
        displayContractGenerated(item.data);
        currentContractId = item.id;
    } else {
        displayContractAnalysis(item.data);
    }
    switchTab('preview');
}

function clearHistory() {
    if (confirm('Clear all history?')) {
        contractHistory = [];
        saveHistory();
        renderHistory();
    }
}

// ============================================
// Utilities
// ============================================

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMarkdown(text) {
    if (typeof text !== 'string') return '';
    
    return text
        .replace(/### (.*)/g, '<strong style="font-size: 16px; display: block; margin: 12px 0 8px;">$1</strong>')
        .replace(/## (.*)/g, '<strong style="font-size: 18px; display: block; margin: 16px 0 10px;">$1</strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '<br><br>');
}

function formatContractContent(content) {
    if (typeof content !== 'string') return '';
    
    // Format the contract content to look like a document
    return content
        // Headers (all caps lines or lines ending with colon)
        .replace(/^([A-Z][A-Z\s]+):?$/gm, '<div class="contract-header-text">$1</div>')
        // Section numbers (1., 2., etc)
        .replace(/^(\d+\.\s+[A-Z].*?)$/gm, '<div class="contract-section-header">$1</div>')
        // Sub-sections (a., b., i., ii., etc)
        .replace(/^(\s+)([a-z]\.|\([a-z]\)|[ivx]+\.)\s+/gm, '$1<span class="contract-subsection">$2</span> ')
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic text
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Preserve line breaks
        .replace(/\n/g, '<br>')
        // Add spacing between major sections
        .replace(/(<\/div><br><div class="contract-header-text">)/g, '</div><br><br><div class="contract-header-text">');
}

function toggleSection(element) {
    const content = element.nextElementSibling;
    const icon = element.querySelector('.toggle-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▲';
    } else {
        content.style.display = 'none';
        icon.textContent = '▼';
    }
}

// ============================================
// Global Exports
// ============================================

window.sendMessage = sendMessage;
window.handleFileSelect = handleFileSelect;
window.clearFile = clearFile;
window.downloadContract = downloadContract;
window.toggleSidebar = toggleSidebar;
window.openSidebar = openSidebar;
window.closeSidebar = closeSidebar;
window.switchTab = switchTab;
window.loadHistoryItem = loadHistoryItem;
window.clearHistory = clearHistory;
window.toggleSection = toggleSection;

console.log(' KontrataPH loaded successfully');