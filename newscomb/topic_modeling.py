"""
    topic_modeling
    ~~~~~~~~~~~~~~

    Generate topic models from article text
"""

from stop_words import get_stop_words
from gensim import corpora, models
from goose import Goose
from nltk.collocations import BigramCollocationFinder
import nltk
import numpy
import gensim
import lda
import pandas

# Goose is a library to extract data and media from sites
goose = Goose()

from text_cleanup import (tokenize_individual_text,
                          normalize_individual_text,
                          remove_stopwords_from_individual_text,
                          normalize_all_texts_for_collocation,
                          normalize_individual_text_by_title,
                          normalize_titles)




def safely_get_content(html):
    '''
    Given html: Uses goose to extract title and clean text.
    '''

    try:
        article = goose.extract(raw_html=html)
        title = article.title
        text = article.cleaned_text
        content = (title, text)

    except (IndexError, TypeError, RuntimeError):
        pass

    return content


def extract_title_and_text_from_html(html_list):
    '''
    Given a list of each article's html, returns list of tuples
    containing extracted titles and text.
    '''
    import multiprocessing
    pool = multiprocessing.Pool(12)

    articles_list = pool.map(safely_get_content, html_list)

    # articles_list = []

    # for html in html_list:
    #     content = safely_get_content(html)
    #     articles_list.append(content)

    return articles_list


def transpose_tuples_lists(tuple_list):
    '''
    Given a list of tuples, return a single tuple of lists.
    '''

    title_list = []
    article_list = []

    for title, article in tuple_list:
        title_list.append(title)
        article_list.append(article)

    return (title_list, article_list)


def generate_collocations(tokens):
    '''
    Given list of tokens, return collocations
    '''

    ignored_words = nltk.corpus.stopwords.words('english')
    bigram_measures = nltk.collocations.BigramAssocMeasures()

    # Best results with window_size, freq_filter of: (2,1) (2,2) (5,1)
    finder = BigramCollocationFinder.from_words(tokens, window_size = 2)
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
    finder.apply_freq_filter(1)

    colls = finder.nbest(bigram_measures.likelihood_ratio, 5)

    return colls


def display_collocations(articles):
    '''
    Given tuple containing title list and token list, PRINTS results (no return)
    '''

    title_list, token_list = articles

    for i, tokens in enumerate(token_list):
        if title_list[i] != '':
            print('-'*15)
            title = title_list[i]
            print("Title: {}\n".format(title))
            print("Topics:")
            colls = generate_collocations(tokens)

            output = ""

            for tup in colls:
                word1, word2 = tup
                output += "{} {}; ".format(word1, word2)


            print(output[:-2])
            print('-'*15)

        else:
            pass


if __name__ == '__main__':

    dataframe = pandas.read_csv("../data/articles.csv", index_col=False)

    html_list = dataframe['html']
    articles_list = extract_title_and_text_from_html(html_list[:20]) # 20 for testing

    tuple_of_lists = transpose_tuples_lists(articles_list)
    title_list, text_list = tuple_of_lists

    clean_title_list = normalize_titles(title_list)

    collocation_ready_text = normalize_all_texts_for_collocation((clean_title_list, text_list))

    articles = (clean_title_list, collocation_ready_text)
    display_collocations(articles)
