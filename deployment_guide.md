# AI Legal Document Analyzer - Deployment Guide

## 🚨 SQLite Compatibility Issue

The error you encountered is due to ChromaDB requiring SQLite version 3.35.0 or higher, but your deployment environment has an older version.

## 🔧 Solutions

### **Solution 1: Use the Fallback Version (Recommended)**

The `legal_team_fallback.py` file removes the ChromaDB dependency and should work in environments with older SQLite versions.

**To deploy:**
```bash
streamlit run legal_team_fallback.py
```

### **Solution 2: Update SQLite (Advanced)**

If you need the full ChromaDB functionality, you can try updating SQLite:

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install sqlite3
```

**For CentOS/RHEL:**
```bash
sudo yum install sqlite
```

**Check SQLite version:**
```bash
sqlite3 --version
```

### **Solution 3: Use Alternative Vector Database**

If ChromaDB continues to cause issues, you can modify the code to use alternatives:

```python
# Replace ChromaDB with FAISS
from agno.vectordb.faiss import FaissDb

st.session_state.vector_database = FaissDb(
    collection="legal_docs",
    embedder=OpenAIEmbedder()
)
```

## 📋 Requirements

### **Minimum Requirements:**
- Python 3.8+
- SQLite 3.35.0+ (for ChromaDB)
- OpenAI API key

### **Recommended Requirements:**
- Python 3.9+
- SQLite 3.37.0+
- 4GB+ RAM
- OpenAI API key

## 🚀 Deployment Options

### **1. Streamlit Cloud (Recommended)**
- Free hosting
- Automatic deployments from GitHub
- Handles most dependencies automatically

### **2. Heroku**
- Add `runtime.txt` with Python version
- Use `Procfile` for Streamlit
- May need buildpacks for SQLite

### **3. Docker**
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y sqlite3
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "legal_team.py", "--server.port=8501"]
```

### **4. Local Development**
```bash
pip install -r requirements.txt
streamlit run legal_team.py
```

## 🔑 Environment Variables

Set these in your deployment environment:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 📁 File Structure

```
legal-reviewer/
├── legal_team.py              # Main application (with ChromaDB)
├── legal_team_fallback.py     # Fallback version (without ChromaDB)
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── deployment_guide.md        # This file
└── README.md                  # Project documentation
```

## 🐛 Troubleshooting

### **Common Issues:**

1. **SQLite Version Error:**
   - Use `legal_team_fallback.py`
   - Or update SQLite to 3.35.0+

2. **OpenAI API Errors:**
   - Check API key is set correctly
   - Verify API key has sufficient credits
   - Check rate limits

3. **Memory Issues:**
   - Reduce chunk size in the UI
   - Use smaller documents
   - Increase deployment memory allocation

4. **Import Errors:**
   - Ensure all requirements are installed
   - Check Python version compatibility
   - Verify agno library version

## 📞 Support

If you continue to experience issues:

1. Check the Streamlit logs for detailed error messages
2. Verify your deployment environment meets minimum requirements
3. Consider using the fallback version for immediate deployment
4. Update your deployment environment's SQLite version

## 🎯 Quick Start

**For immediate deployment with minimal issues:**
```bash
streamlit run legal_team_fallback.py
```

This version provides the same functionality without the SQLite dependency issues.
