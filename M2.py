from flask import Flask, request, render_template
from porter2stemmer import Porter2Stemmer
from urllib.parse import urldefrag
import json
import time

app = Flask(__name__)

stemmer = Porter2Stemmer()
score = {}
DOC_ID_INDEX = 0
FIELD_INDEX = 1
TF_IDF_INDEX = 2

field_weight = {
    "title": 2.0,
    "important": 1.5,
    "body": 1.0,
}

def load_posting(index_table, offset, word):
    index_table.seek(offset)
    index = index_table.readline().strip()
    temp = json.loads(index)
    postings = temp[word]
    return postings

def term_at_a_time(index_table: dict, word: str, offset: int):
    postings = load_posting(index_table, offset, word)
    for posting in postings:
        doc_id = posting[DOC_ID_INDEX]
        if doc_id in score:
            score[doc_id]['score'] += posting[TF_IDF_INDEX] * field_weight[posting[FIELD_INDEX]]
            score[doc_id]['terms'].add(word)
        else:
            score[doc_id] = {'score': posting[TF_IDF_INDEX] * field_weight[posting[FIELD_INDEX]], 'terms': {word}}

def return_url(query_tokens):
    query_terms_set = set(query_tokens)
    filtered_score = {doc_id: info['score'] for doc_id, info in score.items() if query_terms_set.issubset(info['terms'])}
    sorted_score = sorted(filtered_score.items(), key=lambda x: -x[1])
    returned_list = []
    count = 0
    for x in sorted_score:
        if count == 10:
            break
        file_name = file_table[str(x[0])]
        with open(file_name, "r") as f:
            url = urldefrag(json.load(f)['url'])[0]
            if url not in returned_list:
                returned_list.append(url)
                count += 1
    return returned_list

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        start_time = time.time()
        score.clear()
        tokens = query.split()
        stemmed_tokens = [stemmer.stem(token).lower() for token in tokens]
        for token in stemmed_tokens:
            try:
                offset = offset_table[token]
                term_at_a_time(index_table, token, offset)
            except KeyError:
                continue

        results = return_url(stemmed_tokens)
        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_time_ms = round(elapsed_time * 1000)
        return render_template('results.html', query=query, results=results, time=elapsed_time_ms)
    return render_template('index.html')

if __name__ == '__main__':
    with open("offset_table.txt", "r") as f:
        offset_table = json.load(f)
    with open("file_table.txt", "r") as f_1:
        file_table = json.load(f_1)
    index_table = open("index_table.txt", "r")
    app.run(debug=True)