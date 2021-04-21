# cs3245_homework_4

This is the README file for A0228402N-A0230521Y-A0230632U submission.
We are contactable through the following:

A0228402N at e0673235@u.nus.edu
A0230521Y at e0697782@u.nus.edu
A0230632U at e0698539@u.nus.edu

========== Python Version ==========
We are using Python Version 3.8.5 in an Anaconda environment for this homework. We have verified that our system runs on Tembusu.

========== Python Packages ==========
We have tested our system on Tembusu, and the necessary packages that we installed separately have been bundled together with this submission. Here are the package details

    Default Packages assumed to be present in Tembusu. We performed our own checks in Tembusu and found them to be present

        . sys, getopt               - default in boilerplate
        . string                    - string manipulations
        . struct.pack               - used for variable byte encoding
        . struct.unpack             - used for variable byte encoding
        . os                        - used to traverse directory to retrieve files
        . struct.unpack             - used for variable byte encoding
        . pickle                    - used to serialize objects as bytes and save
        . math                      - used to perform mathematical operations
        . time                      - used to time the index creation step
        . regex                     - python module name is 're', used for regular expression matching
        . nltk                      - used for various language processing tasks
        . numpy                     - used by gensim (we did not use numpy directly)
        . multiprocessing           - used to process index in parallel

    Additional Packages that we have downloaded, and submitted with this zip folder. These were not native to Tembusu, but were essential for our search engine

        . nltk.corpus.stopwords     - used to remove English stopwords from corpus
        . nltk.corpus.wordnet       - used to obtain theasaurus for query expansion
        . nltk.tokenize.punkt       - used to perform tokenization
        . gensim                    - used to obtain word2vec to train models to select best synonyms from wordnet theasaurus synonyms
        . smart_open                - used by gensim
        . scipy                     - used by gensim (we did not use scipy directly)
        . progress                  - used to display a progress bar during indexing step

========== Running the Code ==========
We have ran the word2vec.py file and generated the necessary output. There is no requirement to run this file because the model.kv file is already generated. However if required, please perform the following (assuming dataset.csv is also in the root folder):

    word2vec            python word2vec.py           --> generates model.kv file

We made no changes to the default command line code. Exact command depends on your system. For us, it was as such

    Indexing            python index.py -i dataset.csv -d dictionary.txt -p postings.txt
    Searching           python search.py -d dictionary.txt -p postings.txt -q queries/q1.txt -o results1.txt

========== General Notes about this assignment ==========
We have created a search engine for legal documents, obtained from the corpus provided by Intellex. We shall detail the following:

    == System Overview ==
    Key concepts used

    .




    == System Overview (Detailed) ==
    THe implementation of the key concepts that we employed, as outlined above

        == word2vec pseudocode ==

        . Create a word2vec model that is trained on text from title, content, court from all documents in the dataset using gensim
            . Outputs model.kv which will be utilised in our search functions

        == Cleaning pseudocode ==

        . Given an input string, we perform the following steps to clean the string
            1. remove javascript
            2. remove illegal characters (keep alphabet only)
            3. make lower case
            4. change spelling to american spelling
            5. tokenize
            6. remove stopwords
            7. remove punctuations
            8. stem
            9. remove empty words

        == Indexing pseudocode ==

        . We are using multiprocessing in order to parallelize the index creation process. This greatly speeds up our index creation from several hours to 20 minutes. We process each row of the dataset in parallel (i.e. document by document)

        . With every row in the corpus of legal documents (dataset.csv), each row representing one document
            . Read the row and parse the five fields (doc_id, title, content, date, court)
                . Drop the 'date' field since it is not important for our search engine
                . Create a reduced doc_id since the doc_ids are big integers. This performs a mapping like
                    --> reduced doc_id = 1 maps to original doc_id = 2851098
                    --> This will achieve some space savings, as we utilize doc_ids frequently. The mapping is saved once in metadata.txt
                . Replace the 'court' with an integer score to represent the importance of various courts. Save in metadata.txt
                    --> Most important courts = 3, important courts = 2, normal courts = 1
                . Clean the 'title', 'content', 'court' fields using our class Clean in clean.py. The cleaning steps are present in clean.py
                . With the cleaned 'title', 'content', 'court' concatanated as one long string, perform indexing of terms
                    . Add terms into a dictionary, keeping a count and also create the positional index list. If term exists in dictionary, update the entry
                        --> positional index is saved as the postitional delta between term positions in a document, not the absolute position
                        --> This further saves some memory by only saving smaller integer deltas
                    . Calculate the tf-idf score for individual terms using the lnc-ltc scheme (same as Homework 3)
            . Returns the following for each row (document) by writing into the multiprocessing container variables
                1. doc_lengths                      - the length of the document
                2. local_dict_list                  - list of dictionaries of term to doc_id, term_freq and positions
                3. local_doc_metadata_dict_list     - list of dictionaries of downsized doc_id to original doc_id, court rank

        . With the individual rows processed via multiprocessing, accumulate all the data to prepare for writing to output files
            . Aggregate doc_lengths, local_dict_list, local_doc_metadata_dict_list containers and recreate the full output dictionaries from data produced by individual documents
        .  Write out the following to output files
            1. doc_lengths.txt      contains doc_id to document lengths for normalization
            2. metadata.txt         contains mapping from reduced doc_id to original doc_id and its court ranking
            3. postings.txt         postings.txt is written out term by term in order to obtain address for individual postings lists
            4. dictionary.txt       points a term to its postings list in postings.txt via a byte offset

        == Searching pseudocode ==

        . Load in term dictionary, document length dictionary, metadata, and queries
        . Parse the query to retrieve different query types as follows:
            Term is defined as either a word or a phrase
            1. free text list consisting of all individual words within the query string
            2. phrases list consisting of two or three words surrounded by double quotes like "__ __" or "__ __ __"
            3. words list consisting of words that are not part of a phrase, i.e. not wrapped around double quotes
            4. boolean flag indicating presence of 'AND' operator in the query string. Note, we assume that boolean operations always contain "AND" between every term in the query string,

            e.g. "fertility treatment" AND damages (query 3 provided)
                --> free_text = [fertility, treatment, damages]
                --> phrases = ["fertility treament"]
                --> words = [damages]
                --> is_boolean = True

        . Query expansion
            . Adding new words
                . With each individual term in the free text list, generate a list of synonyms using wordnet
                . these synonyms will be stored in a synonym dictionary where each term will be mapped to its generated synonyms
                . clean and perform a check on each synonym
                    . If synonym exists in the term dictionary, calculate the similarity score between the original term and the synonym using the trained word2vec model and map it to the corresponding synonym
                . for each word in the free text array, return the most similar synonym (if any) and append to the free text array and word array
            . Adding new phrases
                . If the original query has phrases
                    . No change
                . Else,
                    . Permute every possible pair of words in the free_text list and append to phrases list to generate artificial phrases

            . Conduct lnc.ltc ranking scheme with cosine normalization for the query
                . for free text query, calculate w(t,q) for each term and normalizae the scores using document length.
            . For each phrase in phrases, split the phrases into the individual terms and retrieve their postings list
                . utilise positional index inside the postings list to find the intersection between the postings list to return documents containing consecutive positional indexes
                    . track the number of occurences of a valid dissected phrase in a document and add it into a dictionary. This number of occurences will be multiplied by a pretermined phrasal weight modifier to be added to the base score for free text
            . If boolean flag is positive ('AND' is present)
                . for each term in the query, retrieve its posting list
                . track the number of occurences of a particular document across all postings list in a dictionary
                . documents with more than one unique count indicate intersection between documents
                . normalize the count for each document over the expected number of AND operations (number of posting lists)
            . Apply modifiers to the original scores from free text handling. There are a total of 3 possible modifiers as follows:
                . phrase modifier -> to increase scores if phrases are matched
                . boolean modifier -> to increase scores if boolean 'AND' condition is matched
                . court modifier -> to increase scores if document's 'court' field matches court importance dictionary
                . Different weights will be applied to boolean and non-boolean queries
                    . assume that for a purely free text query, a higher weightage would be given if phrases are matched, followed by the conditional that boolean 'AND' is matched
                    . for a boolean query, the boolean condition holds the highest weightage followed by the condition that phrases are matched
            . Sort the scores in descending order and append the documents in the corresponding order to a list
            . Remove any possible duplicate documents in the resulting list of documents
            . Return top k list of documents determined by a threshold value. This assumes that our modifier algorithm returns the most relevant documents first, meaning that non-relevant documents will appear much more frequently at the end of the list and should not be returned. This will hence increase precision.



    == System Architecture ==

        . Our output files can be inspected through test.py by commenting out the corresponding lines to load the desired file

        metadata.txt
            {   reduced_doc_id:                     example         { 1:
                {   original_doc_id: n,                                 {   'og_doc_id': 246391,
                    court: m                                                'court': 2
                },                                                      },
                ...                                                     ...
            }                                                       }

        doc_lengths.txt
            {   reduced_doc_id: doc_length,         example         {   1: 35.38262208800508,
                ...                                                     ...
            }                                                       }

        dictionary.txt
            {   term: byte offset in postings.txt,  example         {   'telesurveyor': 704477650,
                ...                                                     ...
            }                                                       }

        postings.txt
            {   'doc_freq': n,                      example         {   'doc_freq': 659,
                'postings_list': [                                      'postings_list': [
                    {   'doc_id': m,                                        {   'doc_id': 1,
                        'term_freq': o,                                         'term_freq': 36,
                        'positions': [1,2,3,4,5...]                             'postitions': [0, 9, 38...]
                    },                                                      },
                    ...                                                     ...
                ]                                                       ]
            },                                                      },
            ...                                                     ...

    == Techniques Employed (worked) ==




    == Techniques Employed (did not work) ==

========== Specific Notes about this assignment ==========

========== Files included with this submission ==========

    == File Sizes ==

        . Total submission size (excluding dataset.csv)             MB
        . Index (postings.txt) file size:                           MB
        . Additional package file size (total):                     MB

    == Python Files ==

        . index.py              Generate the the reference files that contain the dictionary, index, metadata, doc_lengths
        . search.py             Used to process a query file and outputs the results
        . clean.py              Our own mython class that is used to clean documents and queries
        . word2vec.py           Trains the word2vec model that is used to evaluate synonyms via cosine similarity
        . vb_encoder.py         Used to perform variable byte encoding on the positional index array in postings_list to save memory

    == Reference Files ==

        . dictionary.txt        Used to point a term to its posting list
        . postings.txt          Contains posting lists for various terms
        . metadata.txt          Used to convert our reduced document IDs into original document IDs
        . doc_lengths.txt       Used to perform normalization when calculating scores

    == Auxilliary Files ==

        . model.kv              The trained word2vec model generated from word2vec.py that is used in search.py
        . README.txt            This document

    == Packages ==

========== Allocation of Work ==========

    We, A0228402N, A0230521Y, A0230632U verify that we have shared the workload equally for this project, and should be graded equally.

========== Statement of Individual Work ==========

    Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

    [x] We, A0228402N, A0230521Y, A0230632U certify that we have followed the CS 3245 Information
    Retrieval class guidelines for homework assignments.  In particular, we
    expressly vow that we have followed the Facebook rule in discussing
    with others in doing the assignment and did not take notes (digital or
    printed) from the discussions.

    [ ] We, A0228402N, A0230521Y, A0230632U did not follow the class rules regarding homework
    assignment, because of the following reason:

    NA

    We suggest that We should be graded as follows:

    As per normal

== References ==

https://stackoverflow.com/ referenced for some syntax
http://www.nltk.org/index.html to understand how nltk works

    There was no collaboration with other students
