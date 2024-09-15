# src/translation_service.py

from translate import Translator

class TranslationService:
    def __init__(self):
        # Initialize the translator
        self.available_languages = {
            'English': 'en',
            'Dutch': 'nl',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Chinese': 'zh',
            'Japanese': 'ja',
            'Russian': 'ru',
            'Arabic': 'ar',
            'Portuguese': 'pt',
            'Hindi': 'hi',
            'Dutch': 'nl',
            # Add more languages as needed
        }

    def get_supported_languages(self):
        return list(self.available_languages.keys())

    def translate_word(self, word, source_language_name, target_language_name):
        source_lang_code = self.available_languages.get(source_language_name, 'auto')
        target_lang_code = self.available_languages.get(target_language_name, 'en')
        try:
            translator = Translator(from_lang=source_lang_code, to_lang=target_lang_code)
            translation = translator.translate(word)
            return translation
        except Exception as e:
            print(f"Translation Error: {e}")
            return None
