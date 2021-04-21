import os
import pickle
import chardet
import csv
import vb_encoder

csv.field_size_limit(2 ** 30)


def detect_encoding():
    # look at the first ten thousand bytes to guess the character encoding
    with open("dataset.csv", 'rb') as rawdata:
        result = chardet.detect(rawdata.read(1000000))

    # check what the character encoding might be
    return(result["encoding"])


def check_text():
    encoding = detect_encoding()
    with open("dataset.csv", newline='', encoding='utf-8') as csvfile:
        # Read in CSV dataset and remove headers from consideration
        csv_reader = csv.reader(csvfile)
        next(csv_reader, None)

        # Print rows
        for row in csv_reader:
            print(row)


def load_postings(address):
    f_postings = open(
        os.path.join(os.path.dirname(__file__), "postings.txt"), "rb"
    )

    f_postings.seek(address)
    postings_list = pickle.load(f_postings)
    f_postings.close()
    
    for postings in postings_list["postings_list"]:
        postings["positions"] = vb_encoder.decode(postings["positions"])
        
    return postings_list


def load_dictionary():
    f_dict = open(
        os.path.join(os.path.dirname(__file__), "dictionary.txt"), "rb"
    )

    dictionary = pickle.load(f_dict)
    f_dict.close()
    # print(dictionary)
    return dictionary


def load_metadata():
    f_metadata = open(
        os.path.join(os.path.dirname(__file__), "metadata.txt"), "rb"
    )

    metadata = pickle.load(f_metadata)
    f_metadata.close()
    print(metadata)


def load_doc_lengths():
    f_doc_lengths = open(
        os.path.join(os.path.dirname(__file__), "doc_lengths.txt"), "rb"
    )

    doc_lengths = pickle.load(f_doc_lengths)
    f_doc_lengths.close()
    print(doc_lengths)


# # printing dictionary
# print("====================")
dicti = load_dictionary()

# # printing a posting list
# print("====================")
i = 1
for key in dicti.keys():
    if i == 1:
        print("{}: {}".format(key, load_postings(dicti[key])))
        print("--------------")
        i += 1

# # printing metadata
# print("====================")
# load_metadata()

# # printing doc_lengths
# print("====================")
# load_doc_lengths()


# # detect encoding
# print("====================")
# print(detect_encoding())
# check_text()
