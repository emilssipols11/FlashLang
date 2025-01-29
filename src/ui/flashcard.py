from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from ..services.data_handler import DataHandler
import random


class Flashcard(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.data_handler = DataHandler()
        self.stacked_widget = stacked_widget
        self.all_words = []
        self.current_word = None
        self.ultra_mode = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Back button to return to main menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        # Source and Target Languages at the top
        self.languages_label = QLabel()
        self.languages_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.languages_label)

        # Label to show the word
        self.flashcard_label = QLabel()
        self.flashcard_label.setAlignment(Qt.AlignCenter)
        self.flashcard_label.setWordWrap(True)
        self.flashcard_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.flashcard_label)

        # Feedback Label for correct/incorrect
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 24px;")
        self.feedback_label.hide()  # Hide initially
        layout.addWidget(self.feedback_label)

        # Input field for the user's translation
        self.translation_input = QLineEdit()
        self.translation_input.setPlaceholderText("Enter translation")
        layout.addWidget(self.translation_input)

        # Buttons for submitting and skipping
        buttons_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_translation)
        buttons_layout.addWidget(self.submit_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.skip_flashcard)
        buttons_layout.addWidget(self.skip_button)

        # Bind Enter key to submit translation
        self.translation_input.returnPressed.connect(self.submit_translation)

        layout.addLayout(buttons_layout)

    def show_flashcard(self):
        if not self.all_words:
            QMessageBox.information(self, "No Words Available", "There are no words to practice.")
            self.show_main_menu()
            return

        # Select a word based on quotient values
        word_entry = self.select_word_based_on_quotient()
        self.current_word = word_entry

        source_lang = word_entry['source_language']
        target_lang = word_entry['target_language']

        # Determine translation direction
        if self.ultra_mode:
            # Randomly decide direction
            self.current_direction = random.choice(['forward', 'reverse'])
        else:
            # Default direction (source to target)
            self.current_direction = 'forward'

        # Update languages label and display word accordingly
        if self.current_direction == 'forward':
            # From source to target language
            self.languages_label.setText(f"{source_lang} → {target_lang}")
            self.flashcard_label.setText(f"{word_entry['original']}")
        else:
            # From target to source language
            self.languages_label.setText(f"{target_lang} → {source_lang}")
            self.flashcard_label.setText(f"{word_entry['translation']}")

        self.translation_input.clear()
        self.feedback_label.hide()

    def select_word_based_on_quotient(self):
        # Calculate total weight
        total_weight = sum(word['quotient'] for word in self.all_words)
        if total_weight == 0:
            total_weight = 1.0  # To avoid division by zero
        weights = [word['quotient'] / total_weight for word in self.all_words]

        # Use random.choices to select one word
        selected_word = random.choices(self.all_words, weights=weights, k=1)[0]
        return selected_word
    
    def submit_translation(self):
        user_translation = self.translation_input.text().strip()
        if user_translation:
            word_entry = self.current_word
            if self.current_direction == 'forward':
                # From source to target
                correct_translation = word_entry['translation']
                user_answer = user_translation
            else:
                # From target to source
                correct_translation = word_entry['original']
                user_answer = user_translation

            if user_answer.lower() == correct_translation.lower():
                # Update quotient, decrease if correct
                word_entry['quotient'] *= 0.5
                # Save updated quotient to CSV
                self.data_handler.update_word(word_entry)
                # Display green checkmark
                self.show_feedback(correct=True)
            else:
                # Update quotient, increase if incorrect
                word_entry['quotient'] *= 2
                # Save updated quotient to CSV
                self.data_handler.update_word(word_entry)
                # Display correct translation
                self.show_feedback(correct=False, correct_translation=correct_translation)
        else:
            QMessageBox.warning(self, "Input Error", "Please enter your translation.")

    def skip_flashcard(self):
        word_entry = self.current_word
        # Update quotient, increase if skipped (treated as incorrect)
        word_entry['quotient'] *= 2
        # Save updated quotient to CSV
        self.data_handler.update_word(word_entry)
        # Display the correct translation
        self.show_feedback(correct=False, correct_translation=word_entry['translation'])

    def show_feedback(self, correct, correct_translation=None):
        if correct:
            # Display green checkmark
            self.feedback_label.setText("✔")
            self.feedback_label.setStyleSheet("font-size: 48px; color: green;")
        else:
            # Display red cross and correct translation
            if self.current_direction == 'forward':
                # From source to target
                correct_lang = self.current_word['target_language']
            else:
                # From target to source
                correct_lang = self.current_word['source_language']
            self.feedback_label.setText(f"✖ Correct ({correct_lang}): {correct_translation}")
            self.feedback_label.setStyleSheet("font-size: 24px; color: red;")
        self.feedback_label.show()
        # Hide feedback after 1 second
        QTimer.singleShot(1000, self.hide_feedback)

    def hide_feedback(self):
        self.feedback_label.hide()
        self.show_flashcard()
    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.practice_screen)

    def load_words(self, words):
        self.all_words = words

    def set_ultra_mode(self, ultra_mode):
        self.ultra_mode = ultra_mode
