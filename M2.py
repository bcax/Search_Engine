from M1 import Posting
import json
from porter2stemmer import Porter2Stemmer
from urllib.parse import urldefrag
import time


stemmer = Porter2Stemmer()
score = {}
DOC_ID_INDEX = 0
FIELD_INDEX = 1
TF_IDF_INDEX = 2


field_weight = {
    "title" : 2.0,
    "important" : 1.5,
    "body" : 1.0,
}

def load_posting(index_table, offset, word):
    index_table.seek(offset)
    index = index_table.readline().strip()
    #print(index)
    temp = json.loads(index)
    postings = temp[word]
    return postings
        

def term_at_a_time(index_table: dict, word: str, offset: int):
    postings = load_posting(index_table, offset, word)
    for posting in postings:
        if posting[DOC_ID_INDEX] in score:
            score[posting[DOC_ID_INDEX]]['score'] += posting[TF_IDF_INDEX] * field_weight[posting[FIELD_INDEX]]
            score[posting[DOC_ID_INDEX]]['terms'].add(word)
        else:
            score[posting[DOC_ID_INDEX]] = {'score': posting[TF_IDF_INDEX] * field_weight[posting[FIELD_INDEX]], 'terms': {word}}


def return_url(stemmed_tokens: list):
    query_terms = set(stemmed_tokens)
    filtered_score = {doc_id: info['score'] for doc_id, info in score.items() if query_terms.issubset(info['terms'])}
    sorted_score = sorted(filtered_score.items(), key = lambda x: -x[1])
    returned_list = []
    count = 0
    for x in sorted_score:
        if count == 10:
            return
        file_name = file_table[str(x[0])]
        f = open(file_name, "r")
        url = urldefrag(json.load(f)['url'])[0]
        if url not in returned_list:
            print(url)
            returned_list.append(url)
            count += 1
        f.close()


if __name__ == '__main__':
    f = open("offset_table.txt", "r")
    f_1 = open("file_table.txt", "r")
    index_table = open("index_table.txt", "r")
    offset_table = json.load(f)
    file_table = json.load(f_1)

    while(1):
        score = {}
        query = input("Enter Query: ")
        start_time = time.time()
        tokens = query.split()
        stemmed_tokens = [stemmer.stem(token).lower() for token in tokens]
        for token in stemmed_tokens:
            #print(token)
            word = stemmer.stem(token).lower()
            try:
                offset = offset_table[word]
                term_at_a_time(index_table, word, offset)
            except KeyError:
                continue
        return_url(stemmed_tokens)
        end_time = time.time()
        elpased_time = end_time - start_time
        print("Time taken: ", elpased_time, " seconds")





   

