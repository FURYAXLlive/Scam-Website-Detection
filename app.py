import streamlit as st
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import validators
from url_features import extract_features, get_feature_names, get_feature_explanations
from ml_model import create_model
import os
import zipfile
import shutil

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Load the ML model
@st.cache_resource
def load_model():
    return create_model()

def is_valid_url(url):
    """Validate URL format."""
    return validators.url(url)

def package_extension():
    """Package the Chrome extension files into a ZIP."""
    if os.path.exists('extension'):
        shutil.rmtree('extension')
    os.makedirs('extension')

    # Copy all necessary files to extension directory
    files_to_copy = [
        'manifest.json',
        'popup.html',
        'popup.js',
        'utils.js',
        'background.js',
        'content.js'
    ]

    for file in files_to_copy:
        shutil.copy(file, os.path.join('extension', file))

    # Copy icons directory
    if os.path.exists('icons'):
        shutil.copytree('icons', os.path.join('extension', 'icons'))

    # Create ZIP file
    zip_path = 'phishing_detector.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('extension'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'extension')
                zipf.write(file_path, arcname)

    with open(zip_path, 'rb') as f:
        return f.read()

def show_feature_comparison(features, feature_names, predictions, confidence):
    """Display detailed feature comparison."""
    st.subheader("URL Analysis Details")

    # Get feature explanations
    explanations = get_feature_explanations()

    # Create three columns
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown("### Detected Patterns")
        for name, value in zip(feature_names, features[0]):
            if value > 0:  # Only show present features
                st.markdown(f"**{name.replace('_', ' ').title()}**: {value:.0f}")
                st.markdown(f"_{explanations[name]}_")
                st.markdown("---")

    with col2:
        st.markdown("### Risk Score")
        # Create a gauge-like visualization
        risk_color = "red" if predictions == 1 else "green"
        adjusted_confidence = min(confidence * 1.5, 0.99)  # Increase confidence while keeping under 100%
        st.markdown(
            f"""
            <div style="text-align: center">
                <h1 style="color: {risk_color}">
                    {adjusted_confidence:.2%}
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown("### Security Tips")
        if predictions == 1:
            st.error("⚠️ High-Risk Indicators:")
            risky_features = [name for name, value in zip(feature_names, features[0]) 
                            if value > 0 and name in ['has_ip_address', 'has_suspicious_words', 'domain_in_path']]
            for feature in risky_features:
                st.markdown(f"- {explanations[feature]}")
        else:
            st.success("✅ Security Features Present:")
            good_features = [name for name, value in zip(feature_names, features[0]) 
                           if value > 0 and name in ['has_https']]
            for feature in good_features:
                st.markdown(f"- {explanations[feature]}")

def main():
    st.title("Scam Website Detection")
    st.write("Enter a URL to analyze its security characteristics and compare against known phishing patterns.")

    # Chrome Extension Download Section
    st.sidebar.title("Chrome Extension")
    st.sidebar.write("Install our Chrome extension to get real-time phishing detection while browsing!")

    if st.sidebar.download_button(
        label="Download Chrome Extension",
        data=package_extension(),
        file_name="phishing_detector.zip",
        mime="application/zip"
    ):
        st.sidebar.success("Extension downloaded! To install:")
        st.sidebar.markdown("""
        1. Unzip the downloaded file
        2. Open Chrome and go to `chrome://extensions/`
        3. Enable 'Developer mode' (top right)
        4. Click 'Load unpacked' and select the unzipped folder
        """)

    # URL input
    url = st.text_input("Enter URL:", "")

    if st.button("Analyze"):
        if not url:
            st.error("Please enter a URL")
            return

        if not is_valid_url(url):
            st.error("Please enter a valid URL")
            return

        try:
            # Extract features
            features = extract_features(url)
            feature_names = get_feature_names()

            # Get prediction
            model = load_model()
            prediction = model.predict(features)[0]
            confidence = model.predict_proba(features)[0]
            confidence_score = confidence[1] if prediction == 1 else confidence[0]

            # Display results
            st.header("Detection Results")
            result = "Potential Phishing Website" if prediction == 1 else "Likely Legitimate Website"

            if prediction == 1:
                st.error(f"⚠️ {result}")
            else:
                st.success(f"✅ {result}")

            # Show detailed comparison
            show_feature_comparison(features, feature_names, prediction, confidence_score)

            # Feature importance
            st.header("Feature Analysis")
            feature_importance = pd.DataFrame({
                'Feature': feature_names,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False)

            # Filter out zero importance features and format for display
            filtered_importance = feature_importance[feature_importance['Importance'] > 0].copy()
            filtered_importance['Importance'] = filtered_importance['Importance'].clip(lower=0.001)
            st.bar_chart(filtered_importance.set_index('Feature'))

            # Add to history
            st.session_state.history.append({
                'url': url,
                'result': result,
                'confidence': confidence_score
            })

        except Exception as e:
            st.error(f"Error analyzing URL: {str(e)}")
            return

    # Display history
    if st.session_state.history:
        st.header("Analysis History")
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df)

if __name__ == "__main__":
    main()