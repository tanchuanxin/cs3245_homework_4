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
import time

# Import own files
from clean import Clean
import vb_encoder

# Global definitions
csv.field_size_limit(2 ** 30)

NUM_DOCS = 17153  # for progress bar purposes only
COURT_RANKINGS = {
    3: ['sg court of appeal', 'sg privy council', 'uk house of lords', 'uk supreme court', 'high court of australia', 'ca supreme court'],
    2: ['sg high court', 'singapore international commercial court', 'hk high court', 'hk court of first instance', 'uk crown court', 'uk court of appeal', 'uk high court', 'federal court of australia', 'nsw court of appeal', 'nsw court of criminal appeal', 'nsw supreme court']
}


# Create instances of imported classes
cleaner = Clean()


def usage():
    print(
        "Usage: "
        + sys.argv[0]
        + " -i dataset-file -d dictionary-file -p postings-file"
    )


# Writes out the total number of documents in the collection to the postings file
# This is basically N, to compute inverse document frequency
def write_collection_size_to_disk(collection_size: int, out_postings):
    # Open our postings file
    f_postings = open(out_postings, "wb")

    # Writes out PostingsList for this term to postings file
    pickle.dump(collection_size, f_postings)

    # Close our postings file
    f_postings.close()


# Writes out the length of each document as a dictionary to a file
def write_doc_lengths_to_disk(doc_lengths: dict):
    # Open our document lengths file
    f_doc_lengths = open(
        os.path.join(os.path.dirname(__file__), "doc_lengths.txt"), "wb"
    )

    # Write out document lengths dictionary to the document lengths file
    pickle.dump(doc_lengths, f_doc_lengths)

    # Close the file
    f_doc_lengths.close()


# Takes in a PostingsList for a term and writes it out to our postings file
# Returns an address to the PostingsList on disk
def write_postings_list_to_disk(postings_list: dict, out_postings):
    # Open our postings file
    f_postings = open(out_postings, "wb")

    # Get the byte offset of the final position in our postings file on disk
    # This will be where the PostingsList is appended to
    # Bring the pointer to the very end of the postings file
    f_postings.seek(0, 2)
    pointer = f_postings.tell()

    # Writes out PostingsList for this term to postings file
    pickle.dump(postings_list, f_postings)

    # Close our postings file
    f_postings.close()

    # Return address of PostingsList we just wrote out
    return pointer


# Writes out the term dictionary {term: Address of PostingsList for that term} to disk
def write_dictionary_to_disk(term_dict: dict, out_dict):
    # Open our dictionary file
    f_dict = open(out_dict, "wb")

    # Writes out the term dictionary to dictionary file
    pickle.dump(term_dict, f_dict)

    # Close our dictionary file
    f_dict.close()


# Writes out the metadata to disk (truncated_doc_id: {original_doc_id: n, court: m})
def write_metadata_to_disk(metadata_dict: dict, out_metadata):
    # Open our metadata file
    f_metadata = open(out_metadata, "wb")

    # Writes out the metadata dictionary to metadata file
    pickle.dump(metadata_dict, f_metadata)

    # Close our metadata file
    f_metadata.close()


def build_index(in_file, out_dict, out_postings):
    """
    Build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    # Start time
    start = time.time()
    print("Indexing...")

    # Read in documents to index
    with open(in_file, newline='', encoding='utf-8-sig') as csvfile:
        # Create a dictionary to store the mapping of docIDs as incrementing integers, e.g. docID 1 --> docID 245234524
        doc_id_downsized = 1
        doc_metadata_dict = {}

        # containers to perform tf-idf
        terms = []  # Keep track of unique terms in document
        dictionary = {}
        doc_lengths = {}

        # Start progress bar. max obtained from reading in the excel file and checking number of rows
        indexing_progress_bar = Bar(
            "Loading in documents and indexing", max=NUM_DOCS)

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
            # data_row["date_posted"] = row[3] # we do not want the date_posted since it's not important for our querying hence we will simply ignore it
            data_row["court"] = row[4]

            # map large doc_id to smaller doc_id to save space in our postings list
            doc_metadata_dict[doc_id_downsized] = {}
            doc_metadata_dict[doc_id_downsized]["og_doc_id"] = int(
                data_row["doc_id"])
            data_row["doc_id"] = doc_id_downsized

            # add in the fixed court information into the metadata so as to rank important courts higher subsequently
            # most important courts --> rank 1
            if data_row["court"].lower().rstrip() in COURT_RANKINGS[3]:
                doc_metadata_dict[doc_id_downsized]["court"] = 3
            elif data_row["court"].lower().rstrip() in COURT_RANKINGS[2]:
                doc_metadata_dict[doc_id_downsized]["court"] = 2
            else:
                doc_metadata_dict[doc_id_downsized]["court"] = 1

            # process the three text fields - this will effectively create our tokenized version of the original text
            for key in ["title", "content", "court"]:
                data_row[key] = cleaner.clean(data_row[key])

            # we ignore zones since there is no way for the user to enter a phrasal query and specify the zone
            # if we consider zoning, it will effectively be trying to "guess" which zone the token is in
            # therefore we just combine the various fields into "text"
            data_row["text"] = data_row["title"] + \
                data_row["content"] + data_row["court"]

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
                        dictionary[word]["postings_list"][-1]["positions"].append(
                            position - last_position)

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

            # increment to the next doc_id_downsized
            doc_id_downsized += 1
            
            # Update progress bar
            indexing_progress_bar.next()

    # Progress bar finish
    indexing_progress_bar.finish()
    print("Indexing complete. Saving files...")

    '''##############################################################################################################################################################################
    # save to output files
    ##############################################################################################################################################################################'''

    # Save doc_lengths to disk
    write_doc_lengths_to_disk(doc_lengths)

    print("{} document lengths written to disk.".format(NUM_DOCS))

    # Create dictionary of K:V {term: Address to postings list of that term}
    term_dict = {}

    # Track progress while indexing
    print("Indexing terms and saving each postings list to disk...")
    indexing_bar = Bar("Indexing terms", max=len(dictionary.keys()))

    # For each term, split into term_dict and PostingsList, and write out to their respective files
    for term in dictionary.keys():
        # for each posting in postings list, encode posting's position array
        for postings in dictionary[term]["postings_list"]:
            postings["positions"] = vb_encoder.encode(postings["positions"])
            
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

    # writing out the metadata file, hardcode the filename since it is not part of the original console ocmmand
    write_metadata_to_disk(doc_metadata_dict, "metadata.txt")

    print("Indexing complete.")

    # End time
    end = time.time()

    # total time taken
    print(f"Documents finished indexing in {(end - start):.2f}s")


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
