from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class HomeView(QWidget):
    def __init__(self, controller):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(QLabel("🏠 ДОБРО ПОЖАЛОВАТЬ В DERDATE"))
        btn = QPushButton("ПЕРЕЙТИ В МАГАЗИН")
        btn.setFixedSize(200, 50)
        btn.clicked.connect(lambda: controller.switch_page(1))
        layout.addWidget(btn)
