chrome.runtime.onInstalled.addListener(() => {
  console.log('Phishing URL Detector extension installed');
});

// Listen for navigation events
chrome.webNavigation.onCommitted.addListener((details) => {
  if (details.frameId === 0) {  // Only check main frame
    try {
      const features = extractFeatures(details.url);
      const analysis = analyzeUrl(features);

      if (analysis.isPhishing) {
        // Show warning notification
        chrome.action.setBadgeText({
          text: "⚠️",
          tabId: details.tabId
        });

        chrome.action.setBadgeBackgroundColor({
          color: "#c62828",
          tabId: details.tabId
        });

        // Send warning to content script
        chrome.tabs.sendMessage(details.tabId, {
          action: "showWarning",
          data: analysis
        });
      } else {
        chrome.action.setBadgeText({
          text: "✓",
          tabId: details.tabId
        });

        chrome.action.setBadgeBackgroundColor({
          color: "#2e7d32",
          tabId: details.tabId
        });
      }
    } catch (e) {
      console.error("Error analyzing URL:", e);
    }
  }
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyzeUrl") {
    try {
      const features = extractFeatures(request.url);
      const result = analyzeUrl(features);
      sendResponse({ success: true, result });
    } catch (e) {
      sendResponse({ success: false, error: e.message });
    }
    return true;
  }
});