# main.py

from src.ui import FlashcardApp
import sys
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
