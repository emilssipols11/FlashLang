from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QComboBox, QPushButton, QListWidget, QHBoxLayout, QMessageBox, QListWidgetItem
)
from ..services.translation_service import TranslationService
from ..services.data_handler import DataHandler


class InputData(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.translation_service = TranslationService()
        self.data_handler = DataHandler()
        self.current_words = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        # Input fields
        layout.addWidget(QLabel("Source Name:"))
        self.source_name_input = QLineEdit()
        layout.addWidget(self.source_name_input)

        layout.addWidget(QLabel("Lesson Title:"))
        self.lesson_title_input = QLineEdit()
        layout.addWidget(self.lesson_title_input)

        # Source language selector
        self.source_language_selector = QComboBox()
        self.source_language_selector.addItems(self.translation_service.get_supported_languages())
        self.source_language_selector.setCurrentText("Dutch")  # Default to Dutch
        layout.addWidget(QLabel("Select source language:"))
        layout.addWidget(self.source_language_selector)

        # Target language selector
        self.target_language_selector = QComboBox()
        self.target_language_selector.addItems(self.translation_service.get_supported_languages())
        self.target_language_selector.setCurrentText("English")  # Default to English
        layout.addWidget(QLabel("Select target language:"))
        layout.addWidget(self.target_language_selector)

        # Input field for the word and fetch button
        word_input_layout = QHBoxLayout()
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter word in source language")
        word_input_layout.addWidget(self.word_input)

        fetch_translation_button = QPushButton("Fetch Translation")
        fetch_translation_button.clicked.connect(self.fetch_translation)
        word_input_layout.addWidget(fetch_translation_button)

        # Bind Enter key to submit translation
        self.word_input.returnPressed.connect(self.fetch_translation)

        layout.addLayout(word_input_layout)

        # Editable field to show and edit the translation
        self.translation_edit = QLineEdit()
        self.translation_edit.setPlaceholderText("Translation will appear here")
        layout.addWidget(self.translation_edit)

        # Add Word Button
        add_word_button = QPushButton("Add Word")
        add_word_button.clicked.connect(self.add_word)
        layout.addWidget(add_word_button)

        # Bind Enter key to add word
        self.translation_edit.returnPressed.connect(self.add_word)

        # List to display words and their translations
        self.word_list_widget = QListWidget()
        layout.addWidget(self.word_list_widget)

        # Buttons to delete selected words and save file
        buttons_layout = QHBoxLayout()
        delete_word_button = QPushButton("Delete Selected")
        delete_word_button.clicked.connect(self.delete_selected_words)
        buttons_layout.addWidget(delete_word_button)

        save_file_button = QPushButton("Save File")
        save_file_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(save_file_button)

        layout.addLayout(buttons_layout)

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.main_menu_screen)

    def fetch_translation(self):
        word = self.word_input.text().strip()
        if word:
            source_language_name = self.source_language_selector.currentText()
            target_language_name = self.target_language_selector.currentText()

            # Disable language selectors after first word is added
            if len(self.current_words) == 0:
                self.source_language_selector.setEnabled(False)
                self.target_language_selector.setEnabled(False)

            translation = self.translation_service.translate_word(word, source_language_name, target_language_name)
            if translation:
                # Display the translation in the editable field
                self.translation_edit.setText(translation)
            else:
                QMessageBox.warning(self, "Translation Error", "Failed to translate the word.")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a word.")

    def add_word(self):
        word = self.word_input.text().strip()
        translation = self.translation_edit.text().strip()
        if word and translation:
            source_language_name = self.source_language_selector.currentText()
            target_language_name = self.target_language_selector.currentText()

            # Add to current words list
            self.current_words.append({
                'original': word,
                'translation': translation,
                'quotient': 1.0,
                'source_language': source_language_name,
                'target_language': target_language_name
            })
            # Add to list widget
            list_item = QListWidgetItem(f"{word} - {translation}")
            self.word_list_widget.addItem(list_item)
            # Clear input fields
            self.word_input.clear()
            self.translation_edit.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both the word and its translation.")

    def delete_selected_words(self):
        selected_items = self.word_list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.word_list_widget.row(item)
            self.word_list_widget.takeItem(row)
            del self.current_words[row]
        # If all words are deleted, re-enable language selectors
        if len(self.current_words) == 0:
            self.source_language_selector.setEnabled(True)
            self.target_language_selector.setEnabled(True)

    def save_file(self):
        lesson_title = self.lesson_title_input.text().strip()
        source_name = self.source_name_input.text().strip()

        if not source_name:
            QMessageBox.warning(self, "Input Error", "Please enter a source name.")
            return

        if not lesson_title:
            QMessageBox.warning(self, "Input Error", "Please enter a lesson title or CSV file name.")
            return

        if not self.current_words:
            QMessageBox.warning(self, "No Words", "No words to save.")
            return

        # Save to CSV
        self.data_handler.save_words(source_name, lesson_title, self.current_words)
        QMessageBox.information(self, "File Saved", f"Words saved to {source_name}/{lesson_title}.csv")
        # Clear current words and UI elements
        self.current_words.clear()
        self.word_list_widget.clear()
        self.lesson_title_input.clear()
        self.word_input.clear()
        self.translation_edit.clear()
        self.source_language_selector.setEnabled(True)
        self.target_language_selector.setEnabled(True)
        self.source_name_input.clear()
