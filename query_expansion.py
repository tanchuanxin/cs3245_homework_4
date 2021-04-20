import csv
import nltk
from nltk.corpus import wordnet
import time
import gensim
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from progress.bar import Bar
from progress.spinner import Spinner

# Import own files
from clean import Clean

cleaner = Clean()

# Increase csv field size limit
csv.field_size_limit(2 ** 30)

NUM_DOCS = 17153  # for progress bar purposes only

sentences = []
with open("dataset.csv", newline='', encoding='utf-8-sig') as csvfile:

    #Start time
    start = time.time()

    # Start progress bar. max obtained from reading in the excel file and checking number of rows
    indexing_progress_bar = Bar(
    "Reading in documents to train Word2Vec Model", max=NUM_DOCS)

    # Read in CSV dataset and remove headers from consideration
    csv_reader = csv.reader(csvfile)
    next(csv_reader, None)

    # Iterate over each row, and each row represents a document
    for row in csv_reader:

        sentences.append(cleaner.clean(row[2]))

        # Update progress bar
        indexing_progress_bar.next()
    
    #End time
    end = time.time()

    #Time taken
    print(f"Time taken is {(start-end):.2f}s")

# Progress bar finish
indexing_progress_bar.finish()
print("Training complete. Saving model...")

model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

model.wv.save_word2vec_format('model.kv', binary=True)

print("Model saved.")


# wordvectors = KeyedVectors.load_word2vec_format('model.kv',binary=True)

# def query_expansion(free_texts,wordvectors):
#     synonym_dic = {}
#     for word in free_texts:
#         synonyms = []
#         print(word)
#         refined_synonyms = []
#         for syn in wordnet.synsets(word):
#             for l in syn.lemmas():
#                 synonyms.append(l.name())
#         if set(synonyms) != set():
#             for synonym in set(synonyms):
#                 synonym = cleaner.clean(synonym)
#                 refined_synonyms.append(synonym)
#             for s in refined_synonyms:
#                 if s[0] in wordvectors and word in wordvectors and s[0] != word:
#                     if word in synonym_dic.keys():
#                         synonym_dic[word][s[0]] = wordvectors.similarity(word,s[0])
#                     else:
#                         synonym_dic[word] = {}
#                         synonym_dic[word][s[0]] = wordvectors.similarity(word,s[0])
#     return synonym_dic
