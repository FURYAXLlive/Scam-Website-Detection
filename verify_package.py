import zipfile

def print_zip_contents(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print("\nContents of", zip_path, ":")
        for info in zip_ref.infolist():
            print(f"{info.filename:<30} {info.file_size:>10} bytes")

print_zip_contents('phishing_detector.zip')
