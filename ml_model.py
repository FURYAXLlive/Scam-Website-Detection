from sklearn.ensemble import RandomForestClassifier
import numpy as np

def create_model():
    """Create and return a pre-trained model for phishing detection."""
    # Initialize model with fixed parameters for reproducibility
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    # Create synthetic training data
    num_samples = 1000
    num_features = 20  # Updated to match new feature count

    # Generate synthetic features
    X = np.random.rand(num_samples, num_features)

    # Create synthetic labels with specific rules to match JavaScript scoring
    y = np.zeros(num_samples)

    # Define feature importance weights (matching utils.js)
    weights = {
        14: 0.25,  # has_ip_address
        16: 0.20,  # has_suspicious_words
        2: 0.18,   # domain_in_path
        15: 0.15,  # has_https
        0: 0.12,   # url_length
        4: 0.10,   # num_dots
        6: 0.10,   # num_at
        19: 0.08,  # has_double_slash
        1: 0.08,   # hostname_length
        18: 0.08,  # path_length
        5: 0.06,   # num_hyphens
        13: 0.06,  # num_slash
        9: 0.05,   # num_equal
        8: 0.05,   # num_and
        10: 0.02,  # num_underscore
        11: 0.02   # num_tilde
    }

    # Updated threshold adjustments
    score_multiplier = 1.0  # Ensures consistent scoring between Python and JS

    # Label data using the same rules as JavaScript, but with adjusted thresholds
    for i in range(num_samples):
        score = 0
        # Calculate score using feature weights
        for feat_idx, weight in weights.items():
            if feat_idx == 15:  # has_https
                if X[i, feat_idx] < 0.5:  # No HTTPS
                    score += weight
            elif feat_idx == 0:  # url_length
                if X[i, feat_idx] > 0.8:  # Long URL
                    score += weight
            elif feat_idx == 1:  # hostname_length
                if X[i, feat_idx] > 0.7:  # Long hostname
                    score += weight
            else:
                if X[i, feat_idx] > 0.7:  # Feature present
                    score += weight

        # Use adjusted thresholds based on JavaScript getRiskLevel function
        y[i] = 0 if score < 0.4 else (1 if score < 0.7 else 2) # Low, Medium, High mapped to 0,1,2

    # Train the model
    model.fit(X, y)
    return model

def get_risk_level(score):
    if score == 0:
        return "Low"
    elif score == 1:
        return "Medium"
    elif score == 2:
        return "High"
    else:
        return "Unknown" # Handle unexpected scores

# Example usage
model = create_model()
# Simulate a prediction.  Replace with actual feature vector from URL analysis.
prediction = model.predict([np.random.rand(20)])[0]
risk_level = get_risk_level(prediction)
print(f"Predicted risk level: {risk_level}")