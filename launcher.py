from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import subprocess, os
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Parablocks Launcher")
        self.setFixedWidth(400)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        label = QLabel("Parablocks Launcher")
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
        print("Launching Parablocks...")
        subprocess.run("python perlin.py", shell=True)
        subprocess.Popen("python main.py", shell=True)
        os._exit(0)

    def get_program_directory(self):
        return os.path.dirname(os.path.realpath(__file__))

app = QApplication([])

window = MainWindow()
window.show()

app.exec()