from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QStackedWidget,
    QLabel, QLineEdit, QListWidget, QHBoxLayout,
    QComboBox, QListWidgetItem, QMessageBox,
    QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog
from .translation_service import TranslationService
from .llm_service import LanguageModelService
from .data_handler import DataHandler
import random
import json
import os

api_token = os.getenv('HUGGINGFACE_API_TOKEN')

class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Language Flashcards")

        self.language_model_service = LanguageModelService(model_name='gpt-4o')
        self.translation_service = TranslationService()
        self.data_handler = DataHandler()
        self.current_words = []  # Store words before saving to file
        self.all_words = []  # Loaded words for practice

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Stacked Widget to switch between screens
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Main Menu Widget
        self.main_menu_widget = self.create_main_menu_widget()
        self.stacked_widget.addWidget(self.main_menu_widget)

        # Input Data Screen
        self.input_data_widget = self.create_input_data_widget()
        self.stacked_widget.addWidget(self.input_data_widget)

        # Practice Screen
        self.practice_widget = self.create_practice_widget()
        self.stacked_widget.addWidget(self.practice_widget)

        # Flashcard Practice Screen
        self.flashcard_widget = self.create_flashcard_widget()
        self.stacked_widget.addWidget(self.flashcard_widget)

        # Show Main Menu
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)

    def create_main_menu_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Main Menu Buttons
        self.input_data_button = QPushButton("Input Data")
        self.practice_button = QPushButton("Practice")

        self.input_data_button.clicked.connect(self.show_input_data)
        self.practice_button.clicked.connect(self.show_practice)

        layout.addWidget(self.input_data_button)
        layout.addWidget(self.practice_button)

        return widget

    def show_input_data(self):
        self.stacked_widget.setCurrentWidget(self.input_data_widget)

    def show_practice(self):
        self.update_source_list()
        self.stacked_widget.setCurrentWidget(self.practice_widget)

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)

    def create_input_data_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Back button to return to main menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_menu)
        layout.addWidget(back_button)

        # Source Name Input
        self.source_name_input = QLineEdit()
        self.source_name_input.setPlaceholderText("Enter source name (e.g., book, website)")
        layout.addWidget(QLabel("Source Name:"))
        layout.addWidget(self.source_name_input)

        # Lesson Title Input
        self.lesson_title_input = QLineEdit()
        self.lesson_title_input.setPlaceholderText("Enter lesson title or CSV file name")
        layout.addWidget(QLabel("Lesson Title:"))
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

        return widget

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

        # Update practice source selector
        self.practice_source_selector.clear()
        self.practice_source_selector.addItems(self.data_handler.get_sources())

    def create_practice_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Back button to return to main menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_menu)
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
        self.start_practice_button.clicked.connect(self.start_practice)
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

        return widget

    def update_source_list(self):
        self.practice_source_selector.clear()
        self.practice_source_selector.addItems(self.data_handler.get_sources())
        self.update_file_list()

    def update_file_list(self):
        self.file_list.clear()
        source_name = self.practice_source_selector.currentText()
        if source_name:
            files = self.data_handler.get_csv_files(source_name)
            self.file_list.addItems(files)

    def start_practice(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            self.all_words = self.data_handler.load_words(source_name, selected_files)
            if not self.all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Get Ultra Mode setting
            self.ultra_mode_enabled = self.ultra_mode_checkbox.isChecked()
            # Start practice
            self.show_flashcard()
        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")

    def select_word_based_on_quotient(self):
        # Calculate total weight
        total_weight = sum(word['quotient'] for word in self.all_words)
        if total_weight == 0:
            total_weight = 1.0  # To avoid division by zero
        weights = [word['quotient'] / total_weight for word in self.all_words]

        # Use random.choices to select one word
        selected_word = random.choices(self.all_words, weights=weights, k=1)[0]
        return selected_word

    def create_flashcard_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Back button to return to main menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.exit_practice)
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

        return widget

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
        if self.ultra_mode_enabled:
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
        self.stacked_widget.setCurrentWidget(self.flashcard_widget)

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

    def exit_practice(self):
        # Return to main menu
        self.show_main_menu()

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

    def start_gap_test(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            self.all_words = self.data_handler.load_words(source_name, selected_files)
            if not self.all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Start gap test
            self.generate_gap_text()
        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")

    def generate_gap_text(self):
        # Get the list of words from the lesson
        vocabulary_words = [word['original'] for word in self.all_words]
        target_language = self.all_words[0]['source_language']
        prompt = (
            f"Write a coherent text in {target_language} that includes minimum 5 to maximum 10 of the following words or phrases:\n"
            f"{', '.join(vocabulary_words)}.\n"
            f"Replace these words with blanks '____' in the text."
            f"Return the response in json format, with the key 'gap_text' and the value as your text with the gaps. The key 'words' should contain a list of the words that should be filled in the blanks in the order of the list."
            f"An example response from you would be: {'{"gap_text": "This is a ____ example.", "words": ["great"]}'}. Make sure it is always in this format"
            f"Please note that the text should be coherent and make sense. The sentences should be more or less related to each other."
        )

        try:
            gap_text = self.language_model_service.generate_text(prompt)
            print(gap_text)
            self.display_gap_test(gap_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate gap text: {e}")

    def display_gap_test(self, gap_text):
        gap_text = json.loads(gap_text)
        # Create a new widget for the gap test
        self.gap_test_widget = QWidget()
        layout = QVBoxLayout(self.gap_test_widget)

        # Back button to return to practice menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_practice)
        layout.addWidget(back_button)

        # Display the gap text
        self.gap_text_label = QLabel(gap_text.get("gap_text", ""))
        self.gap_text_label.setWordWrap(True)
        layout.addWidget(self.gap_text_label)

        # Create input fields for each blank
        self.gap_inputs = []
        blanks_count = gap_text.get("gap_text", "").count('____')
        for i in range(blanks_count):
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Word for blank {i+1}")
            layout.addWidget(input_field)
            self.gap_inputs.append(input_field)

        # Submit button
        submit_button = QPushButton("Submit Answers")
        submit_button.clicked.connect(lambda: self.submit_gap_test_answers(gap_text.get("words", [])))
        layout.addWidget(submit_button)

        # Switch to the gap test widget
        self.stacked_widget.addWidget(self.gap_test_widget)
        self.stacked_widget.setCurrentWidget(self.gap_test_widget)

    def submit_gap_test_answers(self, correct_words):
        # Collect user inputs
        user_answers = [input_field.text().strip() for input_field in self.gap_inputs]

        # Compare and provide feedback
        feedback_messages = []
        for i, (user_answer, correct_word) in enumerate(zip(user_answers, correct_words)):
            if user_answer.lower() == correct_word.lower():
                feedback_messages.append(f"Blank {i+1}: Correct!")
            else:
                feedback_messages.append(f"Blank {i+1}: Incorrect. Correct word is '{correct_word}'.")

        # Display feedback
        feedback_text = '\n'.join(feedback_messages)
        QMessageBox.information(self, "Results", feedback_text)

        # Return to the practice menu
        self.stacked_widget.setCurrentWidget(self.practice_widget)

    def start_writing_assignment(self):
        selected_items = self.file_list.selectedItems()
        source_name = self.practice_source_selector.currentText()

        if not source_name:
            QMessageBox.warning(self, "No Source Selected", "Please select a source.")
            return

        if selected_items:
            selected_files = [item.text() for item in selected_items]
            # Load words from selected files
            self.all_words = self.data_handler.load_words(source_name, selected_files)
            if not self.all_words:
                QMessageBox.warning(self, "No Words", "Selected lessons contain no words.")
                return
            # Start writing assignment
            self.generate_writing_prompt()
        else:
            QMessageBox.warning(self, "No Lessons Selected", "Please select at least one lesson to practice.")

    def generate_writing_prompt(self):
        # Get the list of words from the lesson
        vocabulary_words = [word['original'] for word in self.all_words]
        target_language = self.all_words[0]['source_language']
        prompt = (
            f"Provide a writing assignment topic in {target_language} that relates to these words:\n"
            f"{', '.join(vocabulary_words)}.\n"
            f"The topic should encourage the use of these words."
        )

        try:
            writing_prompt = self.language_model_service.generate_text(prompt)
            self.display_writing_assignment(writing_prompt)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate writing prompt: {e}")

    def display_writing_assignment(self, writing_prompt):
        # Create a new widget for the writing assignment
        self.writing_assignment_widget = QWidget()
        layout = QVBoxLayout(self.writing_assignment_widget)

        # Back button to return to practice menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_practice)
        layout.addWidget(back_button)

        # Display the writing prompt
        self.writing_prompt_label = QLabel(writing_prompt)
        self.writing_prompt_label.setWordWrap(True)
        layout.addWidget(self.writing_prompt_label)

        # Text area for user's writing
        self.user_text_edit = QTextEdit()
        layout.addWidget(self.user_text_edit)

        # Submit button
        submit_button = QPushButton("Submit Writing")
        submit_button.clicked.connect(self.submit_writing)
        layout.addWidget(submit_button)

        # Switch to the writing assignment widget
        self.stacked_widget.addWidget(self.writing_assignment_widget)
        self.stacked_widget.setCurrentWidget(self.writing_assignment_widget)

    def submit_writing(self):
        user_text = self.user_text_edit.toPlainText().strip()
        if not user_text:
            QMessageBox.warning(self, "Input Error", "Please write something before submitting.")
            return

        target_language = self.all_words[0]['source_language']
        prompt = (
            f"As a language tutor, please correct the following text in {target_language} and provide feedback:\n\n"
            f"{user_text}\n\n"
            f"Identify any mistakes and suggest improvements."
        )

        try:
            feedback = self.language_model_service.generate_text(prompt, max_length=500)
            self.display_writing_feedback(feedback)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get feedback: {e}")

    def display_writing_feedback(self, feedback):
        # Create a new widget for the feedback
        self.feedback_widget = QWidget()
        layout = QVBoxLayout(self.feedback_widget)

        # Back button to return to practice menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_practice)
        layout.addWidget(back_button)

        # Display the feedback
        feedback_label = QLabel(feedback)
        feedback_label.setWordWrap(True)
        layout.addWidget(feedback_label)

        # Switch to the feedback widget
        self.stacked_widget.addWidget(self.feedback_widget)
        self.stacked_widget.setCurrentWidget(self.feedback_widget)
