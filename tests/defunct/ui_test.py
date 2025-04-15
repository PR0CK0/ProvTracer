from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()  # Scales dynamically

btn = QPushButton("Click Me")
layout.addWidget(btn)

window.setLayout(layout)
window.showMaximized()  # Makes the window scale automatically

app.exec()
