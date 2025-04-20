import sys
import os
import shutil
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar,
    QPushButton, QHBoxLayout, QLineEdit, QListWidget, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import the semantic search module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from filesearch import EmbeddingHandler

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

class EmbeddingWorker(QThread):
    done = pyqtSignal(bool)
    
    def __init__(self, embedding_handler):
        super().__init__()
        self.embedding_handler = embedding_handler
    
    def run(self):
        success = self.embedding_handler.generate_embeddings()
        self.done.emit(success)

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
    def __init__(self, embedding_handler):
        super().__init__()
        self.embedding_handler = embedding_handler
        
        self.status_label = QLabel("Initializing semantic search engine...")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Enter your search query...")
        self.search_input.setEnabled(False)  # Disable until embeddings are ready
        self.search_input.returnPressed.connect(self.perform_semantic_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.setEnabled(False)  # Disable until embeddings are ready
        self.search_button.clicked.connect(self.perform_semantic_search)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        self.result_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addLayout(search_layout)
        layout.addWidget(self.result_list)
        self.setLayout(layout)
        
        # Start the embedding generation process
        self.embedding_worker = EmbeddingWorker(self.embedding_handler)
        self.embedding_worker.done.connect(self.on_embeddings_ready)
        self.embedding_worker.start()

    def on_embeddings_ready(self, success):
        if success:
            self.status_label.setText("Semantic search ready. Type your query to find similar files.")
            self.search_input.setEnabled(True)
            self.search_button.setEnabled(True)
        else:
            self.status_label.setText("❌ Failed to generate embeddings. Check console for errors.")

    def perform_semantic_search(self):
        query = self.search_input.text()
        if not query:
            return
            
        self.result_list.clear()
        
        try:
            results = self.embedding_handler.search_files(query)
            
            if not results:
                self.result_list.addItem("No matching files found.")
                return
                
            self.result_list.addItem("Top 3 matches:")
            for i, (file_path, distance) in enumerate(results):
                self.result_list.addItem(f"{i + 1}. {file_path} (Distance: {distance:.4f})")
        except Exception as e:
            self.result_list.addItem(f"Error during search: {str(e)}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📂 Semantic File Search Tool")
        self.setGeometry(300, 300, 700, 400)
        
        # Path for files to search (update this to your root directory)
        self.base_path = "./../../root"  # Root directory to scan
        
        # Create the embedding handler
        self.embedding_handler = EmbeddingHandler(self.base_path)

        self.tabs = QTabWidget()
        self.tabs.addTab(FileDropWidget(), "📤 Drop File")
        self.tabs.addTab(SearchWidget(self.embedding_handler), "🔍 Semantic Search")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())