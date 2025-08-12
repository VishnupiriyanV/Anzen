from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os

FAKE_DB = {
    "users": {
        "admin": "password123",
        "user01": "qwerty",
    }
}

class VulnerableHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            file_path = query_params.get('page', ['index.html'])[0]
            
            try:
                with open(file_path, 'r') as f:
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.wfile.write(b"File not found.")
            except Exception as e:
                self.wfile.write(f"Error: {e}".encode())
            return

        if parsed_path.path == '/search':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            search_query = query_params.get('q', [''])[0]
            
            response_html = f"""
            <html>
                <body>
                    <h1>Search Results</h1>
                    <p>You searched for: {search_query}</p>
                </body>
            </html>
            """
            self.wfile.write(response_html.encode())
            return
            
        if parsed_path.path == '/api/user':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            username = query_params.get('username', [''])[0]

            mock_query = f"SELECT * FROM users WHERE username = '{username}'"
            print(f"[DB] Executing simulated query: {mock_query}")

            if "' OR 1=1" in username:
                response_text = str(FAKE_DB['users'])
            else:
                user_pass = FAKE_DB['users'].get(username, "User not found.")
                response_text = f"Password for {username}: {user_pass}"

            self.wfile.write(response_text.encode())
            return

        self.send_error(404, "Not Found")


def run_server(server_class=HTTPServer, handler_class=VulnerableHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"[*] Starting intentionally VULNERABLE server on port {port}...")
    print("[!] WARNING: This server is insecure. Use for testing only.")
    print("[!] Press Ctrl+C to shut down.")
    httpd.serve_forever()

if __name__ == '__main__':
    with open("index.html", "w") as f:
        f.write("<h1>Welcome to the Vulnerable App!</h1>")
        f.write("<p>Try to find the vulnerabilities.</p>")
        f.write("<p>Check out the <a href='/search?q=test'>search page</a>.</p>")

    run_server()
