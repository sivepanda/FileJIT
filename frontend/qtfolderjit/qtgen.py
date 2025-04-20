import sys
import os
import shutil
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar,
    QPushButton, QHBoxLayout, QLineEdit, QListWidget, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Resolve target folder path relative to script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'autosort'))

# Fake long-running process
def fake_processing():
    time.sleep(5)

class ProcessingWorker(QThread):
    done = pyqtSignal(str)

    def __init__(self, file_path, target_dir):
        super().__init__()
        self.file_path = file_path
        self.target_dir = target_dir

    def run(self):
        try:
            filename = os.path.basename(self.file_path)
            destination = os.path.join(self.target_dir, filename)
            shutil.move(self.file_path, destination)

            fake_processing()  # Simulated task
            self.done.emit("✅ Done")
        except Exception as e:
            self.done.emit(f"❌ Error: {str(e)}")

class FileDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.label = QLabel("Drop a file here to start processing", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)

        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        self.yes_button.setVisible(False)
        self.no_button.setVisible(False)

        self.yes_button.clicked.connect(lambda: self.label.setText("You clicked Yes ✅"))
        self.no_button.clicked.connect(lambda: self.label.setText("You clicked No ❌"))

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.label.setText("⏳ Processing...")
                self.progress.setVisible(True)
                self.yes_button.setVisible(False)
                self.no_button.setVisible(False)

                self.worker = ProcessingWorker(file_path, TARGET_FOLDER)
                self.worker.done.connect(self.finish_processing)
                self.worker.start()

    def finish_processing(self, message):
        self.progress.setVisible(False)
        self.label.setText(message)
        self.yes_button.setVisible(True)
        self.no_button.setVisible(True)

class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search in autosort folder...")
        self.search_input.returnPressed.connect(self.perform_search)

        self.result_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.result_list)
        self.setLayout(layout)

    def perform_search(self):
        query = self.search_input.text().lower()
        self.result_list.clear()

        if not os.path.isdir(TARGET_FOLDER):
            self.result_list.addItem("❌ autosort folder not found.")
            return

        files = os.listdir(TARGET_FOLDER)
        for file in files:
            if query in file.lower():
                self.result_list.addItem(file)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📂 File Processor & Search Tool")
        self.setGeometry(300, 300, 500, 300)

        self.tabs = QTabWidget()
        self.tabs.addTab(FileDropWidget(), "📤 Drop File")
        self.tabs.addTab(SearchWidget(), "🔍 Search")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
