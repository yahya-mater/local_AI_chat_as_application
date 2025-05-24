from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QThread, Signal
from PySide6.QtGui import QMovie, QIcon
import sys
import threading
import time
import open_webui
import requests

URL = "http://127.0.0.1:8080"

class LoadingScreen(QWidget):
    """A small window with a loading spinner shown while the server starts."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starting Open WebUI")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Use an animated GIF as a loading spinner
        self.movie = QMovie("static\loading.gif")  # Provide your own spinner GIF  
        self.label.setMovie(self.movie)
        self.movie.start()

        layout.addWidget(self.label)
        self.setLayout(layout)

class ServerCheckThread(QThread):
    """Thread to check when the server is ready."""
    server_ready = Signal(bool)

    def run(self):
        start_time = time.time()
        timeout = 60  # Maximum wait time
        while time.time() - start_time < timeout:
            try:
                response = requests.get(URL)
                if response.status_code == 200:
                    self.server_ready.emit(True)
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

        self.server_ready.emit(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.setWindowTitle("Open WebUI")

        # Set default icon before fetching the real one
        self.setWindowIcon(QIcon("default_icon.png"))

        # Connect signal to update icon dynamically
        self.browser.page().iconChanged.connect(self.update_icon)
        self.browser.page().titleChanged.connect(self.update_title)

    def load_page(self):
        """Loads the webpage after the server is up."""
        self.browser.load(QUrl(URL))
        
        self.showMaximized()
        #self.show()  # Show the main window

    def update_icon(self, icon: QIcon):
        """Update the application window icon when the webpage icon changes."""
        self.setWindowIcon(icon)
        print("Favicon updated.")
    
    def update_title(self, Title):
        """Update the application window Title when the webpage Title changes."""
        self.setWindowTitle(Title)
        print("Title updated.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the loading screen first
    loading_screen = LoadingScreen()
    loading_screen.show()

    # Start the Open WebUI server in a background thread
    webui_thread = threading.Thread(target=open_webui.serve, daemon=True)
    webui_thread.start()

    # Create the main window but don't show it yet
    main_window = MainWindow()

    # Start a thread to check if the server is up
    server_check_thread = ServerCheckThread()

    def on_server_ready(success):
        """Once the server is ready, close the loading screen and show the browser."""
        loading_screen.close()
        if success:
            print("Server started successfully.")
            main_window.load_page()  # Load the page and show the window
        else:
            print("Server failed to start within the timeout period.")

    server_check_thread.server_ready.connect(on_server_ready)
    server_check_thread.start()

    sys.exit(app.exec())  # Start the event loop ONCE
