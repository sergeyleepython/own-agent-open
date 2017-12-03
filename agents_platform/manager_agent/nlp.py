import nltk

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
# import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests

gazetteer_it = {'code', 'data', 'file', 'java', 'function', 'user', 'android', 'server', 'system', 'error',
                'application', 'html', 'null', 'void', 'online', 'on-line', 'technology', 'internet', 'software',
                'hardware', 'agile', 'scrum', 'programming'}

stop = stopwords.words('english')
extra = ['...', '``', "'re", "'m", "'s", "'ve", "''", 'uh', 'na', "n't", 'oh', "'ll", 'us', 'ok', "'cause",
         'okay', "'d", 'hey', 'fuck', 'right', 'well', 'ha']
full_stop = stop + extra


class TopicsGenerator:
    def __init__(self, tags=None):
        self.__tags = tags if tags is not None else []
        self.history_set = set()
        self.stats = []
        self.corpus = []

    def get_nouns(self, tokens):
        tagged = nltk.pos_tag(tokens)
        nouns = [tag[0] for tag in tagged if tag[1].startswith('N')]
        return nouns

    def lower_case(self, tokens):
        return [t.lower() for t in tokens]

    def no_punct(self, tokens):
        return [t for t in tokens if t not in punctuation]

    def no_stopwords(self, tokens):
        return [t for t in tokens if t.lower() not in full_stop and not t.isdigit()]

    def get_clean(self, tokens):
        tokens0 = self.get_nouns(tokens)
        tokens1 = self.lower_case(tokens0)
        tokens2 = self.no_punct(tokens1)
        tokens3 = self.no_stopwords(tokens2)
        return tokens3

    def get_tfidf(self, corpus, new_doc):
        self.corpus.append(new_doc)
        # full_corpus = self.corpus + [new_doc]
        tf = TfidfVectorizer(analyzer='word', max_df=1)
        tfidf_matrix = tf.fit_transform(self.corpus)
        terms = tf.get_feature_names()
        # sums = tfidf_matrix.sum(axis=0)
        # data = []
        # for col, term in enumerate(terms):
        #     data.append((term, sums[0, col]))

        ranking = []
        for col in tfidf_matrix.nonzero()[1]:
            ranking.append((terms[col], tfidf_matrix[-1, col]))
        ranking = list(set(ranking))
        sorted_ranking = sorted(ranking, key=lambda tup: -tup[1])
        result = [s[0] for s in sorted_ranking[:5]]

        # ranking = pd.DataFrame(data, columns=['term', 'rank'])
        # ranking.sort_values('rank', inplace=True, ascending=False)
        # result = ranking['term'].head(5).tolist()
        return result

    def get_tokens(self, content):
        # print('History Set: {}'.format(len(self.history_set)))
        tokens = word_tokenize(content)
        clean_tokens = self.get_clean(tokens)
        # self.corpus.append(' '.join(clean_tokens))
        clean_tokens_set = set(clean_tokens)
        # print('Current Meeting Full Set: {}'.format(len(clean_tokens)))
        clean_tokens_only = clean_tokens_set.difference(self.history_set)
        # print('Current Meeting Unique Set: {}'.format(len(clean_tokens_only)))
        self.stats.append((len(self.history_set), len(clean_tokens_set), len(clean_tokens_only)))

        new_doc = ' '.join(clean_tokens)
        tfidf_top = self.get_tfidf(self.corpus, new_doc)
        tfidf_top = set(tfidf_top)
        # tfidf_top = tfidf_top.difference(self.history_set)
        print('Candidates: {}'.format(tfidf_top))
        self.history_set = self.history_set.union(clean_tokens_set)
        return tfidf_top

topic_gen_ = TopicsGenerator()
def candidates_wiki_tag_disambiguation(candidates, gazetteer):
    wiki_base_url = 'https://en.wikipedia.org/wiki/'
    topics = []
    for candidate in candidates:
        candidate_url = wiki_base_url + candidate
        result = requests.get(candidate_url)
        if result.status_code == 200:
            c = result.content
            soup = BeautifulSoup(c, "html.parser")
            div = soup.find('div', {'id': 'mw-content-text'})
            p = div.find('p', recursive=True)
            if p and "may refer to:" not in p.text:
                tokens = word_tokenize(p.text)
                tokens = set(topic_gen_.get_clean(tokens))
                if tokens.intersection(gazetteer_it):
                    print('{:15} : POSITIVE'.format(candidate))
                    topics.append(candidate)
                else:
                    print('{:15} : NEGATIVE'.format(candidate))
            else:
                all = []
                ul = div.find_all('ul', recursive=True)
                if ul:
                    for li in ul:
                        tokens = word_tokenize(li.text)
                        tokens = topic_gen_.get_clean(tokens)
                        all.extend(tokens)
                if set(all).intersection(gazetteer):
                    print('{:15} : POSITIVE'.format(candidate))
                    topics.append(candidate)
                else:
                    print('{:15} : NEGATIVE'.format(candidate))
    return topics


if __name__ == '__main__':
    import os
    from os import listdir  # delete

    data_path = '/home/asus/innopolis/NLP/Final_Project/silicon-valley/data'  # delete
    filenames = listdir(data_path)  # delete
    topic_gen = TopicsGenerator()

    for num, filename in enumerate(filenames):
        print(filename)
        print('Iteration {}'.format(num))
        path = os.path.join(data_path, filename)
        with open(path, 'r') as f:
            content = f.read()
        candidates = topic_gen.get_tokens(content)
        topics = candidates_wiki_tag_disambiguation(candidates, gazetteer_it)
        if num > 5: break
        print()
