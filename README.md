# Prerequisites
- Python 3.8+

# Backend Setup

A. Create Virtual Environment
**python -m venv venv**
**venv\Scripts\activate**

B. Install Python Dependencies
**cd backend**
**pip install -r requirements.txt**

C. Install spaCy Language Model (Optional)
**python -m spacy download en_core_web_sm**

D. Install Ollama (Optional)
Download from: https://ollama.com/download
Install the application

- Open terminal and run:
**ollama pull llama3.2**

- Verify Ollama is running:
**bashollama list**

Should show llama3.2

# Run Backend Server
Make sure you're in /backend directory with venv activated

- Run:
**cd backend**
**python app.py**

# Frontend Setup

- Run:
**npm install -g serve**
- Then: 
**cd frontend**
- Lastly:
**serve .**

- live server is an option but it refreshes every time so base on my exp kapag nag generate na ng contract nag r-refresh siya, so, nawawala yung current convo