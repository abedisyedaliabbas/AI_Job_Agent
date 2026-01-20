"""
Run the web application
"""
import webbrowser
import threading
import time
from app import app

def open_browser():
    """Open browser after a short delay to ensure server is ready"""
    time.sleep(1.5)  # Wait for server to start
    url = "http://localhost:5000"
    print(f"\n🌐 Opening browser: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    print("=" * 60)
    print("AI Job Agent - Web Application")
    print("=" * 60)
    print("\nStarting server...")
    print("Browser will open automatically at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
