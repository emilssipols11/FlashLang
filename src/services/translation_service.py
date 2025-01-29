from translate import Translator

class TranslationService:
    def __init__(self):
        # Initialize available languages with language codes
        self.available_languages = {
            'English': 'en',
            'Dutch': 'nl',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Chinese (Simplified)': 'zh',
            'Japanese': 'ja',
            'Russian': 'ru',
            'Arabic': 'ar',
            'Portuguese': 'pt',
            'Hindi': 'hi',
        }

    def get_supported_languages(self):
        return list(self.available_languages.keys())

    def is_single_word(self, text):
        return len(text.strip().split()) == 1

    def translate_word(self, word, source_language_name, target_language_name):
        source_lang_code = self.available_languages.get(source_language_name)
        target_lang_code = self.available_languages.get(target_language_name)

        if not source_lang_code or not target_lang_code:
            print("Unsupported language selected.")
            return None

        if self.is_single_word(word):
            translation = self.translate_single_word(word, source_lang_code, target_lang_code)
            if translation is None:
                translation = self.translate_multiple_words(word, source_lang_code, target_lang_code)
        else:
            translation = self.translate_multiple_words(word, source_lang_code, target_lang_code)

        return translation

    def translate_single_word(self, word, source_lang_code, target_lang_code):
        try:
            translator = Translator(from_lang=source_lang_code, to_lang=target_lang_code)
            return translator.translate(word)
        except Exception as e:
            print(f"Error in single word translation: {e}")
            return None

    def translate_multiple_words(self, text, source_lang_code, target_lang_code):
        try:
            translator = Translator(from_lang=source_lang_code, to_lang=target_lang_code)
            return translator.translate(text)
        except Exception as e:
            print(f"Error in multiple words translation: {e}")
            return None
