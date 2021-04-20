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

    Additional Packages that we have downloaded, and submitted with this zip folder. These were not native to Tembusu, but were essential for our search engine
        . regex                     - python module name is 're', used for regular expression matching
        . nltk                      - used for various language processing tasks
        . nltk.corpus.stopwords     - used to remove English stopwords from corpus
        . nltk.corpus.wordnet       - used to obtain theasaurus for query expansion
        . gensim                    - used to obtain word2vec to train models to select best synonyms from wordnet theasaurus synonyms
        . smart_open                - used by gensim
        . numpy                     - used by gensim (we did not use numpy directly)
        . scipy                     - used by gensim (we did not use scipy directly)
        . progress                  - used to display a progress bar during indexing step

========== Running the Code ==========
We made no changes to the default command line code. Exact command depends on your system. For us, it was as such

    Indexing:           python index.py -i dataset.csv -d dictionary.txt -p postings.txt
    Searching:          python search.py -d dictionary.txt -p postings.txt -q queries/q1.txt -o results1.txt

We have ran the query_expansion.py file and generated the necessary output. There is no requirement to run this file because the model.kv file is already generated. However if required, please perform the following (assuming dataset.csv is also in the root folder):

    Query Expansion:    python query_expansion.py

========== General Notes about this assignment ==========
We have created a search engine for legal documents, obtained from the corpus provided by Intellex. We shall detail the following:

    == System Overview ==

        Indexing pseudocode
        . With every row in the corpus of legal documents (dataset.csv), each row representing one document
            . Read the row and parse the five fields (doc_id, title, content, date, court)
                . Drop the 'date' field since it is not important for our search engine
                . Create a reduced doc_id since the doc_ids are big integers. This performs a mapping like
                    --> reduced doc_id = 1 maps to original doc_id = 2851098
                    This will achieve some space savings, as we utilize doc_ids frequently. The mapping is saved once in metadata.txt
                . Replace the 'court' with an integer score to represent the importance of various courts. Save in metadata.txt
                    --> Most important courts = 3, important courts = 2, normal courts = 1
                . Clean the 'title', 'content', 'court' fields using our class Clean in clean.py. The cleaning steps are as such
                    1. remove javascript
                    2. make lowercase
                    3. remove stopwords
                    4. remove illegal characters (keep alphabet only)
                    5. change spelling to british spelling
                    6. tokenize
                    7. stem
            . With the cleaned 'title', 'content', 'court' concatanated as one long string, perform indexing of terms
                . append terms into master list
                . add terms into a dictionary, keeping a count and also create the positional index posting list. If term exists in dictionary, update the entry
                    --> positional index is saved as the delta between term positions in a document, not the absolute position. This further saves some memory by only saving smaller integer deltas

            . Create a word2vec model that is trained on text from title, content, court from all documents in the dataset
                . Outputs model.kv which will be utilised in our search functions


    == System Architecture ==

        . metadata.txt
            {   reduced_doc_id:
                {   original_doc_id: n,
                    court: m
                }
            }


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
        . query_expansion.py    Trains the word2vec model that is used to evaluate synonyms via cosine similarity
        . vb_encoder.py         Used to perform variable byte encoding on the positional index array in postings_list to save memory

    == Reference Files ==

        . dictionary.txt        Used to point a term to its posting list
        . postings.txt          Contains posting lists for various terms
        . metadata.txt          Used to convert our reduced document IDs into original document IDs
        . doc_lengths.txt       Used to perform normalization when calculating scores

    == Auxilliary Files ==

        . model.kv              The trained word2vec model generated from query_expansion.py that is used in search.py
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
