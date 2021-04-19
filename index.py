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

# Import own files
from clean import Clean

# Global definitions
csv.field_size_limit(2**30)

# Create instances of imported classes
cleaner = Clean()


def usage():
    print(
        "Usage: "
        + sys.argv[0]
        + " -i dataset-file -d dictionary-file -p postings-file"
    )


def build_index(in_file, out_dict, out_postings):
    """
    Build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("Indexing...")

    # Read in documents to index
    with open(in_file, newline='', encoding='utf-8-sig') as csvfile:
        # Create a dictionary to store the mapping of docIDs as incrementing integers, e.g. docID 1 --> docID 245234524 
        doc_id_downsized = 1
        doc_ids_dict = {}

        # containers to perform tf-idf
        terms = []  # Keep track of unique terms in document
        dictionary = {} 
        doc_lengths = {}

        # Start progress bar. max obtained from reading in the excel file and checking number of rows 
        indexing_progress_bar = Bar("Loading in documents and indexing", max=17153)

        # Read in CSV dataset and remove headers from consideration
        csv_reader = csv.reader(csvfile)
        next(csv_reader, None)  

        # Iterate over each row, and each row represents a document 
        for row in csv_reader:
            # dictionary to contain the five fields of every row 
            data_row = {}
            data_row["doc_id"] = row[0]
            data_row["title"] = row[1]
            data_row["content"] = row[2]
            data_row["date_posted"] = row[3] 
            data_row["court"] = row[4]

            # map large doc_id to smaller doc_id to save space in our postings list
            doc_ids_dict[doc_id_downsized] = int(data_row["doc_id"])
            data_row["doc_id"] = doc_id_downsized
            doc_id_downsized += 1

            # we do not want the date_posted since it's not important for our querying hence we will simply ignore it          

            # process the three text fields - this will effectively create our tokenized version of the original text
            for key in ["title", "content", "court"]:
                data_row[key] = cleaner.clean(data_row[key])

            # we ignore zones since there is no way for the user to enter a phrasal query and specify the zone
            # if we consider zoning, it will effectively be trying to "guess" which zone the token is in
            # therefore we just combine the various fields into "text"
            data_row["text"] = data_row["title"] + data_row["content"] + data_row["court"]

            # start creating the dictionary and the postings list by checking every word in the document (exclude date)
            for position, word in enumerate(data_row["text"]):
                # Track unique terms
                terms.append(word)

                # If new term, add term to dictionary and initialize new postings list for that term
                if word not in dictionary:
                    dictionary[word] = {}  # Initialize new postings list

                    # Update document freq for this new word to 1
                    dictionary[word]["doc_freq"] = 1

                    # Create an empty posting list
                    dictionary[word]["postings_list"] = []

                    # create a new entry for the posting list
                    new_posting = {
                        "doc_id": data_row["doc_id"],
                        "term_freq": 1,
                        "positions": [position]
                        }

                    # Add term freq to posting
                    dictionary[word]["postings_list"].append(new_posting)

                # If term in dictionary, check if document for that term is already inside
                else:
                    # If doc_id already exists in postings list
                    if dictionary[word]["postings_list"][-1]["doc_id"] == data_row["doc_id"]:
                        # increment term frequency in doc
                        dictionary[word]["postings_list"][-1]["term_freq"] += 1
                        
                        # append the position delta into the positions array 
                        last_position = dictionary[word]["postings_list"][-1]["positions"][-1]
                        dictionary[word]["postings_list"][-1]["positions"].append(position - last_position)

                    # Create new document in postings list and set term frequency to 1
                    else:
                        # create a new entry for the posting list
                        new_posting = {
                            "doc_id": data_row["doc_id"],
                            "term_freq": 1,
                            "positions": [position]
                            }

                        # Add term freq to posting
                        dictionary[word]["postings_list"].append(new_posting)

                        # Update document frequency
                        dictionary[word]["doc_freq"] += 1

            print(data_row)
            
            # Make set only unique terms
            terms = list(set(terms))

            # Calculate document length (sqrt of all weights squared)
            doc_length = 0
            for term in terms:
                # If term appears in doc, calculate its weight in the document W(t,d)
                if dictionary[term]["postings_list"][-1]["doc_id"] == data_row["doc_id"]:
                    term_weight_in_doc = 0
                    # If term frequency is more than 0 then we add to the weight
                    if dictionary[term]["postings_list"][-1]["term_freq"] > 0:
                        # Take the log frequecy weight of term t in doc
                        # Note that we ignore inverse document frequency for documents
                        term_weight_in_doc = 1 + math.log(
                            dictionary[term]["postings_list"][-1]["term_freq"], 10
                        )

                    # Add term weight in document squared to total document length
                    doc_length += term_weight_in_doc ** 2

            # Take sqrt of doc_length for final doc length
            doc_length = math.sqrt(doc_length)

        # Add final doc_length to doc_lengths dictionary
        doc_lengths[data_row["doc_id"]] = doc_length

        print(dictionary)
        print(doc_lengths)


        # Update progress bar
        indexing_progress_bar.next()

        # Progress bar finish
        indexing_progress_bar.finish()

    print("Documents loaded. Writing out total collection size to disk...")

    # # Write out collection size (number of documents) to disk
    # write_collection_size_to_disk(len(doc_ids), out_postings)

    # print("Total collection size is {}.".format(len(doc_ids)))

    # # Initialize porter stemmer
    # ps = nltk.stem.PorterStemmer()

    # print("Stemming terms and tracking document lengths...")

    # # Track progress while indexing
    # processing_bar = Bar("Processing documents", max=len(doc_ids))

    # # Create a dictionary of terms and another dictionary for document lengths
    # dictionary = {}
    # doc_lengths = {}

    # # Process every document and create a dictionary of posting lists
    # for doc_id in doc_ids:
    #     # Open the document file
    #     f = open(os.path.join(in_file, str(doc_id)), "r")

    #     text = f.read()  # Read the document in fulltext
    #     text = text.lower()  # Convert text to lower case
    #     sentences = nltk.sent_tokenize(text)  # Tokenize by sentence

    #     terms = []  # Keep track of unique terms in document

    #     for sentence in sentences:
    #         words = nltk.word_tokenize(sentence)  # Tokenize by word

    #         words = [
    #             w for w in words if w not in string.punctuation
    #         ]  # clean out isolated punctuations
    #         words_stemmed = [ps.stem(w) for w in words]  # Stem every word

    #         for word in words_stemmed:
    #             # Track unique terms
    #             terms.append(word)

    #             # If new term, add term to dictionary and initialize new postings list for that term
    #             if word not in dictionary:
    #                 dictionary[word] = {}  # Initialize new postings list

    #                 # Update document freq for this new word to 1
    #                 dictionary[word]["doc_freq"] = 1

    #                 # Create an empty posting list
    #                 dictionary[word]["postings_list"] = []

    #                 # Add term freq to posting
    #                 dictionary[word]["postings_list"].append([doc_id, 1])
    #             # If term in dictionary, check if document for that term is already inside
    #             else:
    #                 # If doc_id already exists in postings list, simply increment term frequency in doc
    #                 if dictionary[word]["postings_list"][-1][0] == doc_id:
    #                     dictionary[word]["postings_list"][-1][1] += 1
    #                 # Create new document in postings list and set term frequency to 1
    #                 else:
    #                     # Add term freq to posting
    #                     dictionary[word]["postings_list"].append([doc_id, 1])

    #                     # Update document frequency
    #                     dictionary[word]["doc_freq"] += 1

    #     # Make set only unique terms
    #     terms = list(set(terms))

    #     # Calculate document length (sqrt of all weights squared)
    #     doc_length = 0
    #     for term in terms:
    #         # If term appears in doc, calculate its weight in the document W(t,d)
    #         if dictionary[term]["postings_list"][-1][0] == doc_id:
    #             term_weight_in_doc = 0
    #             # If term frequency is more than 0 then we add to the weight
    #             if dictionary[term]["postings_list"][-1][1] > 0:
    #                 # Take the log frequecy weight of term t in doc
    #                 # Note that we ignore inverse document frequency for documents
    #                 term_weight_in_doc = 1 + math.log(
    #                     dictionary[term]["postings_list"][-1][1], 10
    #                 )

    #             # Add term weight in document squared to total document length
    #             doc_length += term_weight_in_doc ** 2

    #     # Take sqrt of doc_length for final doc length
    #     doc_length = math.sqrt(doc_length)

    #     # Add final doc_length to doc_lengths dictionary
    #     doc_lengths[doc_id] = doc_length

    #     # Close file and update progress bar
    #     f.close()
    #     processing_bar.next()

    # # Update progress bar
    # processing_bar.finish()
    # print("Pre-processing complete. Writing document lengths to disk...")

    # # Save doc_lengths to disk
    # write_doc_lengths_to_disk(doc_lengths)

    # print("{} document lengths written to disk.".format(len(doc_ids)))

    # # Create dictionary of K:V {term: Address to postings list of that term}
    # term_dict = {}

    # # Track progress while indexing
    # print("Indexing terms and saving each postings list to disk...")
    # indexing_bar = Bar("Indexing terms", max=len(dictionary.keys()))

    # # For each term, split into term_dict and PostingsList, and write out to their respective files
    # for term in dictionary.keys():
    #     # Write PostingsList for each term out to disk and get its address
    #     ptr = write_postings_list_to_disk(dictionary[term], out_postings)

    #     # Update term_dict with the address of the PostingsList for that term
    #     term_dict[term] = ptr

    #     # Update progress bar
    #     indexing_bar.next()

    # # Update progress bar
    # indexing_bar.finish()
    # print("Posting lists saved to disk.")

    # # Track progress while indexing
    # print("Saving term dictionary to disk...")

    # # Now the term_dict has the pointers to each terms' PostingsList
    # # Write out the dictionary to the dictionary file on disk
    # write_dictionary_to_disk(term_dict, out_dict)

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
