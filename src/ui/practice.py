from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QCheckBox, QPushButton, QMessageBox, QHBoxLayout
from ..services.data_handler import DataHandler
import random

class Practice(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.data_handler = DataHandler()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        # Source Selector
        self.practice_source_selector = QComboBox()
        self.practice_source_selector.addItems(self.data_handler.get_sources())
        self.practice_source_selector.currentIndexChanged.connect(self.update_file_list)
        layout.addWidget(QLabel("Select Source:"))
        layout.addWidget(self.practice_source_selector)

        # List of available CSV files
        self.file_list = QListWidget()
        self.update_file_list()
        layout.addWidget(QLabel("Select lessons to practice:"))
        layout.addWidget(self.file_list)
        self.file_list.setSelectionMode(QListWidget.MultiSelection)

        # Ultra Mode Checkbox
        self.ultra_mode_checkbox = QCheckBox("Enable Ultra Mode (Random Direction)")
        layout.addWidget(self.ultra_mode_checkbox)

        # Buttons for different practice modes
        buttons_layout = QHBoxLayout()

        # Button to start flashcard practice
        self.start_practice_button = QPushButton("Flashcard Practice")
        self.start_practice_button.clicked.connect(self.start_flashcard_practice)
        buttons_layout.addWidget(self.start_practice_button)

        # Button to start gap test
        self.start_gap_test_button = QPushButton("Gap Test")
        self.start_gap_test_button.clicked.connect(self.start_gap_test)
        buttons_layout.addWidget(self.start_gap_test_button)

        # Button to start writing assignment
        self.start_writing_assignment_button = QPushButton("Writing Assignment")
        self.start_writing_assignment_button.clicked.connect(self.start_writing_assignment)
        buttons_layout.addWidget(self.start_writing_assignment_button)

        layout.addLayout(buttons_layout)

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.main_menu_screen)


    def start_writing_assignment(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.writing_assignment_screen)

    def update_file_list(self):
        self.file_list.clear()
        source_name = self.practice_source_selector.currentText()
        if source_name:
            files = self.data_handler.get_csv_files(source_name)
            self.file_list.addItems(files)

    def start_flashcard_practice(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            all_words = self.data_handler.load_words(source_name, selected_files)
            if not all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Get Ultra Mode setting
            ultra_mode_enabled = self.ultra_mode_checkbox.isChecked()
            # Start practice
            self.stacked_widget.flashcard_screen.load_words(all_words)
            self.stacked_widget.flashcard_screen.set_ultra_mode(ultra_mode_enabled)
            self.stacked_widget.flashcard_screen.show_flashcard()
            self.stacked_widget.setCurrentWidget(self.stacked_widget.flashcard_screen)
        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")

    def start_gap_test(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            all_words = self.data_handler.load_words(source_name, selected_files)
            if not all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Start gap test
            self.stacked_widget.gap_test_screen.set_lesson_data(all_words)
            self.stacked_widget.gap_test_screen.generate_gap_test()
            self.stacked_widget.setCurrentWidget(self.stacked_widget.gap_test_screen)

        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")

    def start_writing_assignment(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            all_words = self.data_handler.load_words(source_name, selected_files)
            if not all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Start writing assignment
            self.stacked_widget.writing_assignment_screen.set_lesson_data(all_words)
            self.stacked_widget.setCurrentWidget(self.stacked_widget.writing_assignment_screen)
        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")
