import codecs
import string
import pymorphy2
import math
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
import streamlit as st
import pandas as pd

# list of symbols to be removed
MARKS = [',', '.', ':', '?', '«', '»', '-', '(', ')', '!', "“", "„", "–", '\'', "—", ';', "”", "...", "\'\'",
         "/**//**/"]
WORDS_TXT = "words.txt"
OUTPUT_TXT = "output.txt"
INVERTED_INDEX_TXT = "inverted_index.txt"
WORDS_COUNT_TXT = "words_count.txt"
TF_IDF_TXT = "tf_idf.txt"
INDEX_TXT = "pages/index.txt"
DOCS_COUNT = 105


# parse text from html
def parse_words(html_file):
    file_path = "pages/" + html_file
    page_html = codecs.open(file_path, 'r', 'utf-8')
    html = page_html.read()
    soup = BeautifulSoup(html, features='html.parser')

    # remove html symbols
    for script in soup(
            ["script", "style", "meta", "link", "span", "a", "time", "button", "li", "dt", "h2", "h3", "legend"]):
        script.extract()

    # get words
    text = soup.get_text()
    words = (word.strip() for word in text.split(" "))
    text = ' '.join(word for word in words if word)

    return text.split()


# remove marks
# remove stop words and make it to lowercase
# remove non alphabetic strings
# remove marks words
# remove marks chars
def remove_unnecessary_symbols(words):
    stop_words = set(stopwords.words('russian'))
    filtered_words = set()
    for word in words:
        if ((word not in string.punctuation) and
                (word not in MARKS) and
                (word not in stop_words) and
                (word.isalpha())):
            filtered_words.add(word)

    # remove marks symbols
    result = []
    for filtered_word in filtered_words:
        result.append("".join(filter(lambda char: char, filtered_word)))
    return result


# write our cleared text into the file
def write_clear_words_into_file(text):
    file = open(WORDS_TXT, "a", encoding="utf-8")
    for word in text:
        file.write(word + '\n')
    file.close()


# the mystery box.
def lemmatizing_and_indexing(clear_words, file, index_dict):
    # dictionary with word-token elements
    lem_dict = {}

    for word in clear_words:
        normal_form = get_normal_form(word.strip())
        if normal_form:
            # if the word doesn't exist, put it as a key
            if normal_form[0] not in lem_dict.keys():
                lem_dict[normal_form[0]] = [word.strip()]
            # if the word already exist, put it's not normal form as a value
            else:
                lem_dict[normal_form[0]].append(word.strip())

            # if the word doesn't exist in indexes, put it as a key
            if normal_form[0] not in index_dict:
                index_dict[normal_form[0]] = [file]
                # if the word already exist, put it's not normal form as a value
            else:
                index_dict[normal_form[0]].append(file)

    # write our result into output.txt file
    file = open(OUTPUT_TXT, "a", encoding="utf-8")
    for word, tokens in lem_dict.items():
        file.write("{word}:" + word)
        [file.write(" {token}:" + token) for token in set(tokens)]
        file.write("\n")
    file.close()

    return index_dict


# get the normal form of the word
def get_normal_form(word):
    tokens = word_tokenize(word)
    analyzer = pymorphy2.MorphAnalyzer()
    normalized_words = []
    for token in tokens:
        normalized_words.append(analyzer.parse(token)[0].normal_form)

    return normalized_words


def boolean_search(normal_words, index_dict):
    page_numbers = []
    for word in normal_words.split():
        if word in index_dict:
            page_numbers.append(index_dict[word])

    union = page_numbers[0]
    for numbers in page_numbers:
        union = set(union) & set(numbers)
    return union


# returns dict {file : words_count}
def get_words_count_in_all_docs():
    docs_words_amount = {}
    file = open(WORDS_COUNT_TXT, "w", encoding="utf-8")
    with open("pages/index.txt", "r") as index:
        lines = index.readlines()
        docs_numb = [line[: line.find(" ")] for line in lines]
        for file_name in docs_numb:
            # создаем словарь формата -> номер документа: количество слов
            words = parse_words(f"{file_name}.txt")
            symbols = remove_unnecessary_symbols(words)
            docs_words_amount[file_name] = list(symbols).__len__()
            file.write(file_name + " " + str(docs_words_amount[file_name]) + "\n")

    file.close()
    return docs_words_amount


def compute_tf(in_doc, all_doc):
    return in_doc / float(all_doc)


def compute_idf(numb):
    return math.log10(DOCS_COUNT / float(numb))


def count_tf_idf():
    file = open(TF_IDF_TXT, "w", encoding="utf-8")

    docs_word_count = get_words_count_in_all_docs()
    inv_index_file = open(INVERTED_INDEX_TXT, "r", encoding="utf-8")
    all_tokens_indexes = inv_index_file.readlines()
    for line in all_tokens_indexes:
        line_token_indexes = line.split()

        # dict {file_with_token : times_occurred}
        docs_token_occured_count_dict = {}

        curr_token_from_line = line_token_indexes[0]
        print(curr_token_from_line, end=" : ")
        file.write(curr_token_from_line + " : ")

        for i in range(1, line_token_indexes.__len__()):
            if line_token_indexes[i] in docs_token_occured_count_dict:
                docs_token_occured_count_dict[line_token_indexes[i]] += 1
            else:
                docs_token_occured_count_dict[line_token_indexes[i]] = 1

        for current_doc in docs_token_occured_count_dict:
            count_curr_doc_token_occurred = float(docs_token_occured_count_dict[current_doc])
            count_total_words = docs_word_count[current_doc]
            tf = round(compute_tf(count_curr_doc_token_occurred, count_total_words), 15)

            idf = round(compute_idf(len(docs_token_occured_count_dict)), 15)
            dict_idf[current_doc] = idf

            tf_idf = tf * idf

            print(str(current_doc) + " " + str(idf) + " " + str(tf_idf), end="; ")
            file.write(str(current_doc) + " " + str(idf) + " " + str(tf_idf) + "; ")

        print("\n")
        file.write("\n")

    file.close()


def get_index_dict():
    inv_index_file = open(INVERTED_INDEX_TXT, "r", encoding="utf-8")
    all_tokens_indexes = inv_index_file.readlines()
    index_dict = {}

    for line in all_tokens_indexes:
        line_token_indexes = line.split()
        index_dict[line_token_indexes[0]] = line_token_indexes[1:line_token_indexes.__len__()]

    inv_index_file.close()
    return index_dict


# A dict with idf for every token
def get_idf_dict(docs_count, index_dict):
    idf_dict = {}
    for token in index_dict.keys():
        idf = math.log(docs_count / len(index_dict[token]))
        idf_dict[token] = idf
    return idf_dict


# A dict with idf for every token for every document
def get_tf_idf_dict():
    inv_index_file = open(TF_IDF_TXT, "r", encoding="utf-8")
    all_tokens_files_indexes = inv_index_file.readlines()

    docs_tf_idf_dict = {}

    for line in all_tokens_files_indexes:
        line = line.strip()
        line_token_indexes = line.split(":")
        token = line_token_indexes[0].strip()
        docs_tf_idf = line_token_indexes[1].split(";")
        for docs_tf_idf_item in docs_tf_idf:
            if docs_tf_idf_item != "":
                values = docs_tf_idf_item.split()
                doc = str(values[0])
                if doc not in docs_tf_idf_dict:
                    docs_tf_idf_dict[doc] = {}

                tf = values[1]
                idf = values[2]
                docs_tf_idf_dict[doc][token] = idf

    inv_index_file.close()
    return docs_tf_idf_dict


# A dict with words count
def get_words_count_in_all_docs_dict():
    inv_index_file = open(WORDS_COUNT_TXT, "r", encoding="utf-8")
    all_tokens_files_indexes = inv_index_file.readlines()

    words_count_dict = {}

    for line in all_tokens_files_indexes:
        line = line.strip()
        line_token_indexes = line.split()
        words_count_dict[line_token_indexes[0]] = line_token_indexes[1]

    inv_index_file.close()
    return words_count_dict


# A dict with links to file
def get_file_link_dict():
    index_file = open(INDEX_TXT, "r", encoding="utf-8")
    url_lines = index_file.readlines()

    words_count_dict = {}

    for line in url_lines:
        line = line.strip()
        line_token_indexes = line.split("->")
        words_count_dict[line_token_indexes[0].strip()] = line_token_indexes[1].strip()

    index_file.close()
    return words_count_dict


def vector_search(text_to_search, index_dict, idf_dict, lengths_dict, docs_tf_idf_dict):
    words = text_to_search.split()
    normal_words = [get_normal_form(word)[0] for word in words]

    # list of pages which contains the words
    pages = boolean_search(text_to_search, index_dict)

    # count of words in the text
    words_count = len(normal_words)

    # dict which contains number of each word in the next
    words_count_dict = {}
    for word in normal_words:
        if word not in words_count_dict:
            words_count_dict[word] = 1
        else:
            words_count_dict[word] += 1

    # tf of every word in the text
    tf_dict = dict.fromkeys(words_count_dict.keys())
    for word in words_count_dict.keys():
        tf_dict[word] = words_count_dict[word] / words_count

    # tf-idf every word in the text
    tf_idf_dict = dict.fromkeys(tf_dict.keys())
    for word in tf_dict.keys():
        tf_idf_dict[word] = tf_dict[word] * idf_dict.get(word)

    # length of the text
    tf_idf_sum = 0
    for word in tf_idf_dict.keys():
        tf_idf_sum += tf_idf_dict[word] * tf_idf_dict[word]
    text_length = math.sqrt(tf_idf_sum)

    cos_sim_dict = dict.fromkeys(pages)

    # cosine similarity
    for page_num in pages:
        cos_sim_dict[page_num] = vector_distance(
            tf_idf_dict,
            docs_tf_idf_dict[page_num],
            text_length,
            lengths_dict[page_num]
        )

    cos_sim_list = sorted(cos_sim_dict.items(), key=lambda distance: distance[1], reverse=True)

    sorted_pages_list = []
    for item in cos_sim_list:
        sorted_pages_list.append(item[0])
    links_list = [dict_file_to_link[file] for file in sorted_pages_list]
    print(links_list)
    df = pd.DataFrame(links_list)
    st.table(df)
    return sorted_pages_list


def vector_distance(tf_idf_dict_x, tf_idf_dict_y, length_x, length_y):
    cos_sim_sum = 0
    for token in tf_idf_dict_x.keys():
        if token in tf_idf_dict_y.keys():
            cos_sim_sum += tf_idf_dict_x[token] + float(tf_idf_dict_y[token])
    cos_sim = cos_sim_sum / (length_x * float(length_y))
    return cos_sim


if __name__ == '__main__':
    dict_index = get_index_dict()
    dict_idf = get_idf_dict(DOCS_COUNT, dict_index)
    dict_length = get_words_count_in_all_docs_dict()
    dict_docs_tf_idf = get_tf_idf_dict()
    dict_file_to_link = get_file_link_dict()
    st.title('Поисковая система')
    title = st.text_input('Найти')
    if st.button('Поиск'):
        st.write('Результаты по запросу - ', title)
        vector_search(title, dict_index, dict_idf, dict_length, dict_docs_tf_idf)
