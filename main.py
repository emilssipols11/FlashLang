# # main.py

# from src.ui import FlashcardApp
# import sys
# from PySide6.QtWidgets import QApplication

# def main():
#     app = QApplication(sys.argv)
#     window = FlashcardApp()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()
from PySide6.QtWidgets import QApplication, QStackedWidget
from src.ui.main_menu import MainMenu
from src.ui.input_data import InputData
from src.ui.practice import Practice
from src.ui.flashcard import Flashcard
from src.ui.gap_test import GapTest
from src.ui.writing_assignment import WritingAssignment
from src.services.llm_service import LanguageModelService

app = QApplication([])
stacked_widget = QStackedWidget()
language_model_service = LanguageModelService("gpt-4o")

# Initialize screens
main_menu = MainMenu(stacked_widget)
input_data = InputData(stacked_widget)
practice = Practice(stacked_widget)
flashcard = Flashcard(stacked_widget)
gap_test = GapTest(stacked_widget, language_model_service)
writing_assignment = WritingAssignment(stacked_widget, language_model_service)

# Add to stacked widget
stacked_widget.main_menu_screen = main_menu
stacked_widget.input_data_screen = input_data
stacked_widget.practice_screen = practice
stacked_widget.flashcard_screen = flashcard
stacked_widget.gap_test_screen = gap_test
stacked_widget.writing_assignment_screen = writing_assignment

stacked_widget.addWidget(main_menu)
stacked_widget.addWidget(input_data)
stacked_widget.addWidget(practice)
stacked_widget.addWidget(flashcard)
stacked_widget.addWidget(gap_test)
stacked_widget.addWidget(writing_assignment)

stacked_widget.setCurrentWidget(main_menu)
stacked_widget.show()
app.exec()
