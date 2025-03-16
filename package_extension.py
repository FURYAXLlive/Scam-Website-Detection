import os
import zipfile
import shutil

# First generate icons if script exists
if os.path.exists('generate_icons.py'):
    exec(open('generate_icons.py').read())

# Create extension directory
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
    'content.js'  # Added content.js to the list
]

for file in files_to_copy:
    shutil.copy(file, 'extension/')

# Copy icons directory
shutil.copytree('icons', 'extension/icons')

# Create ZIP file
with zipfile.ZipFile('phishing_detector.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('extension'):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, 'extension')
            zipf.write(file_path, arcname)

print("Extension package created as 'phishing_detector.zip'")
print("\nTo install in Chrome:")
print("1. Open Chrome and go to chrome://extensions/")
print("2. Enable 'Developer mode' (top right)")
print("3. Drag and drop 'phishing_detector.zip' into the Chrome extensions page")
print("4. Or click 'Load unpacked' and select the 'extension' folder")