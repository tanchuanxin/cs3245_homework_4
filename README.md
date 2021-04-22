# cs3245_homework_4

This is the README file for A0228402N-A0230521Y-A0230632U submission.
We are contactable through the following:

* A0228402N at e0673235@u.nus.edu
* A0230521Y at e0697782@u.nus.edu
* A0230632U at e0698539@u.nus.edu

### ========== Python Version ==========

We are using Python Version 3.8.5 in an Anaconda environment for this homework. We have verified that our system runs on Tembusu.

### ========== Python Packages ==========

We have tested our system on Tembusu, and the necessary packages that we installed separately have been bundled together with this submission. Here are the package details

    Default Packages assumed to be present in Tembusu. We performed our own checks in Tembusu and found them to be present

        * sys, getopt               - default in boilerplate
        * string                    - string manipulations
        * struct.pack               - used for variable byte encoding
        * struct.unpack             - used for variable byte encoding
        * os                        - used to traverse directory to retrieve files
        * pickle                    - used to serialize objects as bytes and save
        * math                      - used to perform mathematical operations
        * time                      - used to time the index creation step
        * regex                     - python module name is 're', used for regular expression matching
        * nltk                      - used for various language processing tasks
        * numpy                     - used by gensim (we did not use numpy directly)
        * multiprocessing           - used to process index in parallel

    Additional Packages that we have received help from the TA to install on the leaderboard environment. Thanks to TA Liu Zhiyuan for the help rendered. We will work on the assumption that the grading environment will be the same as the leaderboard environment, and therefore these packages will be present

        * gensim                    - used to obtain word2vec to train models to select best synonyms from wordnet theasaurus synonyms
        * smart_open                - used by gensim
        * scipy                     - used by gensim (we did not use scipy directly)

    Additional Packages that we have downloaded, and submitted with this zip folder. These were not native to Tembusu, but were essential for our search engine.We have verified multiple runs on the leaderboard that this works

        * nltk.corpus.stopwords     - used to remove English stopwords from corpus
        * nltk.corpus.wordnet       - used to obtain theasaurus for query expansion
        * nltk.tokenize.punkt       - used to perform tokenization
        * progress                  - used to display a progress bar during indexing step

### ========== Running the Code ==========

We have ran the word2vec.py file and generated the necessary output. There is no requirement to run this command because the model.kv file is already generated and included in our submission. However if required, please perform the following (assuming dataset.csv is also in the root folder):

    * word2vec            python word2vec.py           --> generates model.kv file

We made no changes to the default command line code. Exact command depends on your system. For us, it was as such

    * Indexing            python index.py -i dataset.csv -d dictionary.txt -p postings.txt
    * Searching           python search.py -d dictionary.txt -p postings.txt -q queries/q1.txt -o results1.txt

### ========== Specific Notes about this assignment ==========

    * Query Expansion, Relevance Feedback
        We have employed query expansion techniques, and it allowed us to retrieve more relevant documents. We initially added one synonym per originial word in the query to expand our search, but found that it included too many false positives. Therefore we limited it to just one most important synonym to expand our search

        We opted for query expansion, therefore did not employ relevance feedback in this assignment. However this has caused our results to suffer, because the documents marked as relevant in the query files would not have been pushed to the top of the return list through relevance feedback. Other groups however would have picked up these relevant documents and pushed it to the top of their search results, and hence have a better score.

        While we can pick up these relevant document ids and push them up as well, we decided not to since it would not be in the spirit of fair play if we do not implement the rest of the relevance feedback code.

    * Net Scoring Function
        Our net scoring function failed to produce better scores than the baseline tf-idf version on the leaderboard. However we achieved Mean Average F2: 0.19779623780332 versus the baseline version of 0.214287158831903, which is fairly close.

        Our normal tf-idf baseline version performed better than the baseline version, but due to strange submission complications, the scores were overwritten. Therefore we will submit our net score version

        Our net scoring function did not perform as well on the leaderboard as it did locally, However we still believe that net scoring function is important and therefore chose to include it in this submission.

        As a point of clarification: query expansion WORKED on query 1-3, the queries that were provided to us, significantly improving the results returned.

        For example, we have the following experiments on the provided query 1-3, and we managed to return the relevant documents provided at a higher score by implementing score modifiers, versus the basic tf-tdf scores.

        With the following weights on the modifiers:
            MODIFIER_WEIGHT_PHRASE = 1
            MODIFIER_WEIGHT_BOOLEAN = 0
            MODIFIER_WEIGHT_COURT = 0.01

        With net score                              index returned for relevant documents
        query   query string                        doc1    doc2    doc3    average
        q1      quiet phone call                    31      427     665     374.333
        q2      good grades exchange scandal        2       32              17.0
        q3      "fertility treatment" AND damages   22      1       23      15.33

        Without net score (pure tf-idf)             index returned for relevant documents
        query   query string                        doc1    doc2    doc3    average
        q1      quiet phone call                    2243    98      476     939.0
        q2      good grades exchange scandal        169     7               88.0
        q3      "fertility treatment" AND damages   20      5       11      12.0

        Note the dramatic improvement in the average return index for the documents we know to be relevant. Except for q3, which only performed marginally worse.

        There is merit to the net scoring function. However it may be necessary to implement some form of machine learning in order to learn the best weights to apply to get a more generalizable weight to apply to our score modifiers. Hence we would like to note that query expansion can work, if given a way to optimize the weights applied to the score modifiers.

### ========== General Notes about this assignment ==========

We have created a search engine for legal documents, obtained from the corpus provided by Intellex. We shall detail the following:

    == Techniques Employed (worked) ==

        * Multiprocessing
            Not strictly a component in a search engine, but we accelerated the index creation step through multiprocessing. dataset.csv is a 700MB file, which is a fairly large dataset. Therefore it is important to have an index creation process that is scalable even with large datasets, and can complete in reasonable time.

            Our experimentation without multiprocessing took around 4 hours in order to create the index, but with multiprocessing, the time reduced significantly to ~20 minutes

        *  Variable Byte Encoding for Compression of Positional Index Deltas
            The majority of the content in postings.txt would be the positional index deltas. These represent the locations of a specific term within a document, based on its relative position with the previous time it appeared. Because position indexes within a document can run up into very large integers, it is important that we store the deltas between the positions instead of the raw position.

            We opted to further compress the memory required for our index by adding in variable byte encoding on the positional index deltas. This allowed us to compress the list even further and achieve greater memory savings

        * Query Expansion - Thesaurus and Word Vector Model (Gensim)
            We referenced from the notes to employ thesaurus-based query expansion. For each term t in a query, we expanded the query with synonyms of t from the thesaurus. The thesaurus used was Princeton's WordNet. This method generally increases recall, which more emphasised is placed on, but may decrease precision when terms are ambiguous. However, by combining it with our word2vec model from gensim trained on the dataset itself, we are able to filter out these synonyms to better fit the query by means of checking for high cosine similarity between the synonym and original word. This method proved to be effective, further justified by analysing the given relevance judgements.

            Take for example query 1: 'quiet phone call'

            A quick look at the relevance judgements provided showed that there was no presence of the word 'quiet' or 'phone' in some of the documents. Instead, the term 'telephone' is very prevalent. A naive search on terms without employing query expansion would hence not return this document based on the term 'phone', causing it to not be ranked highly and hence affecting recall and precision. Should the query be 'quiet phone', the particular relevance judgement document will not even be returned at all.

            However, by running the query expansion, we would be able to perform a search on highly similar terms e.g telephone hence increasing the document's score and allowing it to be highly ranked.

        * Net Score
            We combined various sources of "user happiness" in our scoring metric. For a given query, we considered several factors, and applied weights to these factors in order to derive our net score for a documents' relevance to the query. These alternative sources of user satisfaction were able to help our model rank the truly relevant documents higher, at least from the test queries that we have access to.

            Our rough formulas is: net_score(q,d) = cos(q,d) + f(court) + g(phrase) + h(boolean)
                where q is query, d is document, court is from d, phrase and boolean from q

            cos(q,d) is the score obtained from the lnc.ltc version of tf-idf scoring.
            This is in accordance to Homework 3

            f(court) applies a modifier on the court that the document was from.
            Some courts are more important than others, and should typically be returned higher than the less important courts.

            g(phrase) applies a modifier on the number of phrases that the query matches.
            Partial phrase matches also contribute to the score. The details of the implementation can be found under <System Overview>

            h(boolean) applies a modifier on the number of boolean conditions that can be found .
            Partial boolean condition matches also contribute to the score. The details of the implementation can be found under <System Overview>

            Documents will then be ordered according to net_score(q,d), where the most relevant documents are assumed to be at the top.

            When running our own local tests, the documents identified as relevant in q1-q3 were returned within the first 50 results for q2 and q3, and within the first 700 for q1. This is better than the baseline version where some entries were returned as in entries over 2000

    == Techniques Employed (did not work) ==

        * Query Expansion - Spacy
            Originally, we wanted to use gensim/SpaCy to do query expansion by generating synonyms of the current query.
            However, we were unable to load gensim onto the grading platform since it contains platform specific libraries.
            SpaCy was also too large, since the module itself was around 800MB, which would have caused us to exceed our submission limit.

        * Zones and Fields
            We intially tried to include zone and field information through creating new terms.
                e.g. if term = Simon (in the title), a new term of term = 'Simon.title' will be generated
            However given the nature of the search query, which is a static query in a text file, without zone or field information specified, we found that there was no way to meaningfully provide a better search experience by including zone information, since we do not know the user requirement and therefore cannot limit the search to a particular field. There are also only two searchable fields of title and content, therefore there is little need for distinction between the two.

            Hence, we opted to remove zone and field information

    == System Overview ==
    THe implementation of the key concepts that we employed, as outlined above

        == word2vec pseudocode ==

        * Create a word2vec model that is trained on text from title, content, court from all documents in the dataset using gensim
            * Outputs model.kv which will be utilised in our search functions

        == Cleaning pseudocode ==

        * Given an input string, we perform the following steps to clean the string
            1. remove javascript
            2. remove illegal characters (keep alphabet only)
            3. make lower case
            4. change all british spelling to american spelling
            5. tokenize
            6. remove stopwords
            7. remove punctuations
            8. stem
            9. remove empty words

        == Indexing pseudocode ==

        * We are using multiprocessing in order to parallelize the index creation process. This greatly speeds up our index creation from several hours to 20 minutes. We process each row of the dataset in parallel (i.e. document by document)

        * With every row in the corpus of legal documents (dataset.csv), each row representing one document
            * Read the row and parse the five fields (doc_id, title, content, date, court)
                * Drop the 'date' field since it is not important for our search engine
                * Create a reduced doc_id since the doc_ids are big integers. This performs a mapping like
                    --> reduced doc_id = 1 maps to original doc_id = 2851098
                    --> This will achieve some space savings, as we utilize doc_ids frequently. The mapping is saved once in metadata.txt
                * Replace the 'court' with an integer score to represent the importance of various courts. Save in metadata.txt
                    --> Most important courts = 3, important courts = 2, normal courts = 1
                * Clean the 'title', 'content', 'court' fields using our class Clean in clean.py. The cleaning steps are present in clean.py
                * With the cleaned 'title', 'content', 'court' concatanated as one long string, perform indexing of terms
                    * Add terms into a dictionary, keeping a count and also create the positional index list. If term exists in dictionary, update the entry
                        --> positional index is saved as the postitional delta between term positions in a document, not the absolute position
                        --> This further saves some memory by only saving smaller integer deltas
                        --> We further applied variable byte encoding to save space on these smaller integer deltas (details found in vb_encoder.py)
                    * Calculate the tf-idf score for individual terms using the lnc.ltc scheme (same as Homework 3)
            * Returns the following for each row (document) by writing into the multiprocessing container variables
                1. doc_lengths                      - the vector length of the document
                2. local_dict_list                  - list of dictionaries of term to doc_id, term_freq and positions
                3. local_doc_metadata_dict_list     - list of dictionaries of downsized doc_id to original doc_id, court rank

        * With the individual rows processed via multiprocessing, accumulate all the data to prepare for writing to output files
            * Aggregate doc_lengths, local_dict_list, local_doc_metadata_dict_list containers and recreate the full output dictionaries from data produced by individual documents
        *  Write out the following to output files
            1. doc_lengths.txt      contains doc_id to document lengths for normalization
            2. metadata.txt         contains mapping from reduced doc_id to original doc_id and its court ranking
            3. postings.txt         postings.txt is written out term by term in order to obtain address for individual postings lists
            4. dictionary.txt       points a term to its postings list in postings.txt via a byte offset

        == Searching pseudocode ==

        * Load in term dictionary, document length dictionary, metadata, and queries
        * Parse the query (includes cleaning) to retrieve different query types as follows:
            Term is defined as either a word or a phrase
            1. free text list consisting of all individual words within the query string
            2. phrases list consisting of two or three words surrounded by double quotes like "__ __" or "__ __ __"
            3. words list consisting of words that are not part of a phrase, i.e. not wrapped around double quotes
            4. boolean flag indicating presence of 'AND' operator in the query string. Note, we assume that boolean operations always contain "AND" between every term in the query string,

            e.g. "fertility treatment" AND damages (query 3 provided)
                --> free_text = ['damag', 'fertil', 'treatment']
                --> phrases = [ ['fertil', 'treatment'] ]
                --> words = [ ['damag'] ]
                --> is_boolean = True

        * Query expansion
            * Adding new words
                * With each individual term in the free text list, generate a list of synonyms using wordnet
                * These synonyms will be stored in a synonym dictionary where each term will be mapped to its generated synonyms
                * Clean and perform a check on each synonym
                    * If synonym exists in the term dictionary, calculate the similarity score between the original term and the synonym using the trained word2vec model and map it to the corresponding synonym
                * For each word in the free text array, return the most similar synonym (if any) to a new dictionary. This method may potentially result in up to 100% increase in number of terms potentially reducing precision (especially if many false positives are returned)
                * In the new dictionary, calculate the similarity between each synonym and all words in the original query and append them to a list in descending order of similarity score with all query terms.
                * Append to the free text array and word array the synonym with the greatest similarity score with all original query terms
            * Adding new phrases
                * If the original query has phrases
                    * No change
                * Else,
                    * Permute every possible pair of words in the free_text list and append to phrases list to generate artificial phrases

        * Scoring
            1. Get baseline score through freetext query result, on the assumption of "OR" between every individual token (modified homework 3)
                * Conduct lnc.ltc ranking scheme with cosine normalization using the expanded free text list
                    * create term_freq dictionary for the query
                    * for expanded free text list, for each term,
                        * retrieve postings list for the specific term by accessing dictionary and getting byte offset required in postings.txt
                        * calculate w(t,d) and w(t,q) using postings list
                        * push the retrieved posting list into a holding list for subsequent use beyond free text
                    *  normalize the scores for the documents using document length to create a baseline score

            2. Generate score modifiers for phrases
                * Using the list of phrases generated, consolidate a count of the number of phrases matched. We perform pairwise check so as to assign some extra score for partial phrase match. e.g phrase "a b c" receives some score for "a b", even if "b c" is not in the document. The more (partial) phrases that match the higher the score
                    * For each phrase in phrases, if phrase is three words like "a b c", split the phrase into two like "a b" and "b c"
                    * For each phrase, split into the individual words and retrieve their postings list from the holding list for all postings list of all terms in free text list
                    * utilise positional index inside the postings list to find valid documents that contain the phrase
                        * we are utilising positional deltas for the positional index
                            --> Ensure we are summing up the deltas as we try and compare the positions of the two words to find consecutive positional indexes for the two words of the phrase
                        * track the number of occurences of a valid dissected phrase in a document and add the count into a dictionary.
                * The number of valid partial phrase occurences found per document is normalized by the maximum number of valid partial phrases found across all documents. It  will be used later by multiplication with a pre-determined phrasal weight modifier to be added to the base score for free text search

            3. Generate score modifiers for boolean constraints
                * Assume boolean query, even if the underlying is a free text query. get the count of partial intersections of documents between query terms (recall words and phrases are considered terms), e.g. for <a AND b AND c AND d>, if we satisfy <a AND b>, <a AND d>, we still get a count of 2 for the number of partial boolean constraints satisfied. Basically, we count the number of AND (same docID) terms we could find in our corpus.
                    * For every term in the words list and phrases list
                        * Obtain the strict intersection of the valid document ids for that term, using the posting list.
                            * For words, the valid document ids are simply the documents that the word appears in
                            * For terms, the valid document ids are the documents that all words in the phrase appears in
                        * Permute across all possible pairs of terms and compute the intersection of documents
                            * If a document id appears more than once across all terms, then we use the count of the number of terms it appears in in a dictionary
                * We use the count multiplied by a modifier to modify our baseline scores. The more ANDs that match, the higher our score will be.
                    * Normalize the count of partial boolean constaints satisfied over total possible boolean constraints
                    * e.g. <a AND b AND c AND d>, if we satisfy <a AND b>, <a AND d>, we get 2/6 = 0.33 since 2 partial booleans are satisfied, and there are 6 total

            4. Apply net score function
                * Baseline score - scores obtained form lnc.ltc form of tf-idf, on the free_text list
                * Things to modify
                    * Phrases - bump scores up if we match phrases
                        * The more partial phrases matched, the higher the score
                    * Booleans - bump scores up if we match more partial boolean queries
                        * The more partial boolean queries matched, the higher the score
                    * Courts - bump scores up if the court the document is from is important
                        * Court importance is obtained from metadata.txt
                        * The more important the court, the higher the score
                * Different weights are given to the modifiers
                    * We want to assume that if given a free text query, if given no additional information free text searches should be rated higher if they meet additional boolean criteria
                    * However the weightage should be different, after all it was a free text vs a boolean query

                * If is_boolean flag is positive ('AND' is explicitly present in query)
                    * Weigh the boolean modifier higher
                * If is_boolean flag is positive (free text query)
                    * Weigh the phrase modifier higher

                * Example calculation (dummy example)
                    * doc_id = 10 has baseline score of 0.4
                    * it has phrase_modifier = 0.1, boolean_modifier = 0.3, court_modifier = 3, is_boolean = True
                    * modifier weights for is_boolean = True are 3, 5, 1
                    * Final score for doc_id = 10 = 0.4 + 0.1*3 + 0.3*5 + 3*1 = 5.2

            5. Output valid documents
                * Sort the scores in descending order and append the documents in the corresponding order to a list. Remove any possible duplicate documents in the resulting list of documents
                * Write out the valid_doc_ids into the results file


### ========== System Architecture ==========

    Our output files can be inspected through test.py by commenting out the corresponding lines to load the desired file

    == metadata.txt == 

        {   reduced_doc_id:                     example         { 1:
            {   original_doc_id: n,                                 {   'og': 246391,
                court: m                                                'court': 2
            },                                                      },
            ...                                                     ...
        }                                                       }

    == doc_lengths.txt == 

        {   reduced_doc_id: doc_length,         example         {   1: 35.38262208800508,
            ...                                                     ...
        }                                                       }

    == dictionary.txt == 

        {   term: byte offset in postings.txt,  example         {   'telesurveyor': 704477650,
            ...                                                     ...
        }                                                       }

    == postings.txt == 
    
        {   'doc_freq': n,                      example         {   'df': 659,
            'postings_list': [                                      'postings_list': [
                {   'doc_id': m,                                        {   'doc_id': 1,
                    'term_freq': o,                                         'tf': 36,
                    'positions': [1,2,3,4,5...]                             'pos': [0, 9, 38...]
                },                                                      },
                ...                                                     ...
            ]                                                       ]
        },                                                      },
        ...                                                     ...

### ========== Files included with this submission ==========

    == File Sizes ==

        * Total submission size (excluding dataset.csv)             630 MB (within submission limit)
        * Index (postings.txt) file size                            488 MB
        * word2vec model (model.kv) file size                       65.9 MB
        * Additional package file size (total)                      72.5 MB

    == Python Files ==

        * index.py              Generate the the reference files that contain the dictionary, index, metadata, doc_lengths
        * search.py             Used to process a query file and outputs the results
        * clean.py              Our own mython class that is used to clean documents and queries
        * word2vec.py           Trains the word2vec model that is used to evaluate synonyms via cosine similarity
        * vb_encoder.py         Used to perform variable byte encoding on the positional index array in postings_list to save memory

    == Reference Files ==

        * dictionary.txt        Used to point a term to its posting list
        * postings.txt          Contains posting lists for various terms
        * metadata.txt          Used to convert our reduced document IDs into original document IDs
        * doc_lengths.txt       Used to perform normalization when calculating scores

    == Auxilliary Files ==

        * model.kv              The trained word2vec model generated from word2vec.py that is used in search.py
        * README.txt            This document

    == Packages ==

        * nltk_data             Contains wordnet, punkt and stopwords libraries that had to be downloaded
        * progress              Used for progress bars

### ========== Allocation of Work ==========

    We, A0228402N, A0230521Y, A0230632U verify that we have shared the workload equally for this project, and should be graded equally.

### ========== Statement of Individual Work ==========

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

### ========== References ==========

    * https://stackoverflow.com/
        referenced for some syntax
    * http://www.nltk.org/index.html
        to understand how nltk works
    * https://www.nltk.org/howto/stem.html
        referenced for implementation of NLTK snowball stemmer
    * https://nlp.stanford.edu/IR-book/html/htmledition/basic-xml-concepts-1.html
        Referenced for zones and fields
    * https://nlp.stanford.edu/IR-book/html/htmledition/phrase-queries-1.html
        referenced for some ideas on how to process phrase queries
    * https://nlp.stanford.edu/IR-book/html/htmledition/variable-byte-codes-1.html
        referenced for variable byte encoding
    * http://wordnetweb.princeton.edu/perl/webwn
        referenced for generation of synonyms for query expansion
    * https://radimrehurek.com/gensim/models/word2vec.html
        referenced how to create and train a word2vec model for measuring cosine similarity between words


    There was no collaboration with other students
