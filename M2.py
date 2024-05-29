from M1 import Posting
import json
from porter2stemmer import Porter2Stemmer
from urllib.parse import urldefrag
from math import log


stemmer = Porter2Stemmer()
score = {}

field_weight = {
    "title" : 2.0,
    "important" : 1.5,
    "body" : 1.0,
}
"""
class Posting:
    def __init__(self, doc_id, field, frequency = 0) -> None:
        self.doc_id = doc_id
        self.field = field
        self.frequency = frequency
        self.tf_idf = 0.0

    def increment_frequency(self):
        self.frequency += 1
    
    def to_dict(self):
        return {
            "doc_id" : self.doc_id,
            "frequency" : self.frequency,
            "field" : self.field,
            "tf_idf" : self.tf_idf
        }
    
    def calculate_tf_idf(self, total_files, length):
        self.tf_idf = (1 + log(self.frequency)) * log(total_files / length)
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['doc_id'], data['field'], data['frequency'])
        obj.tf_idf = data['tf_idf']
        return obj
"""

def load_posting(index_table, offset, word):
    index_table.seek(offset)
    index = index_table.readline().strip()
    #print(index)
    temp = json.loads(index)
    postings = temp[word]
    return [Posting.from_dict(posting) for posting in postings]
        

def term_at_a_time(index_table: dict, word: str, offset: int):
    postings = load_posting(index_table, offset, word)
    for posting in postings:
        if posting.doc_id in score:
            score[posting.doc_id] += posting.tf_idf * field_weight[posting.field]
        else:
            score[posting.doc_id] = posting.tf_idf * field_weight[posting.field]


def return_url():
    sorted_score = sorted(score.items(), key = lambda x: -x[1])
    returned_list = []
    count = 0
    for x in sorted_score:
        if count == 5:
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
        tokens = query.split()
        for token in tokens:
            #print(token)
            word = stemmer.stem(token).lower()
            try:
                offset = offset_table[word]
                term_at_a_time(index_table, word, offset)
            except KeyError:
                continue
        return_url()





   

