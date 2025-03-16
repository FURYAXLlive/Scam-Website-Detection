// Create and inject warning banner if needed
function showPhishingWarning(analysis) {
  const banner = document.createElement('div');
  banner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background-color: #c62828;
    color: white;
    padding: 15px;
    text-align: center;
    z-index: 999999;
    font-family: Arial, sans-serif;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;
  
  banner.innerHTML = `
    <strong>⚠️ Warning: Potential Phishing Website Detected!</strong>
    <p style="margin: 5px 0">This website shows characteristics commonly associated with phishing attempts.</p>
    <button onclick="this.parentElement.style.display='none'" 
            style="background: white; color: #c62828; border: none; padding: 5px 10px; margin-top: 5px; cursor: pointer; border-radius: 3px;">
      Dismiss
    </button>
  `;
  
  document.body.insertBefore(banner, document.body.firstChild);
}

// Listen for warning messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "showWarning") {
    showPhishingWarning(message.data);
  }
});
