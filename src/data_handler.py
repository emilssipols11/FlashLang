# src/data_handler.py

import pandas as pd
import os

class DataHandler:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.file_word_map = {}  # Map words to filenames

    def save_words(self, lesson_title, words_list):
        csv_file = os.path.join(self.data_dir, f"{lesson_title}.csv")
        df = pd.DataFrame(words_list)
        df.to_csv(csv_file, index=False)

    def get_csv_files(self):
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        return files

    def load_words(self, filenames):
        words = []
        for filename in filenames:
            csv_file = os.path.join(self.data_dir, filename)
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                word_entries = df.to_dict('records')
                for entry in word_entries:
                    # Add filename to entry to track where it came from
                    entry['filename'] = filename
                    words.append(entry)
        return words

    def update_word(self, word_entry):
        # Update the word in its corresponding CSV file
        filename = word_entry.get('filename')
        if not filename:
            return  # Cannot update without filename
        csv_file = os.path.join(self.data_dir, filename)
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
