import json
import os
import nltk
import re
from math import log
from nltk.tokenize import word_tokenize
from porter2stemmer import Porter2Stemmer
from nltk.stem import PorterStemmer
from collections import defaultdict
from bs4 import BeautifulSoup
nltk.download('punkt')


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
        #print(f'{self.frequency} : {type(self.frequency)}')
        #print(f'{total_files} : {type(total_files)}')
        #print(f'{len(index_table)} : {type(len(index_table))}')
        self.tf_idf = (1 + log(self.frequency)) * log(total_files / length)
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['doc_id'], data['field'], data['frequency'])
        obj.tf_idf = data['tf_idf']
        return obj


def process_text(text):
    text = text.lower()
    
    text = re.sub(r'\\u[\da-fA-F]{4}', '', text)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'//\S+', '', text)
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\\', '', text)
    text = re.sub(r'\b[a-zA-Z0-9]+:[0-9TtZz\-]+', '', text)
    text = re.sub(r'(=)\1{3,}', '', text)
    return text


def extract_first_part_of_path(path):
    parts = path.strip('/').split('/')
    #print(parts)
    if parts:
        if parts[0] in ["http:", "https:"]:
            return parts[2]
        return parts[0]
    return None


def eval_json_files(path):
    global doc_id
    global index_table
    for folder in os.listdir(path):
        folder = os.path.join(path, folder)
        for file in os.listdir(folder):
            file = os.path.join(folder, file)
            print(f"{doc_id} -> {file}")
            file_table[doc_id] = file
            build_index(file)
            doc_id += 1
            if doc_id == 13838:
                f_1 = open("index_table_part_1.json", "x")
                serializable_index = {word: [posting.to_dict() for posting in postings] for word, postings in index_table.items()}
                json.dump(serializable_index, f_1)
                f_1.close()
                index_table = dict()
            elif doc_id == 27696:
                f_1 = open("index_table_part_2.json", "x")
                serializable_index = {word: [posting.to_dict() for posting in postings] for word, postings in index_table.items()}
                json.dump(serializable_index, f_1)
                f_1.close()
                index_table = dict()
            elif doc_id == 45144:
                f_1 = open("index_table_part_3.json", "x")
                serializable_index = {word: [posting.to_dict() for posting in postings] for word, postings in index_table.items()}
                json.dump(serializable_index, f_1)
                f_1.close()
                index_table = dict()
            elif doc_id == 55393:
                f_1 = open("index_table_part_4.json", "x")
                serializable_index = {word: [posting.to_dict() for posting in postings] for word, postings in index_table.items()}
                json.dump(serializable_index, f_1)
                f_1.close()
                index_table = dict()


def build_index(path):
    file = open(path, 'r', encoding = "utf-8")
    content = json.load(file)
    fields = {"title": content.get('title',''), "body": '', "important": ""}

    parsed = BeautifulSoup(content.get('content',''), 'html.parser')
    tags = parsed.find_all(['h1', 'h2', 'h3', 'b', 'strong'])
    fields["important"] = ' '.join(tag.get_text() for tag in tags)
    text = parsed.get_text()
    fields["body"] = text
    for field, text in fields.items():
        text = process_text(text)
        tokens = word_tokenize(text)
        for word in tokens:
            word = extract_first_part_of_path(word)
            if word.endswith("."):
                word = word[:-1]
            #print(word)
            word = stemmer.stem(word).lower()
            if len(word) > 1 and not word.isdigit():
                if word not in index_table:
                    index_table[word] = []
                existing_posting = next((p for p in index_table[word] if p.doc_id == doc_id and p.field == field), None)
                if existing_posting:
                    existing_posting.increment_frequency()
                else:
                    index_table[word].append(Posting(doc_id, field, 1))
    file.close()


def load_and_combine(files):
    combined_index_table = dict()
    for f in files:
        with open(f, 'r') as file:
            data = json.load(file)
            for word, posting_data in data.items():
                if word not in combined_index_table:
                    combined_index_table[word] = []
                for posting in posting_data:
                    combined_index_table[word].append(Posting.from_dict(posting))
    return combined_index_table


def secondary_index(index_table):
    offsets = {}
    f_1 = open("index_table.txt", "w+")
    for word, postings in index_table.items():
        entry = json.dumps({word: [posting.to_dict() for posting in postings]})
        offsets[word] = f_1.tell()
        f_1.write(entry + '\n')
    f_2 = open("offset_table.txt", "w+")
    json.dump(offsets, f_2)


def calculate_tf_idf_index_table():
    total_files = doc_id
    for word, postings in index_table.items():
        unique = set(postings.doc_id for postings in postings)
        for posting in postings:
            posting.calculate_tf_idf(total_files, len(unique))


if __name__ == '__main__':
    index_table = {}
    file_table = {}
    doc_id = 0
    stemmer = Porter2Stemmer()

    path = "developer/DEV"
    eval_json_files(path)
    files = ["index_table_part_1.json", "index_table_part_2.json", "index_table_part_3.json", "index_table_part_4.json"]
    index_table = load_and_combine(files)
    calculate_tf_idf_index_table()
    unique_tokens = len(index_table)
    total_files = doc_id
    f = open("report.txt", "w+")
    f.write(f'total unique tokens {unique_tokens}')
    f.write(f'total files searched {total_files}')
    secondary_index(index_table)
    file_size = os.path.getsize("index_table.txt")
    f.write(f'size of index table in KB {file_size/1024}')
    f_2 = open("file_table.txt", "w+")
    json.dump(file_table, f_2)
    f.close()
    f_2.close()
