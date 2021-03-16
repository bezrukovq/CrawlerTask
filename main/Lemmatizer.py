# coding=utf-8
import codecs
import string
import pymorphy2
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

# list of symbols to be removed
MARKS = [',', '.', ':', '?', '«', '»', '-', '(', ')', '!', "“", "„", "–", '\'', "—", ';', "”", "...", "\'\'",
         "/**//**/"]
WORDS_TXT = "words.txt"
OUTPUT_TXT = "output.txt"


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


# clear text
def remove_unnecessary_symbols(words):
    # clear text from the unnecessary symbols
    text_without_marks = remove_marks(words)
    text_without_stop_words = remove_stopwords(text_without_marks)
    text_without_numbers = remove_non_alphabet_symbols(text_without_stop_words)
    return text_without_numbers


# remove marks
def remove_marks(words):
    # remove marks words
    filtered_words = list(
        filter(lambda word: (word not in string.punctuation) and (word not in MARKS), words))

    # remove marks symbols
    result = []
    for filtered_word in filtered_words:
        result.append("".join(filter(lambda char: char not in MARKS, filtered_word)))
    return result


# remove stop words and make it to lowercase
def remove_stopwords(words):
    stop_words = set(stopwords.words('russian'))
    filtered_sentences = [word.lower() for word in words if word not in stop_words]
    return filtered_sentences


# remove non alphabetic strings
def remove_non_alphabet_symbols(words):
    return filter(lambda word: word.isalpha(), words)


# write our cleared text into the file
def write_clear_words_into_file(text):
    file = open(WORDS_TXT, "w", encoding="utf-8")
    for word in text:
        file.write(word + '\n')


# the mystery box.
def lemmatize():
    # read clear words
    lst = open(WORDS_TXT, "r", encoding="utf-8")
    words = lst.readlines()

    # dictionary with word-token elements
    lem_dict = {}

    for word in words:
        normal_form = get_normal_form(word.strip())
        if normal_form:
            # if the word doesn't exist, put it as a key
            if normal_form[0] not in lem_dict.keys():
                lem_dict[normal_form[0]] = [word.strip()]
            # if the word already exist, put it's not normal form as a value
            else:
                lem_dict[normal_form[0]].append(word.strip())

    # write our result into output.txt file
    file = open(OUTPUT_TXT, "w", encoding="utf-8")
    for word, tokens in lem_dict.items():
        file.write("{word}:" + word)
        [file.write(" {token}:" + token) for token in set(tokens)]
        file.write("\n")
    file.close()


# get the normal form of the word
def get_normal_form(word):
    tokens = word_tokenize(word)
    analyzer = pymorphy2.MorphAnalyzer()
    normalized_words = []
    for token in tokens:
        if token in string.punctuation:
            continue
        if token in MARKS:
            continue
        normalized_words.append(analyzer.parse(token)[0].normal_form)
    return normalized_words


if __name__ == '__main__':
    # get list with files
    indexes = open("pages/index.txt", "r")
    arr_words = []
    indexes_lines = indexes.readlines()
    file_names = [line[: line.find(" ")] for line in indexes_lines]

    # get all alphabetic words and write it into the file
    for file_name in file_names:
        file_name_txt = "%s.txt" % file_name
        arr_words.extend(parse_words(file_name_txt))
    clear_text = remove_unnecessary_symbols(arr_words)
    write_clear_words_into_file(clear_text)

    # do the lemmatization
    lemmatize()
