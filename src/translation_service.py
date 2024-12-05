import requests
from libretranslatepy import LibreTranslateAPI

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
            # Add more languages as needed
        }
        # Initialize LibreTranslate API client
        self.api_url = 'https://libretranslate.com/'  # Use the public instance or your own URL
        self.translator = LibreTranslateAPI(self.api_url)

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
            # Use dictionary API for single words
            translation = self.translate_single_word(word, source_lang_code, target_lang_code)
            if translation is None:
                # Fall back to translation API if dictionary API fails
                translation = self.translate_multiple_words(word, source_lang_code, target_lang_code)
        else:
            # Use translation API for multiple words
            translation = self.translate_multiple_words(word, source_lang_code, target_lang_code)

        return translation

    def translate_single_word(self, word, source_lang_code, target_lang_code):
        # The Free Dictionary API supports only English definitions
        # We'll use it if either source or target language is English
        if source_lang_code == 'en' or target_lang_code == 'en':
            try:
                language_code = 'en'  # API supports only English
                url = f"https://api.dictionaryapi.dev/api/v2/entries/{language_code}/{word}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Extract the meanings
                    meanings = data[0].get('meanings', [])
                    for meaning in meanings:
                        # Check if the part of speech matches (optional)
                        definitions = meaning.get('definitions', [])
                        for definition in definitions:
                            # Return the first definition or translation
                            return definition.get('definition')
                    return None  # No definition found
                else:
                    print(f"Dictionary API Error: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error fetching definition: {e}")
                return None
        else:
            # Dictionary API doesn't support other languages; return None
            return None

    def translate_multiple_words(self, text, source_lang_code, target_lang_code):
        try:
            translation = self.translator.translate(
                q=text,
                source=source_lang_code,
                target=target_lang_code
            )
            return translation
        except Exception as e:
            print(f"Translation Error: {e}")
            return None
