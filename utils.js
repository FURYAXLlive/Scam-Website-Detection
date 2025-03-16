// Feature extraction and analysis utilities
const extractFeatures = (url) => {
  try {
    const features = {};
    const parsedUrl = new URL(url);

    // Length based features
    features.url_length = url.length;
    features.hostname_length = parsedUrl.hostname.length;

    // Domain specific features
    const domain = parsedUrl.hostname;
    features.domain_in_path = parsedUrl.pathname.toLowerCase().includes(domain.toLowerCase()) ? 1 : 0;
    features.domain_age_days = 0; // Placeholder

    // Special character features
    features.num_dots = (url.match(/\./g) || []).length;
    features.num_hyphens = (url.match(/-/g) || []).length;
    features.num_at = (url.match(/@/g) || []).length;
    features.num_question_marks = (url.match(/\?/g) || []).length;
    features.num_and = (url.match(/&/g) || []).length;
    features.num_equal = (url.match(/=/g) || []).length;
    features.num_underscore = (url.match(/_/g) || []).length;
    features.num_tilde = (url.match(/~/g) || []).length;
    features.num_percent = (url.match(/%/g) || []).length;
    features.num_slash = (url.match(/\//g) || []).length;

    // Security indicators
    features.has_ip_address = /^(http|https):\/\/(\d{1,3}\.){3}\d{1,3}/.test(url) ? 1 : 0;
    features.has_https = parsedUrl.protocol === 'https:' ? 1 : 0;
    features.has_suspicious_words = /(secure|login|signin|bank|account|update|verify)/i.test(url) ? 1 : 0;

    // Path analysis
    features.dir_count = parsedUrl.pathname.split('/').filter(x => x).length;
    features.path_length = parsedUrl.pathname.length;
    features.has_double_slash = parsedUrl.pathname.includes('//') ? 1 : 0;

    // Convert features object to array in the same order as Python model
    const featureOrder = [
      'url_length', 'hostname_length', 'domain_in_path', 'domain_age_days',
      'num_dots', 'num_hyphens', 'num_at', 'num_question_marks',
      'num_and', 'num_equal', 'num_underscore', 'num_tilde',
      'num_percent', 'num_slash', 'has_ip_address', 'has_https',
      'has_suspicious_words', 'dir_count', 'path_length', 'has_double_slash'
    ];

    return featureOrder.map(key => features[key]);
  } catch (e) {
    throw new Error(`Error extracting features: ${e.message}`);
  }
};

// Updated scoring weights to match Python model
const getFeatureImportance = () => {
  return {
    has_ip_address: 0.15,
    has_suspicious_words: 0.12,
    domain_in_path: 0.10,
    has_https: 0.10,
    url_length: 0.08,
    num_dots: 0.07,
    num_at: 0.07,
    has_double_slash: 0.06,
    hostname_length: 0.05,
    path_length: 0.05,
    num_hyphens: 0.05,
    num_slash: 0.04,
    num_equal: 0.02,
    num_and: 0.02,
    num_underscore: 0.01,
    num_tilde: 0.01
  };
};

const analyzeUrl = (features) => {
  const featureNames = [
    'url_length', 'hostname_length', 'domain_in_path', 'domain_age_days',
    'num_dots', 'num_hyphens', 'num_at', 'num_question_marks',
    'num_and', 'num_equal', 'num_underscore', 'num_tilde',
    'num_percent', 'num_slash', 'has_ip_address', 'has_https',
    'has_suspicious_words', 'dir_count', 'path_length', 'has_double_slash'
  ];

  const featureObj = {};
  featureNames.forEach((name, index) => {
    featureObj[name] = features[index];
  });

  let riskScore = 0;
  const importance = getFeatureImportance();
  
  // Match Python model thresholds
  if (featureObj.has_ip_address) riskScore += 0.15;
  if (featureObj.has_suspicious_words) riskScore += 0.12;
  if (featureObj.domain_in_path) riskScore += 0.10;
  if (!featureObj.has_https) riskScore += 0.10;
  if (featureObj.url_length > 75) riskScore += 0.08;
  if (featureObj.num_dots > 3) riskScore += 0.07;
  if (featureObj.num_at > 0) riskScore += 0.07;
  if (featureObj.has_double_slash) riskScore += 0.06;
  if (featureObj.hostname_length > 30) riskScore += 0.05;
  if (featureObj.path_length > 50) riskScore += 0.05;
  if (featureObj.num_slash > 4) riskScore += 0.04;
  if (featureObj.num_equal > 2) riskScore += 0.02;

  // Match the Python model's threshold of 0.5
  const isPhishing = riskScore >= 0.5;

  return {
    isPhishing: isPhishing,
    riskScore: Math.min(riskScore, 0.99),
    features: featureObj,
    riskLevel: riskScore < 0.3 ? 'Low' : riskScore < 0.6 ? 'Medium' : 'High'
  };
};

const getFeatureExplanations = () => {
  return {
    url_length: 'Unusually long URLs may indicate hidden malicious content',
    hostname_length: 'Extremely long hostnames are often suspicious',
    domain_in_path: 'Domain name repeated in URL path may indicate deception',
    domain_age_days: 'Newly registered domains are more likely to be malicious',
    num_dots: 'Excessive dots may indicate subdomain abuse',
    num_hyphens: 'Multiple hyphens are common in phishing URLs',
    num_at: 'The @ symbol in URLs can be used to obscure the actual destination',
    num_question_marks: 'Multiple query parameters may hide malicious code',
    num_and: 'Numerous parameters might indicate suspicious data collection',
    num_equal: 'Many parameters could suggest data harvesting',
    num_underscore: 'Uncommon in legitimate URLs',
    num_tilde: 'Rarely used in legitimate URLs',
    num_percent: 'Encoded characters may hide malicious content',
    num_slash: 'Deep directory structures might hide malicious content',
    has_ip_address: 'IP addresses instead of domain names are suspicious',
    has_https: 'Lack of HTTPS indicates poor security',
    has_suspicious_words: 'Contains terms commonly used in phishing',
    dir_count: 'Excessive directories may hide true purpose',
    path_length: 'Extremely long paths may hide malicious content',
    has_double_slash: 'Double slashes in path may indicate URL manipulation'
  };
};