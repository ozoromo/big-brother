import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer

nltk.download('punkt')
nltk.download('stopwords')


class TextSummarizer:
    def __init__(self):
        self.stemmer = SnowballStemmer("german")
        self.stop_words = set(stopwords.words("german"))

    def summarize_text(self, text):
        sentences = sent_tokenize(text, language='german')
        words = word_tokenize(text, language='german')
        filtered_words = [word for word in words if word.casefold() not in self.stop_words]
        stemmed_words = [self.stemmer.stem(word) for word in filtered_words]
        word_frequencies = nltk.FreqDist(stemmed_words)
        sentence_scores = {}

        for sentence in sentences:
            if "=== SLIDE ===" in sentence:
                continue

            for word in nltk.word_tokenize(sentence.lower(), language='german'):
                if word in word_frequencies:
                    if len(sentence.split(" ")) < 30:
                        if sentence not in sentence_scores:
                            sentence_scores[sentence] = word_frequencies[word]
                        else:
                            sentence_scores[sentence] += word_frequencies[word]

        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        summary_sentences = []
        max_summary_length = len(sentences)

        for i in range(min(max_summary_length, len(sorted_sentences))):
            summary_sentences.append(sorted_sentences[i][0])

        summary = " ".join(summary_sentences)
        return summary

    def summarize_file(self, filename, output_filename):
        with open(filename, encoding="utf8") as file:
            text = file.read()
            summary = self.summarize_text(text)

        with open(output_filename, "w", encoding="utf8") as output_file:
            output_file.write(summary)

        print("Step 3 --> Summary: done")
