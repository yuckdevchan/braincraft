from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import subprocess, os
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("braincraft Launcher")
        self.setFixedWidth(400)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        label = QLabel("braincraft Launcher")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        guide = QLabel("Controls: WASD to move, shift to sprint, ctrl to crouch, space to jump, mouse to look around")
        guide.setWordWrap(True)
        guide.setAlignment(Qt.AlignCenter)
        layout.addWidget(guide)

        layout.addStretch()

        # set qss
        self.setStyleSheet("""
                           QPushButton {
                           background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 12px;
                            padding: 7px 14px;
                            text-align: center;
                            }
                            QPushButton:pressed {
                            background-color: #45a049;
                            }
                            QPushButton:hover {
                            background-color: #45a049;
                            }
                            """)
        launch_button = QPushButton("Launch")
        launch_button.clicked.connect(self.launch)
        layout.addWidget(launch_button)

    def launch(self):
        print("Launching braincraft...")
        subprocess.Popen(["python", os.path.join(self.get_program_directory(), "main.py")])
        os._exit(0)

    def get_program_directory(self):
        return os.path.dirname(os.path.realpath(__file__))

app = QApplication([])

window = MainWindow()
window.show()

app.exec()