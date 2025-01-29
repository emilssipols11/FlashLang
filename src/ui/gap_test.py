from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
import json
import re


class GapTest(QWidget):
    def __init__(self, stacked_widget, language_model_service):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.language_model_service = language_model_service
        self.all_words = None  # List of all words in the lesson
        self.gap_text_data = None  # Stores gap text and correct answers
        self.gap_inputs = []  # List of input fields for blanks

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.practice_screen)

    def set_lesson_data(self, lesson_data):
        self.all_words = lesson_data
        self.generate_gap_test()

    def extract_json_from_response(self, response_text):
        try:
            # Match content between curly braces (handles cases with backticks or extra text)
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                json_content = match.group(0)  # Extract matched JSON text
                return json_content  # Parse as JSON
            else:
                raise ValueError("No valid JSON found in the response.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")
    
    def generate_gap_test(self):
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
            "Return only the json response. Do not include any other text. it should start with '{' and end with '}'"
        )

        try:
            gap_text = self.language_model_service.generate_text(prompt)
            gap_text = self.extract_json_from_response(gap_text)
            self.display_gap_test(gap_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate gap text: {e}")

    def display_gap_test(self, gap_text):
        gap_text = json.loads(gap_text)
        layout = QVBoxLayout(self)

        # Back button to return to practice menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
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
        self.setLayout(layout)

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
        self.go_back()
