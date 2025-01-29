from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
)


class WritingAssignment(QWidget):
    def __init__(self, stacked_widget, language_model_service):
        super().__init__()
        self.all_words = None
        self.stacked_widget = stacked_widget
        self.language_model_service = language_model_service

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.practice_screen)

    def set_lesson_data(self, all_words):
        self.all_words = all_words
        self.generate_writing_prompt()

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
        layout = QVBoxLayout(self)

        # Back button to return to practice menu
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
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

        self.setLayout(layout)

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
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        # Display the feedback
        feedback_label = QLabel(feedback)
        feedback_label.setWordWrap(True)
        layout.addWidget(feedback_label)

        # Switch to the feedback widget
        self.stacked_widget.addWidget(self.feedback_widget)
        self.stacked_widget.setCurrentWidget(self.feedback_widget)
