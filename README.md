# Scam Website Detection System

A Streamlit-based application that analyzes URLs to detect potential phishing websites using machine learning.

## Files

- `app.py`: Main Streamlit application interface
- `url_features.py`: URL feature extraction and analysis
- `ml_model.py`: Machine learning model for phishing detection
- `.streamlit/config.toml`: Streamlit server configuration

## Setup

1. Install required packages:
```bash
pip install streamlit pandas numpy scikit-learn validators tld
```

2. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Features

- URL analysis and feature extraction
- Machine learning-based phishing detection
- Detailed security analysis and explanations
- Historical analysis tracking
- Interactive visualization of results
