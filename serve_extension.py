import http.server
import socketserver
import os
import sys
import mimetypes

PORT = 8001  # Changed port to avoid conflict
DIRECTORY = "extension"

def find_free_port(start_port):
    """Find next available port."""
    import socket
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            port += 1
    raise OSError("No free ports available")

def check_directory():
    """Check and create extension directory with required files."""
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory '{DIRECTORY}' does not exist!")
        print("Creating directory and copying files...")
        os.makedirs(DIRECTORY, exist_ok=True)

        # Copy required files
        files_to_copy = [
            'manifest.json',
            'popup.html',
            'popup.js',
            'utils.js',
            'background.js',
            'content.js'
        ]

        for file in files_to_copy:
            if os.path.exists(file):
                with open(file, 'r') as src:
                    content = src.read()
                    dest_path = os.path.join(DIRECTORY, file)
                    with open(dest_path, 'w') as dst:
                        dst.write(content)
                print(f"Copied {file} to extension directory")
            else:
                print(f"Warning: {file} not found")

        # Copy icons if they exist
        if os.path.exists('icons'):
            os.system(f'cp -r icons {DIRECTORY}/')
            print("Copied icons directory")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        print(f"[Server] {format%args}")

    def guess_type(self, path):
        """Guess the type of a file based on its extension."""
        ext = os.path.splitext(path)[1]
        if ext == '.js':
            return 'application/javascript'
        elif ext == '.html':
            return 'text/html'
        elif ext == '.css':
            return 'text/css'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return f'image/{ext[1:]}'
        elif ext == '.json':
            return 'application/json'
        return super().guess_type(path)

    def do_GET(self):
        # Add debug logging
        print(f"[Server] Handling GET request for: {self.path}")
        try:
            # Check if file exists
            if self.path == '/':
                self.path = '/popup.html'

            file_path = os.path.join(DIRECTORY, self.path.lstrip('/'))
            if os.path.exists(file_path):
                print(f"[Server] Serving file: {file_path}")
                # Set content type
                content_type = self.guess_type(file_path)
                print(f"[Server] Content-Type: {content_type}")
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()

                # Read and send file content
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                print(f"[Server] File not found: {file_path}")
                self.send_error(404, f"File not found: {self.path}")
        except Exception as e:
            print(f"[Server] Error serving file: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

def run_server():
    try:
        check_directory()

        print("\nCurrent directory contents:")
        os.system(f"ls -la {DIRECTORY}")

        print(f"\nStarting server at http://0.0.0.0:{PORT}")
        print(f"Open http://0.0.0.0:{PORT}/popup.html to view the extension interface")

        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print("Server is running. Press Ctrl+C to stop.")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {PORT} is already in use!")
        else:
            print(f"Server error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()