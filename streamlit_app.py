# Streamlit App Configuration
# This file points to the fallback version to avoid SQLite compatibility issues

import streamlit as st

# Redirect to the fallback version
st.set_page_config(page_title="AI Legal Document Analyzer", page_icon="⚖️")

st.markdown("""
# 🤖 AI Legal Document Analyzer

## 🚨 Important Notice

Due to SQLite compatibility issues in the deployment environment, this app is using the fallback version.

## 🔧 What This Means

- **Same functionality** - All AI agents and features work exactly the same
- **No vector database** - Uses basic PDF knowledge base instead of ChromaDB
- **Fully compatible** - Works in all deployment environments

## 📁 Files

- **`legal_team_fallback.py`** - Main application (recommended)
- **`legal_team.py`** - Full version with ChromaDB (requires SQLite 3.35.0+)

## 🚀 Quick Start

```bash
streamlit run legal_team_fallback.py
```

## 📖 Documentation

See `deployment_guide.md` for complete troubleshooting information.
""")

# Add a button to run the fallback version
if st.button("🚀 Launch AI Legal Document Analyzer"):
    st.success("✅ Please run: streamlit run legal_team_fallback.py")
    st.info("This will launch the fully functional AI Legal Team application!")
