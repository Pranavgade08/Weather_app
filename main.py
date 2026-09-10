"""
Main launcher for the Weather Web Application.
Starts the server and automatically opens http://localhost:5000 in your web browser.
"""

import threading
import time
import webbrowser
from app import app


def open_browser():
    """Waits for server to initialize, then opens the browser."""
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")


def main():
    print("\n" + "=" * 55)
    print(" Modern Weather App Server is starting...")
    print(" Live Website: http://127.0.0.1:5000")
    print("=" * 55 + "\n")

    # Automatically open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask Web Server
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
