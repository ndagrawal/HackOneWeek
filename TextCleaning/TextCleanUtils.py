import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def remove_emails(text):
    return re.sub('[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]', ' ', text)


def remove_ip(text):
    return re.sub('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', ' ',
                  text)

def html2text(text):
    # Remove Html tags
    text = BeautifulSoup(text, "lxml").get_text(' ')
    text = re.sub('<[^>\s]+>', ' ', text)

    ## Remove other xml tags in second pass
    text = BeautifulSoup(text, "lxml").text
    
    return text

def remove_guids(text):
    return re.sub('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', ' ', text)


def keep_only_alpha_numeric(text):
    return re.sub('[\W_]+', ' ', text)


def remove_non_ascii(text):
    return text.encode("ascii", errors="ignore").decode()


def remove_numbers(words):
    return re.sub(r'\w*\d\w*', ' ', words).strip()


def reduce_lengthening(text):
    """
    Replace repeated character sequences of length 3 or greater with sequences
    of length 3.
    """
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1\1", text)


def camel_case_split(text):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace('_', ' ')


stops = set(stopwords.words("english"))


def remove_stop_words(text):
    words = text.split()
    non_stop_words = [word for word in words if word not in stops]
    return ' '.join(non_stop_words)


lemmer = WordNetLemmatizer()


def lemmatize(text):
    words = text.split()
    lemmatized_words = []
    for word in words:
        lemmatized_words.append(lemmer.lemmatize(word))
    return ' '.join(lemmatized_words)


def lemmatize_verbs(text):
    words = text.split()
    lemmatized_words = []
    for word in words:
        lemmatized_words.append(lemmer.lemmatize(word, 'v'))
    return ' '.join(lemmatized_words)


stemmer = SnowballStemmer('english')


def stem_words(text):
    words = text.split()
    stemmed_words = []
    for word in words:
        stemmed_words.append(stemmer.stem(word))
    return ' '.join(stemmed_words)


default_repro = '<b>Affected Branch:</b> <br> <b>Affected Build:</b> <br> <b>Affected Product Language:</b> <br> <br><b>Steps to reproduce:</b><br> <br> 1.'

def remove_single_char(text):
    words = text.split()
    return ' '.join([word for word in words if len(word) > 1])

def clean_text(text, stem=False):
    text = html2text(text)
    text = remove_emails(text)
    text = remove_guids(text)
    text = remove_ip(text)
    text = keep_only_alpha_numeric(text)
    text = remove_numbers(text)
    text = remove_non_ascii(text)
    text = reduce_lengthening(text)
    text = camel_case_split(text)
    text = remove_stop_words(text)
    text = lemmatize(text)
    text = lemmatize_verbs(text)
    text = remove_single_char(text)
    if stem:
        text = stem_words(text)
    return text