import re
import string
import requests
import nltk

# Initialize porter stemmer
ps = nltk.stem.PorterStemmer()


class Clean:
    def clean(self, text):
        text = self.remove_js(text)
        text = self.remove_illegal_chars(text)
        text = self.make_lowercase(text)
        text = self.britishize(text)
        text = self.tokenize(text)
        text = self.stem(text)

        return text

    def remove_js(self, text):
        # Find first occurance of javascript code
        js_start = text.find('//<![CDATA')

        # While we can find the start of javascript code, find the end
        while js_start != -1:
            js_end = text.find('//]]>', js_start)

            # If no end, we won't know where to stop deleting, so just ignore it
            if js_end == -1:
                break

            # Remove the code through string splicing
            text = text[:js_start] + text[js_end + len('//]]>'):]

            # Find next occurance of javascript
            js_start = text.find('//<![CDATA')

        return text

    # Changes American english to British english
    def britishize(self, text):
        url = "https://raw.githubusercontent.com/hyperreality/American-British-English-Translator/master/data/american_spellings.json"
        american_to_british_dict = requests.get(url).json()

        for american_spelling, british_spelling in american_to_british_dict.items():
            text = text.replace(american_spelling, british_spelling)

        return text

    def remove_illegal_chars(self, text):
        # Remove punctuations
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove all non alphanumeric characters and punctuation

        text = re.sub("[^0-9a-zA-Z]+", " ", text)

        return text

    def make_lowercase(self, text):
        # Convert text to lower case
        text = text.lower()

        return text

    def tokenize(self, text):
        text = nltk.word_tokenize(text)  # Tokenize by word

        return text

    def stem(self, text):
        text = [ps.stem(word) for word in text]  # Stem every word

        return text
