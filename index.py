#!/usr/bin/python3
import re
import csv
import nltk
import os
import sys
import getopt
import pickle
import math
import string
from progress.bar import Bar
from progress.spinner import Spinner

# Global definitions
csv.field_size_limit(2**30)


def usage():
    print(
        "Usage: "
        + sys.argv[0]
        + " -i dataset-file -d dictionary-file -p postings-file"
    )


def read_dataset(in_file):
    # Open dataset file
    with open(in_file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        # Create a dictionary to store the data and store all doc_ids
        data = {}
        doc_ids = []

        # Load all data from dataset into the dict
        load_documents_bar = Bar("Loading in documents", max=17153)

        return data


def build_index(in_file, out_dict, out_postings):
    """
    Build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("Indexing...")

    # Read in documents to index
    with open(in_file, newline='', encoding='utf-8') as csvfile:
        # Create a dictionary to store the data and store all doc_ids
        data = {}
        doc_ids = []

        # Start progress bar
        indexing_progress_bar = Bar("Loading in documents", max=17153)

        # Read in CSV dataset
        csv_reader = csv.reader(csvfile)

        # Iterate over each row
        i = 0
        for row in csv_reader:
            if i < 1:
                print(row)
            i += 1
            # Update progress bar
            indexing_progress_bar.next()

        # Progress bar finish
        indexing_progress_bar.finish()

    print("Documents loaded. Writing out total collection size to disk...")

    # Write out collection size (number of documents) to disk
    write_collection_size_to_disk(len(doc_ids), out_postings)

    print("Total collection size is {}.".format(len(doc_ids)))

    # Initialize porter stemmer
    ps = nltk.stem.PorterStemmer()

    print("Stemming terms and tracking document lengths...")

    # Track progress while indexing
    processing_bar = Bar("Processing documents", max=len(doc_ids))

    # Create a dictionary of terms and another dictionary for document lengths
    dictionary = {}
    doc_lengths = {}

    # Process every document and create a dictionary of posting lists
    for doc_id in doc_ids:
        # Open the document file
        f = open(os.path.join(in_file, str(doc_id)), "r")

        text = f.read()  # Read the document in fulltext
        text = text.lower()  # Convert text to lower case
        sentences = nltk.sent_tokenize(text)  # Tokenize by sentence

        terms = []  # Keep track of unique terms in document

        for sentence in sentences:
            words = nltk.word_tokenize(sentence)  # Tokenize by word

            words = [
                w for w in words if w not in string.punctuation
            ]  # clean out isolated punctuations
            words_stemmed = [ps.stem(w) for w in words]  # Stem every word

            for word in words_stemmed:
                # Track unique terms
                terms.append(word)

                # If new term, add term to dictionary and initialize new postings list for that term
                if word not in dictionary:
                    dictionary[word] = {}  # Initialize new postings list

                    # Update document freq for this new word to 1
                    dictionary[word]["doc_freq"] = 1

                    # Create an empty posting list
                    dictionary[word]["postings_list"] = []

                    # Add term freq to posting
                    dictionary[word]["postings_list"].append([doc_id, 1])
                # If term in dictionary, check if document for that term is already inside
                else:
                    # If doc_id already exists in postings list, simply increment term frequency in doc
                    if dictionary[word]["postings_list"][-1][0] == doc_id:
                        dictionary[word]["postings_list"][-1][1] += 1
                    # Create new document in postings list and set term frequency to 1
                    else:
                        # Add term freq to posting
                        dictionary[word]["postings_list"].append([doc_id, 1])

                        # Update document frequency
                        dictionary[word]["doc_freq"] += 1

        # Make set only unique terms
        terms = list(set(terms))

        # Calculate document length (sqrt of all weights squared)
        doc_length = 0
        for term in terms:
            # If term appears in doc, calculate its weight in the document W(t,d)
            if dictionary[term]["postings_list"][-1][0] == doc_id:
                term_weight_in_doc = 0
                # If term frequency is more than 0 then we add to the weight
                if dictionary[term]["postings_list"][-1][1] > 0:
                    # Take the log frequecy weight of term t in doc
                    # Note that we ignore inverse document frequency for documents
                    term_weight_in_doc = 1 + math.log(
                        dictionary[term]["postings_list"][-1][1], 10
                    )

                # Add term weight in document squared to total document length
                doc_length += term_weight_in_doc ** 2

        # Take sqrt of doc_length for final doc length
        doc_length = math.sqrt(doc_length)

        # Add final doc_length to doc_lengths dictionary
        doc_lengths[doc_id] = doc_length

        # Close file and update progress bar
        f.close()
        processing_bar.next()

    # Update progress bar
    processing_bar.finish()
    print("Pre-processing complete. Writing document lengths to disk...")

    # Save doc_lengths to disk
    write_doc_lengths_to_disk(doc_lengths)

    print("{} document lengths written to disk.".format(len(doc_ids)))

    # Create dictionary of K:V {term: Address to postings list of that term}
    term_dict = {}

    # Track progress while indexing
    print("Indexing terms and saving each postings list to disk...")
    indexing_bar = Bar("Indexing terms", max=len(dictionary.keys()))

    # For each term, split into term_dict and PostingsList, and write out to their respective files
    for term in dictionary.keys():
        # Write PostingsList for each term out to disk and get its address
        ptr = write_postings_list_to_disk(dictionary[term], out_postings)

        # Update term_dict with the address of the PostingsList for that term
        term_dict[term] = ptr

        # Update progress bar
        indexing_bar.next()

    # Update progress bar
    indexing_bar.finish()
    print("Posting lists saved to disk.")

    # Track progress while indexing
    print("Saving term dictionary to disk...")

    # Now the term_dict has the pointers to each terms' PostingsList
    # Write out the dictionary to the dictionary file on disk
    write_dictionary_to_disk(term_dict, out_dict)

    print("Indexing complete.")


input_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:d:p:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-i":  # input directory
        input_file = a
    elif o == "-d":  # dictionary file
        output_file_dictionary = a
    elif o == "-p":  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if (
    input_file == None
    or output_file_postings == None
    or output_file_dictionary == None
):
    usage()
    sys.exit(2)

build_index(input_file, output_file_dictionary, output_file_postings)
