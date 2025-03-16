document.addEventListener('DOMContentLoaded', () => {
  const urlInput = document.getElementById('urlInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const resultDiv = document.getElementById('result');
  const loadingDiv = document.getElementById('loading');
  const featureChartDiv = document.getElementById('featureChart');

  // Get current tab URL when popup opens
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (tabs[0]?.url) {
      urlInput.value = tabs[0].url;
    }
  });

  const showLoading = () => {
    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';
    featureChartDiv.innerHTML = '';
  };

  const hideLoading = () => {
    loadingDiv.style.display = 'none';
  };

  const createScoreDisplay = (score, isPhishing) => {
    const percentage = Math.round(score * 100);
    const color = isPhishing ? '#c62828' : '#2e7d32';
    return `
      <div class="score-container">
        <div class="score" style="color: ${color}">${percentage}%</div>
        <div>Risk Score</div>
      </div>
    `;
  };

  const displayFeatureImportance = (features) => {
    const importance = getFeatureImportance();
    const sortedFeatures = Object.entries(importance)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    let html = '<h4>Top Impacting Features:</h4>';
    sortedFeatures.forEach(([feature, weight]) => {
      const barWidth = weight * 300;
      html += `
        <div class="feature-item">
          <div>${feature.replace(/_/g, ' ').toUpperCase()}</div>
          <div class="bar" style="width: ${barWidth}px"></div>
        </div>
      `;
    });

    featureChartDiv.innerHTML = html;
  };

  const displayResults = (url, analysis) => {
    const explanations = getFeatureExplanations();
    const features = analysis.features;

    let html = `
      <div class="result ${analysis.isPhishing ? 'danger' : 'safe'}">
        <h3>${analysis.isPhishing ? '⚠️ Potential Phishing Website' : '✅ Likely Legitimate Website'}</h3>
        ${createScoreDisplay(analysis.riskScore, analysis.isPhishing)}
        <p><strong>Risk Level:</strong> ${analysis.riskLevel}</p>
      </div>
      <div class="features">
        <h4>Security Analysis:</h4>
    `;

    // Show high-impact features first
    const highImpactFeatures = ['has_ip_address', 'has_https', 'has_suspicious_words', 'domain_in_path'];
    for (const feature of highImpactFeatures) {
      if (features[feature] > 0 || feature === 'has_https') {
        const value = feature === 'has_https' ? !features[feature] : features[feature];
        if (value) {
          html += `
            <div class="feature-item">
              <strong>${feature.replace(/_/g, ' ').toUpperCase()}</strong><br>
              <em>${explanations[feature]}</em>
            </div>
          `;
        }
      }
    }

    // Additional security tips
    html += `
      <h4>Security Tips:</h4>
      <div class="feature-item">
    `;

    if (analysis.isPhishing) {
      html += `
        <strong>⚠️ Warning Signs Detected:</strong>
        <ul>
          ${!features.has_https ? '<li>This website does not use HTTPS encryption</li>' : ''}
          ${features.has_ip_address ? '<li>URL contains an IP address instead of a domain name</li>' : ''}
          ${features.has_suspicious_words ? '<li>URL contains suspicious keywords</li>' : ''}
          ${features.domain_in_path ? '<li>Domain name is suspiciously repeated in the URL</li>' : ''}
        </ul>
      `;
    } else {
      html += `
        <strong>✅ Security Features:</strong>
        <ul>
          ${features.has_https ? '<li>Website uses secure HTTPS encryption</li>' : ''}
          <li>No suspicious patterns detected in URL structure</li>
          ${features.url_length < 75 ? '<li>URL length is within normal range</li>' : ''}
        </ul>
      `;
    }

    html += `
      </div>
    </div>
    `;

    resultDiv.innerHTML = html;
    displayFeatureImportance(features);
  };

  analyzeBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();

    if (!url) {
      resultDiv.innerHTML = '<div class="result danger">Please enter a URL</div>';
      return;
    }

    try {
      showLoading();
      const features = extractFeatures(url);
      const analysis = analyzeUrl(features);
      hideLoading();
      displayResults(url, analysis);

      // Save to history
      chrome.storage.local.get(['history'], (result) => {
        const history = result.history || [];
        history.unshift({
          url,
          timestamp: new Date().toISOString(),
          riskScore: analysis.riskScore,
          isPhishing: analysis.isPhishing
        });
        // Keep only last 100 entries
        chrome.storage.local.set({ history: history.slice(0, 100) });
      });
    } catch (e) {
      hideLoading();
      resultDiv.innerHTML = `<div class="result danger">Error analyzing URL: ${e.message}</div>`;
    }
  });
});