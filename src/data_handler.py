import pandas as pd
import os

class DataHandler:
    def __init__(self):
        self.base_data_dir = "data"
        os.makedirs(self.base_data_dir, exist_ok=True)
        self.file_word_map = {}  # Map words to filenames

    def save_words(self, source_name, lesson_title, words_list):
        source_dir = os.path.join(self.base_data_dir, source_name)
        os.makedirs(source_dir, exist_ok=True)
        csv_file = os.path.join(source_dir, f"{lesson_title}.csv")
        df = pd.DataFrame(words_list)
        df.to_csv(csv_file, index=False)

    def get_sources(self):
        # List all subdirectories in the base data directory
        sources = [d for d in os.listdir(self.base_data_dir) if os.path.isdir(os.path.join(self.base_data_dir, d))]
        return sources

    def get_csv_files(self, source_name):
        source_dir = os.path.join(self.base_data_dir, source_name)
        if not os.path.exists(source_dir):
            return []
        files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]
        return files

    def load_words(self, source_name, filenames):
        words = []
        for filename in filenames:
            csv_file = os.path.join(self.base_data_dir, source_name, filename)
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                word_entries = df.to_dict('records')
                for entry in word_entries:
                    # Add filename and source name to entry to track where it came from
                    entry['filename'] = filename
                    entry['source_name'] = source_name
                    words.append(entry)
        return words

    def update_word(self, word_entry):
        # Update the word in its corresponding CSV file
        filename = word_entry.get('filename')
        source_name = word_entry.get('source_name')
        if not filename or not source_name:
            return  # Cannot update without filename and source name
        csv_file = os.path.join(self.base_data_dir, source_name, filename)
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            # Find the index of the word to update
            condition = (
                (df['original'] == word_entry['original']) &
                (df['translation'] == word_entry['translation'])
            )
            indices = df.index[condition]
            if not indices.empty:
                index = indices[0]
                df.at[index, 'quotient'] = word_entry['quotient']
                df.to_csv(csv_file, index=False)
