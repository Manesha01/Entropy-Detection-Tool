import sys 
import filetype
import math
import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout
from PyQt5.QtGui import QFont

def get_entropy_strength_message(entropy):
    if entropy < 3.0:
        return "Very Low Entropy - Likely plain or structured data."
    elif entropy < 5.0:
        return "Low Entropy - Possibly compressed or lightly obfuscated."
    elif entropy < 7.0:
        return "Moderate Entropy - Possibly partially encrypted or compressed."
    elif entropy < 7.99:
        return "High Entropy - Likely encrypted or well-compressed data."
    else:
        return "Maximum Entropy - Strongly resembles encrypted or truly random data."

class EntropyDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Entropy Detection App')
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #2C3E50; color: white;")
        
        layout = QVBoxLayout()
        
        # Upload Button
        self.uploadButton = QPushButton('Upload File', self)
        self.uploadButton.setFont(QFont("Arial", 12, QFont.Bold))
        self.uploadButton.setStyleSheet("background-color: #1ABC9C; color: white; padding: 10px; border-radius: 5px;")
        self.uploadButton.clicked.connect(self.upload_file)
        layout.addWidget(self.uploadButton)
        
        # Entropy Display
        self.entropyLabel = QLabel('Entropy: N/A', self)
        self.entropyLabel.setFont(QFont("Arial", 12))
        layout.addWidget(self.entropyLabel)
        
        self.setLayout(layout)
    
    def calculate_entropy(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
        
        byte_freq = {}
        for byte in data:
            byte_freq[byte] = byte_freq.get(byte, 0) + 1
        
        total_bytes = len(data)
        entropy = 0
        for freq in byte_freq.values():
            prob = freq / total_bytes
            entropy -= prob * math.log2(prob)
        
        return entropy, data
    
    def display_histogram(self, data):
        window_size = 1024
        entropy_values = []
        
        for i in range(0, len(data), window_size):
            chunk = data[i:i+window_size]
            chunk_freq = {byte: chunk.count(byte) for byte in set(chunk)}
            total_bytes = len(chunk)
            chunk_entropy = -sum((freq / total_bytes) * math.log2(freq / total_bytes) for freq in chunk_freq.values())
            entropy_values.append(chunk_entropy)
        
        plt.figure(figsize=(10, 5))
        plt.plot(entropy_values, color='blue', linewidth=1)
        plt.title('Entropy Plot')
        plt.xlabel('Data Offset (1024-byte blocks)')
        plt.ylabel('Entropy')
        plt.grid()
        plt.show()
    
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*.*)')

        if file_path:
            # File Extension Validation
            allowed_extensions = {'.txt', '.bin', '.dat', '.jpg', '.png'}
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in allowed_extensions:
                self.entropyLabel.setText("Unsupported file type.")
                return

            # File Size Validation (max 50 MB)
            max_file_size = 50 * 1024 * 1024
            file_size = os.path.getsize(file_path)
            if file_size > max_file_size:
                self.entropyLabel.setText("File is too large. Max 50 MB allowed.")
                return

            # Safe file reading with error handling
            try:
                entropy, data = self.calculate_entropy(file_path)
            except Exception as e:
                self.entropyLabel.setText(f"Error reading file: {str(e)}")
                return

            message = get_entropy_strength_message(entropy)
            self.entropyLabel.setText(f"Entropy: {entropy:.4f} - {message}")
            self.display_histogram(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EntropyDetectionApp()
    window.show()
    sys.exit(app.exec_())
