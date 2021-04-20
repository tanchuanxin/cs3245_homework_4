#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
import math
import os
import string
# TODO
# from nltk.corpus import wordnet
# from gensim.models import KeyedVectors

# Import own files
from clean import Clean
import vb_encoder

# Global definitions
NUM_DOCS = 17153

# Create instances of imported classes
cleaner = Clean()


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


# Loads in the term dictionary from file
def load_dictionary(dict_file):
    # Open our dictionary file
    f_dict = open(dict_file, "rb")

    # Read in dictionary into object
    term_dict = pickle.load(f_dict)

    # Close our dictionary file
    f_dict.close()

    # Return term dictionary
    return term_dict


# Loads in a dictionary of document lengths
def load_doc_lengths():
    # Open our doc lengths file
    f_doc_lengths = open(
        os.path.join(os.path.dirname(__file__), "doc_lengths.txt"), "rb"
    )

    # Read in dictionary into object
    doc_lengths = pickle.load(f_doc_lengths)

    # Close our doc lengths file
    f_doc_lengths.close()

    # Return doc lengths dictionary
    return doc_lengths


# Loads in a postings list given the address offset in the postings file
def load_postings_list(postings_file, address):
    # Open our postings file
    f_postings = open(postings_file, "rb")

    # Read in PostingsList
    f_postings.seek(address, 0)  # Seek to start of PostingsList
    postings_list = pickle.load(f_postings)  # Read in PostingsList

    # for each posting in postings list, decode the posting's position array
    for postings in postings_list["postings_list"]:
        postings["positions"] = vb_encoder.decode(postings["positions"])

    # Close our postings file
    f_postings.close()

    # Return the postings list for that term
    return postings_list


# Loads in a metadata dictionary that contains the original document id and the court priority
def load_metadata():
    # Open our metadata file
    f_metadata = open(
        os.path.join(os.path.dirname(__file__), "metadata.txt"), "rb"
    )

    # Read in Metadata
    metadata = pickle.load(f_metadata)

    # Close our metadata file
    f_metadata.close()

    # Return the metadata dictionary
    return metadata


# Returns an array of queries (each element is a query)
def load_queries(queries_file):
    # Open our queries file
    f_queries = open(queries_file, "r")

    # Read all queries in
    queries = f_queries.readlines()

    # Remove newline characters
    queries = [query.rstrip() for query in queries]

    # Close our queries file
    f_queries.close()

    # Return the queries array
    return queries


# Writes out the results
def write_results_to_disk(results: list, results_file):
    f_results = open(results_file, "w")

    # Write result as a line
    output = ""
    for doc_id in results:
        output += str(doc_id) + " "

    output = output.rstrip()  # No need newline, just remove trailing spaces

    f_results.write(output)
    f_results.close()


# processes the input query by identifying boolean queries, and phrases
def parse_query(query):
    is_boolean = False
    query_string = query[0]

    # identify boolean queries
    if " AND " in query_string:
        is_boolean = True
        query_string = query_string.replace(" AND ", " ")
    query_string = query_string.split()

    # containers to differentiate words and phrases
    words = []
    phrases = []

    # splitting the query string into words and phrases
    phrase = None
    for term in query_string:
        term = term.strip()
        if term[0] == '"':
            phrase = term[1:]
        elif phrase != None:
            phrase += " "
            phrase += term[0:-1]
            if term[-1] == '"':
                phrases.append(phrase)
                phrase = None
        else:
            words.append(term)

    # cleaning all tokens in words and phrases (also tokenizing and stemming)
    words = [cleaner.clean(word) for word in words]
    words = [word for word in words if word]
    phrases = [cleaner.clean(phrase) for phrase in phrases]
    free_texts = [item for sublist in words+phrases for item in sublist]

    ''' We want to assume that if given a free text query, if given no additional information
    free text searches should be rated higher if they meet the boolean criteria 
    
    turn this flag off if we no longer wish to make the assumption '''
    is_boolean = True

    return words, phrases, free_texts, is_boolean


# utilise positional index inside the postings list in order to check if a phrase is present
# return value is the intersection between pl1 and pl2, which represents the documents containing consecutive positional indexes (i.e. phrase)
def check_phrase(pl1, pl2):
    valid_docs = {}

    if pl1 == None or pl2 == None:
        return valid_docs

    # intialize running counters for document indexes
    pl1_doc_index, pl2_doc_index = 0, 0  # the document we are on, based on index

    while True:
        # terminating conditions: if we run out of documents to process, terminate and return the current matches
        if pl1_doc_index >= len(pl1) or pl2_doc_index >= len(pl2):
            return valid_docs

        # advancing indexes when the document no longer matches
        if pl1[pl1_doc_index]["doc_id"] > pl2[pl2_doc_index]["doc_id"]:
            pl2_doc_index += 1
        elif pl2[pl2_doc_index]["doc_id"] > pl1[pl1_doc_index]["doc_id"]:
            pl1_doc_index += 1
        else:
            # doc_ids are equal, start comparing the positions of the words to determine if the phrase exists
            # intialize the index of the position we are on, inside a document
            pl1_pos_index, pl2_pos_index = 0, 0

            # initialize the incremental sum of position, to undo the positional deltas
            pl1_pos, pl2_pos = pl1[pl1_doc_index]["positions"][pl1_pos_index], pl2[pl2_doc_index]["positions"][pl2_pos_index]

            while True:
                # terminating conditions: if we run out of positions to process, terminate and move on to the next document
                if pl1_pos_index >= len(pl1[pl1_doc_index]["positions"]) or pl2_pos_index >= len(pl2[pl2_doc_index]["positions"]):
                    pl2_doc_index += 1
                    pl1_doc_index += 1
                    break

                # advancing indexes when the positions are not consecutive. advance the smaller position
                # e.g. pl1_pos = 0, pl2_pos = 0, there is no way for it to be a phrase. Therefore we increment pl2_pos_index and pl2_pos
                if pl1_pos >= pl2_pos:
                    pl2_pos_index += 1
                    # if exceed max length, cannot add
                    if pl2_pos_index < len(pl2[pl2_doc_index]["positions"]):
                        pl2_pos += pl2[pl2_doc_index]["positions"][pl2_pos_index]
                # e.g. pl2_pos = 5, pl1_pos = 3, there is no way for it to be a phrase. Therefore we increment pl1_pos_index and pl1_pos
                elif pl2_pos > pl1_pos+1:
                    pl1_pos_index += 1
                    # if exceed max length, cannot add
                    if pl1_pos_index < len(pl1[pl1_doc_index]["positions"]):
                        pl1_pos += pl1[pl1_doc_index]["positions"][pl1_pos_index]
                # if we find a consecutive instance of the first and second word, the phrase is found
                elif pl1_pos + 1 == pl2_pos:
                    # we track the number of occurences of the phrase. The more a phrase occurs, the higher the score for that document
                    if pl1[pl1_doc_index]["doc_id"] in valid_docs.keys():
                        valid_docs[pl1[pl1_doc_index]["doc_id"]] += 1
                    else:
                        valid_docs[pl1[pl1_doc_index]["doc_id"]] = 1
                    pl1_pos_index += 1
                    pl2_pos_index += 1
                    # if exceed max length, cannot add
                    if pl1_pos_index < len(pl1[pl1_doc_index]["positions"]):
                        pl1_pos += pl1[pl1_doc_index]["positions"][pl1_pos_index]
                    # if exceed max length, cannot add
                    if pl2_pos_index < len(pl2[pl2_doc_index]["positions"]):
                        pl2_pos += pl2[pl2_doc_index]["positions"][pl2_pos_index]

    return valid_docs


# # load trained word vectors
# wordvectors = KeyedVectors.load_word2vec_format('model.kv', binary=True)

# # generate synonyms from wordnet then evaluate against word2vec


# def query_expansion(free_texts, wordvectors):

#     # create a synonym dictionary to store word: {synonym:similarity score}
#     synonym_dic = {}
#     for word in free_texts:
#         synonyms = []
#         refined_synonyms = []
#         for syn in wordnet.synsets(word):
#             for l in syn.lemmas():
#                 # synonym list
#                 synonyms.append(l.name())
#         # if there are synonyms available
#         if set(synonyms) != set():
#             for synonym in set(synonyms):
#                 # clean and preprocess the synonyms
#                 synonym = cleaner.clean(synonym)
#                 # if synonym is not an empty list (word removed due to cleaning because it is a stopword)
#                 if synonym != []:
#                     refined_synonyms.append(synonym)
#             # for each refined synonym
#             for s in refined_synonyms:
#                 # check if word and generated synonyms are within the trained model and proceed if the synonym is different from the original word
#                 if s[0] in wordvectors and word in wordvectors and s[0] != word:
#                     if word in synonym_dic.keys():
#                         # calculate similarity of each synonym and the original word
#                         synonym_dic[word][s[0]] = wordvectors.similarity(
#                             word, s[0])
#                     else:
#                         # initialise dictionary to store synonym and its similarity score
#                         synonym_dic[word] = {}
#                         synonym_dic[word][s[0]] = wordvectors.similarity(
#                             word, s[0])
#     return synonym_dic

# utilise intersection of document ids in order to check if a boolean function is satisfied
def check_boolean(words, phrases, free_texts, free_texts_postings_lists_dict):
    # a list of all the document ids for every term that we have. A term is either a phrase of a word
    term_document_ids = []

    # a dictionary that contains the document ids for every word that we have in the free-text form
    word_document_ids = {}

    # extract all document ids for every word that we have in the free-text form
    for word in free_texts:
        word_document_id = []
        if free_texts_postings_lists_dict[word] == None:
            word_document_ids[word] = word_document_id
        else:
            for doc in free_texts_postings_lists_dict[word]:
                word_document_id.append(doc["doc_id"])
            word_document_ids[word] = word_document_id

    # find the intersection document ids list for the words in the phrase queries (a, b) n (b, c) -> (b)
    for phrase in phrases:
        # a list to hold the valid document ids
        phrase_document_ids = []
        for word in phrase:
            phrase_document_ids.append(set(word_document_ids[word]))

        # finding the intersection
        phrase_document_ids = list(
            phrase_document_ids[0].intersection(*phrase_document_ids))
        term_document_ids.append(phrase_document_ids)

    # add on the document ids list for the word queries
    for word in words:
        # small data structure change, since words are encapsulated in a list
        word = word[0]
        term_document_ids.append(word_document_ids[word])

    return term_document_ids


def run_search(dict_file, postings_file, queries_file, results_file):
    ''' ##############################################################################################################################################################################
    # read in files 
    ##############################################################################################################################################################################'''
    print("Loading in necessary files")

    # Load in term dictionary
    dictionary = load_dictionary(dict_file)
    print("Term dictionary loaded. Loading in document lengths...")

    # Load in document lengths
    doc_lengths = load_doc_lengths()
    print("Document lengths loaded.")

    # Load in metadata
    metadata = load_metadata()
    print("Metadata loaded")

    # Load in queries
    query = load_queries(queries_file)
    print("Queries loaded. Now querying...")

    ''' ##############################################################################################################################################################################
    # perform search
    ############################################################################################################################################################################## '''
    print("Running search on the queries...\n")

    # Store results of each query
    results = []

    # parse our query and obtain the different query types
    words, phrases, free_texts, is_boolean = parse_query(query)
    print("query words:", words)
    print("query phrases:", phrases)
    print("query free_texts:", free_texts)
    print("query is_boolean:", is_boolean)

    # # obtain synonyms for free_texts
    # synonyms = query_expansion(free_texts, wordvectors)
    # terms = []

    # # sort synonyms by descending similarity score
    # for key in synonyms:
    #     synonyms[key] = {k: v for k, v in sorted(
    #         synonyms[key].items(), key=lambda item: item[1], reverse=True)}
    #     # only take the term with the highest similarity
    #     terms.append(list(synonyms[key].keys())[0])

    # # append the expanded query terms (synonyms) to the free_text query as well as the words query
    # for term in terms:
    #     free_texts.append(term)
    #     words.append([term])

    # print("expanded_query free_texts:", free_texts)
    # print("expanded_query words:", words)

    # For query, conduct lnc.ltc ranking scheme with cosine normalization
    # Create scores dictionary to store scores of each relevant document
    scores = {}
    free_texts_postings_lists_dict = {}

    ''' ##############################################################################################################################################################################
    # step 1 - get the freetext query result, on the assumptuon of "OR" between every individual token 
    ############################################################################################################################################################################## '''
    # Count term frequencies for each term in freetext query
    term_freqs = {}

    for term in free_texts:
        if term in term_freqs:
            term_freqs[term] += 1
        else:
            term_freqs[term] = 1

    # Calculate w(t, q) for each term in the free text version
    for term in free_texts:
        # Term not found, skip it
        if term not in dictionary:
            free_texts_postings_lists_dict[term] = None
            continue

        # Load in PostingsList of term
        term_postings_list = load_postings_list(
            postings_file, dictionary[term])
        # Actual postings list
        postings_list = term_postings_list["postings_list"]
        # Document frequency of term
        term_doc_freq = term_postings_list["doc_freq"]

        # For subsequent ranking based on boolean query and phrasal query
        free_texts_postings_lists_dict[term] = postings_list

        # Get term frequency
        term_freq = 1 + math.log(term_freqs[term], 10)

        # Get inverted document frequency
        inv_doc_freq = math.log(NUM_DOCS / term_doc_freq, 10)

        # Calculate weight for term in query
        weight_term_query = term_freq * inv_doc_freq

        # Iterate through postings list for the term and compute w(t, d)
        for posting in postings_list:
            # Calculate w(t, d). Again, we ignore idf. posting[1] is term_freq
            weight_term_doc = 1 + math.log(posting["term_freq"], 10)

            # Add to the document's scores the dot product of w(t, d) and w(t, q).
            # posting[0] is doc_id
            if posting["doc_id"] not in scores:
                scores[posting["doc_id"]] = weight_term_doc * weight_term_query
            else:
                scores[posting["doc_id"]] += weight_term_doc * \
                    weight_term_query

    # Normalize the scores using doc_length
    for doc_id in scores.keys():
        scores[doc_id] = scores[doc_id] / doc_lengths[doc_id]

    ''' ##############################################################################################################################################################################
    # step 2 - get the phrase query results and use it to modify scores 
    we perform pairwise check so as to assign some extra score for partial phrase match
    e.g phrase "a b c" receives some score for "a b", even if "b c" is not in the document 
    ############################################################################################################################################################################## '''
    # container to track the number of occurences of a valid dissected valid phrase in a document
    valid_phrases_docs_modifier = {}

    for phrase in phrases:
        # pairwise check
        for i in range(len(phrase) - 1):
            valid_docs = check_phrase(
                free_texts_postings_lists_dict[phrase[i]], free_texts_postings_lists_dict[phrase[i + 1]])

            # add into the overall container
            for key in valid_docs.keys():
                if key in valid_phrases_docs_modifier.keys():
                    valid_phrases_docs_modifier[key] += valid_docs[key]
                else:
                    valid_phrases_docs_modifier[key] = valid_docs[key]

                # valid_phrases_docs_modifier[key] = valid_phrases_docs_modifier[key]*2 / metadata[key]["num_terms"] # KIV

    if len(valid_phrases_docs_modifier.values()) > 0:
        max_phrase_matches = max(valid_phrases_docs_modifier.values())

        for key in valid_phrases_docs_modifier.keys():
            # KIV
            valid_phrases_docs_modifier[key] = valid_phrases_docs_modifier[key] / \
                max_phrase_matches

    # print("valid_phrases_docs_modifier:", valid_phrases_docs_modifier)

    ''' ##############################################################################################################################################################################
    # step 3 - if boolean query, get the intersection results and use it to modify scores
    # the more ANDs that match, the higher our score will be 
    ############################################################################################################################################################################## '''
    # container to track the number of occurences of a an AND query in a document
    valid_boolean_docs_modifier = {}

    # only if the query is a boolean query
    if is_boolean:
        term_document_ids = check_boolean(
            words, phrases, free_texts, free_texts_postings_lists_dict)

        # temporary holder for the documents that will match the boolean query
        boolean_docs = {}

        # for every valid set of document ids for a term
        for term_document_id in term_document_ids:
            # for every document id in that set
            for document_id in term_document_id:
                # uniqueness count
                if document_id in boolean_docs:
                    boolean_docs[document_id] += 1
                else:
                    boolean_docs[document_id] = 1

        # only those document ids with count>1 satisfy the AND operation
        for document_id in boolean_docs.keys():
            if boolean_docs[document_id] != 1:
                # normalize over the expected number of AND operations
                valid_boolean_docs_modifier[document_id] = (
                    boolean_docs[document_id] - 1) / (len(term_document_ids) - 1)

        # print("valid_boolean_docs_modifier:", valid_boolean_docs_modifier)

    ''' ##############################################################################################################################################################################
    # step 4 - apply modifiers to our original scores 
    a. valid_phrases_docs_modifier - bump scores up if we match phrases
    b. valid_boolean_docs_modifier - bump scores up if we match the boolean value closely
    c. court - metadata contains the court importance (3 - most important, 1 - least important)
    ############################################################################################################################################################################## '''
    MODIFIER_WEIGHT_PHRASE = 3
    MODIFIER_WEIGHT_BOOLEAN = 3
    MODIFIER_WEIGHT_COURT = 0.05

    # g(d) for phrases_docs_modifier is just 1
    for phrases_docs_modifier in valid_phrases_docs_modifier.keys():
        if phrases_docs_modifier in scores:
            scores[phrases_docs_modifier] += valid_phrases_docs_modifier[phrases_docs_modifier] * \
                MODIFIER_WEIGHT_PHRASE

    # g(d) for boolean_docs_modifier is just 1
    for boolean_docs_modifier in valid_boolean_docs_modifier.keys():
        if boolean_docs_modifier in scores:
            scores[boolean_docs_modifier] += valid_boolean_docs_modifier[boolean_docs_modifier] * \
                MODIFIER_WEIGHT_BOOLEAN

    # g(d) for court = 0.05
    for key in scores.keys():
        scores[key] += metadata[key]["court"] * MODIFIER_WEIGHT_COURT

    scores = {k: v for k, v in sorted(
        scores.items(), key=lambda item: item[1], reverse=True)}

    ''' ##############################################################################################################################################################################
    # step 5 - convert the small doc_id into the original large doc_id, then output to results file
    metadata - contains the mapping of small doc_id to original large doc_id
    large doc_id is the output of the results file
    ############################################################################################################################################################################## '''
    THRESHOLD = 0.5  # keep a subset of the scores

    results = []

    for key in scores.keys():
        if metadata[key]["og_doc_id"] not in results:
            results.append(metadata[key]["og_doc_id"])

    cutoff = int(THRESHOLD * len(results))
    results = results[:cutoff]

    # Write out results to disk
    write_results_to_disk(results, results_file)

    print("Querying complete. Find your results at `{}`.".format(results_file))


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:p:q:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        dictionary_file = a
    elif o == "-p":
        postings_file = a
    elif o == "-q":
        file_of_queries = a
    elif o == "-o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if (
    dictionary_file == None
    or postings_file == None
    or file_of_queries == None
    or file_of_output == None
):
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
