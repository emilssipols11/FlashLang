from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget


class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Language Flashcards")
        layout = QVBoxLayout(self)

        # Navigation buttons
        input_data_button = QPushButton("Input Data")
        input_data_button.clicked.connect(self.show_input_data)
        layout.addWidget(input_data_button)

        practice_button = QPushButton("Practice")
        practice_button.clicked.connect(self.show_practice)
        layout.addWidget(practice_button)

    def show_input_data(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.input_data_screen)

    def show_practice(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.practice_screen)
