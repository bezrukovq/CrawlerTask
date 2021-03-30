import codecs
import string
import pymorphy2
import re
import math
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

# list of symbols to be removed
MARKS = [',', '.', ':', '?', '«', '»', '-', '(', ')', '!', "“", "„", "–", '\'', "—", ';', "”", "...", "\'\'",
         "/**//**/"]
WORDS_TXT = "words.txt"
OUTPUT_TXT = "output.txt"
INDEX_TXT = "inverted_index.txt"


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


def boolean_search(text, index_dict):
    pattern = r"[^\w]"
    text = re.sub(pattern, " ", text)
    words = text.split()

    normal_words = []

    for word in words:
        form = get_normal_form(word)[0]
        normal_words.append(form)

    page_numbers = []
    for word in normal_words:
        if word in index_dict:
            page_numbers.append(index_dict[word])

    union = page_numbers[0]
    for numbers in page_numbers:
        union = union & numbers
    return union

DOCS_COUNT = 105

def get_words_count_from_docs():
    docs_words_amount = {}
    with open("pages/index.txt", "r") as index:
        lines = index.readlines()
        docs_numb = [line[: line.find(" ")] for line in lines]
        for elt in docs_numb:
            # создаем словарь формата -> номер документа: количество слов
            docs_words_amount[elt] = list(remove_unnecessary_symbols(
                parse_words(f"{elt}.html"))).__len__()
    return docs_words_amount


def compute_tf(in_doc, all_doc):
    return in_doc / float(all_doc)


def compute_idf(numb):
    return math.log10(DOCS_COUNT / float(numb))


def count_tf_idf():
    docs_word_count = get_words_count_from_docs()
    inv_index_file = open(INDEX_TXT, "r", encoding="utf-8")
    lines = inv_index_file.readlines()
    for line in lines:
        line_text = line.split()
        line_text[0] = -1
        docs_count = {}
        for docId in line_text:
            docs_count[docId] += 1
        for doc in docs_count:
            tf = round(compute_tf(float(docs_count[doc.key]), docs_word_count[doc.key]), 15)
            idf = round(compute_idf(docs_count.__len__), 15)
            tf_idf = tf * idf
        # TODO save to file in format
            # word: {docId} {idf} {tf-idf}, {docId} {idf} {tf-idf}...


if __name__ == '__main__':
    # clear files
    file = open(OUTPUT_TXT, "w", encoding="utf-8")
    file.close()
    file_words = open(WORDS_TXT, "w", encoding="utf-8")
    file_words.close()

    indexes = open("pages/index.txt", "r")
    indexes_lines = indexes.readlines()
    file_names = [line[: line.find(" ")] for line in indexes_lines]
    index_dict = {}

    # get all alphabetic words and write it into the file of tokens and indexes
    for file_name in file_names:
        file_name_txt = "%s.txt" % file_name
        all_words = parse_words(file_name_txt)
        clear_words = remove_unnecessary_symbols(all_words)
        write_clear_words_into_file(clear_words)
        index_dict = (lemmatizing_and_indexing(clear_words, file_name, index_dict))

    # write indexes into inverted_index.txt
    index_file = open(INDEX_TXT, "w", encoding="utf-8")
    index_dict = dict(sorted(index_dict.items()))
    for word, indexes in index_dict.items():
        index_dict[word] = set(indexes)
        index_file.write(f"{word}")
        [index_file.write(f" {index}") for index in indexes]
        index_file.write("\n")

    index_file.close()
    text = "свежий сайт"
    page_numbers = boolean_search(text, index_dict)
    print(page_numbers)
#     the result will be {'26', '59', '5', '38', '77', '46', '30', '28', '58', '75', '40', '23', '1', '36', '78', '25', '95', '41', '70', '3', '35', '68', '105', '52', '20', '96', '2', '88', '18', '6', '17', '21', '50', '61', '104', '73', '33', '11', '60', '91', '4', '87', '62', '66', '71', '54', '12', '43', '47', '49', '53', '64', '103', '24', '8', '39', '80', '81', '22', '93', '32', '67', '85', '10', '76', '92', '9', '14', '89', '94', '51', '7', '74', '16', '99', '13', '69', '55', '72', '83', '42', '34', '44', '102', '86', '97', '63', '57', '19', '27', '90', '15', '29', '48', '37', '82', '79', '98', '65'}
