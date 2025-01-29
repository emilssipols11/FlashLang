import os
import openai

class LanguageModelService:
    def __init__(self, model_name):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model_name = model_name  # e.g., "gpt-3.5-turbo"

    def generate_text(self, prompt, max_length=200):
        response = openai.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_length,
            temperature=0.7,
            top_p=0.95
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
