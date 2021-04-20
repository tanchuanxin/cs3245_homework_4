import csv
import nltk
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
        # append title, content and court for training
        data = row[1] +row[2] +row[4]
        sentences.append(cleaner.clean(data))

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

