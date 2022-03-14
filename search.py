import pandas as pd
import numpy as np
import difflib
from bs4 import BeautifulSoup
import spacy
import unidecode
from word2number import w2n
import contractions


nlp = spacy.load('ru_core_news_sm')

deselect_stop_words = ['no', 'not']
for w in deselect_stop_words:
    nlp.vocab[w].is_stop = False


def strip_html_tags(text):
    """remove html tags from text"""
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def remove_whitespace(text):
    """remove extra whitespaces from text"""
    text = text.strip()
    return " ".join(text.split())


def remove_accented_chars(text):
    """remove accented characters from text, e.g. café"""
    text = unidecode.unidecode(text)
    return text


def expand_contractions(text):
    """expand shortened words, e.g. don't to do not"""
    text = contractions.fix(text)
    return text


def text_preprocessing(text, accented_chars=True, contractions=True, 
                       convert_num=True, extra_whitespace=True, 
                       lemmatization=True, lowercase=True, punctuations=True,
                       remove_html=True, remove_num=True, special_chars=True, 
                       stop_words=True):
  
    """preprocess text with default option set to true for all steps"""
    if remove_html == True: #remove html tags
        text = strip_html_tags(text)
    if extra_whitespace == True: #remove extra whitespaces
        text = remove_whitespace(text)
    if accented_chars == True: #remove accented characters
        text = remove_accented_chars(text)
    if contractions == True: #expand contractions
        text = expand_contractions(text)
    if lowercase == True: #convert all characters to lowercase
        text = text.lower()

    doc = nlp(text) #tokenise text

    clean_text = []
    
    for token in doc:
        flag = True
        edit = token.text
        # remove stop words
        if stop_words == True and token.is_stop and token.pos_ != 'NUM': 
            flag = False
        # remove punctuations
        if punctuations == True and token.pos_ == 'PUNCT' and flag == True: 
            flag = False
        # remove special characters
        if special_chars == True and token.pos_ == 'SYM' and flag == True: 
            flag = False
        # remove numbers
        if remove_num == True and (token.pos_ == 'NUM' or token.text.isnumeric()) \
        and flag == True:
            flag = False
        # convert number words to numeric numbers
        if convert_num == True and token.pos_ == 'NUM' and flag == True:
            edit = w2n.word_to_num(token.text)
        # convert tokens to base form
        elif lemmatization == True and token.lemma_ != "-PRON-" and flag == True:
            edit = token.lemma_
        # append tokens edited and not removed to list 
        if edit != "" and flag == True:
            clean_text.append(edit)       
    return clean_text


async def similarity(ms):
    df = pd.read_json('./channel_messages.json')
    for i in df.message:
        normalized1 = text_preprocessing(text= i, accented_chars=False, contractions=True, 
                       convert_num=False, extra_whitespace=True, 
                       lemmatization=False, lowercase=True, punctuations=True,
                       remove_html=True, remove_num=False, special_chars=True, 
                       stop_words=True)
        normalized2 = text_preprocessing(text= ms, accented_chars=False, contractions=True, 
                       convert_num=False, extra_whitespace=True, 
                       lemmatization=False, lowercase=True, punctuations=True,
                       remove_html=True, remove_num=False, special_chars=True, 
                       stop_words=True)
        matcher = difflib.SequenceMatcher(None, normalized1, normalized2).ratio()
        if matcher >= 0.35:
            return i, df['channel'].loc[df.message == i].values[0], pd.to_datetime(str(df['date'].loc[df.message == i].values[0])).strftime('%Y.%m.%d %H:%M:%S')