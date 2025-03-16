from urllib.parse import urlparse
import re
import numpy as np
import tld

def extract_features(url):
    """Extract features from URL for phishing detection."""
    try:
        features = {}
        parsed = urlparse(url)

        # Length based features
        features['url_length'] = len(url)
        features['hostname_length'] = len(parsed.netloc)

        # Domain specific features
        domain = parsed.netloc
        features['domain_in_path'] = 1 if domain.lower() in parsed.path.lower() else 0
        features['domain_age_days'] = 0  # Placeholder - would need domain age API

        # Special character features
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_at'] = url.count('@')
        features['num_question_marks'] = url.count('?')
        features['num_and'] = url.count('&')
        features['num_equal'] = url.count('=')
        features['num_underscore'] = url.count('_')
        features['num_tilde'] = url.count('~')
        features['num_percent'] = url.count('%')
        features['num_slash'] = url.count('/')

        # Security indicators
        features['has_ip_address'] = 1 if bool(re.match(
            r'^(http|https)://(\d{1,3}\.){3}\d{1,3}', url)) else 0
        features['has_https'] = 1 if parsed.scheme == 'https' else 0
        features['has_suspicious_words'] = 1 if any(word in url.lower() 
            for word in ['secure', 'login', 'signin', 'bank', 'account', 'update', 'verify']) else 0

        # Path analysis
        features['dir_count'] = len([x for x in parsed.path.split('/') if x])
        features['path_length'] = len(parsed.path)
        features['has_double_slash'] = 1 if '//' in parsed.path else 0

        return np.array(list(features.values())).reshape(1, -1)

    except Exception as e:
        raise ValueError(f"Error extracting features: {str(e)}")

def get_feature_names():
    """Return list of feature names in order."""
    return [
        'url_length', 'hostname_length', 'domain_in_path', 'domain_age_days',
        'num_dots', 'num_hyphens', 'num_at', 'num_question_marks',
        'num_and', 'num_equal', 'num_underscore', 'num_tilde',
        'num_percent', 'num_slash', 'has_ip_address', 'has_https',
        'has_suspicious_words', 'dir_count', 'path_length', 'has_double_slash'
    ]

def get_feature_explanations():
    """Return explanations for each feature."""
    return {
        'url_length': 'Unusually long URLs may indicate hidden malicious content',
        'hostname_length': 'Extremely long hostnames are often suspicious',
        'domain_in_path': 'Domain name repeated in URL path may indicate deception',
        'domain_age_days': 'Newly registered domains are more likely to be malicious',
        'num_dots': 'Excessive dots may indicate subdomain abuse',
        'num_hyphens': 'Multiple hyphens are common in phishing URLs',
        'num_at': 'The @ symbol in URLs can be used to obscure the actual destination',
        'num_question_marks': 'Multiple query parameters may hide malicious code',
        'num_and': 'Numerous parameters might indicate suspicious data collection',
        'num_equal': 'Many parameters could suggest data harvesting',
        'num_underscore': 'Uncommon in legitimate URLs',
        'num_tilde': 'Rarely used in legitimate URLs',
        'num_percent': 'Encoded characters may hide malicious content',
        'num_slash': 'Deep directory structures might hide malicious content',
        'has_ip_address': 'IP addresses instead of domain names are suspicious',
        'has_https': 'Lack of HTTPS indicates poor security',
        'has_suspicious_words': 'Contains terms commonly used in phishing',
        'dir_count': 'Excessive directories may hide true purpose',
        'path_length': 'Extremely long paths may hide malicious content',
        'has_double_slash': 'Double slashes in path may indicate URL manipulation'
    }