from rake_nltk import Rake

class KeywordExtractor:
    def __init__(self, language='german'):
        self.language = language

    def extract_keywords(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        r = Rake(language=self.language)
        r.extract_keywords_from_text(text)
        keywords = r.get_ranked_phrases()

        return keywords

    def save_keywords(self, keywords, output_file_path):
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(keywords))

        print("Step 4 --> Keywords extracted and saved successfully!")
