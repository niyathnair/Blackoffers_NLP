# -*- coding: utf-8 -*-
"""Code_Blackcoffer_Assignment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PZ0i3L0xGyP6QHoHAisKf5XFVWvncTAU
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
import re

df = pd.read_excel('/content/drive/MyDrive/20211030 Test Assignment/Input.xlsx')

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('h1', class_='entry-title')
            title = title_tag.get_text(strip=True) if title_tag else "Title not found"
            content_div = soup.find('div', class_='td-post-content tagdiv-type')
            if content_div:
                text = content_div.get_text(strip=True)
                return title, text
            else:
                return title, "Error: div not found"
        else:
            return "Error: Unable to fetch URL", "Error: Unable to fetch URL"
    except Exception as e:
        return str(e), str(e)

def extract_title(html_snippet):
    soup = BeautifulSoup(html_snippet, 'html.parser')
    title = soup.h1.text
    return title

def extract_text_from_url_FNF(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
            if content_div:
                text = content_div.get_text(strip=True)
                return text
            else:
                return "Error: div not found"
        else:
            return "Error: Unable to fetch URL"
    except Exception as e:
        return str(e)

tqdm.pandas()
df[['Title', 'Extracted_Text']] = df['URL'].progress_apply(extract_text_from_url).apply(pd.Series)

df.to_excel('updated_file.xlsx', index=False)
df_new = pd.read_excel('updated_file.xlsx')
df_new.head()

df_new.rename(columns={'URL_ID': 'File_Name'}, inplace=True)
df_new.drop(columns=['URL'], inplace=True)
df_new.head()

df_new.to_csv('work_input.csv', index=False)
dff=pd.read_csv('work_input.csv')

filenames_title_not_found = dff.loc[dff['Title'] == 'Title not found', 'File_Name'].tolist()

print(filenames_title_not_found)
print(len(filenames_title_not_found))

html_snippet = '<h1 class="tdb-title-text">Rise of e-health and its impact on humans by the year 2030</h1>'
dff.loc[dff['Title'] == 'Title not found', 'Title'] = dff.loc[dff['Title'] == 'Title not found'].apply(lambda row: extract_title(html_snippet), axis=1)

filtered_urls = df.loc[dff['File_Name'].isin(filenames_title_not_found), 'URL']
for url in filtered_urls:
    extracted_text = extract_text_from_url_FNF(url)
    dff.loc[df['URL'] == url, 'Extracted_Text'] = extracted_text

dff.iloc[10:20]

"""Cleaning"""

stopwords_folder = "/content/drive/MyDrive/20211030 Test Assignment/StopWords"
stop_words_list = []

for filename in os.listdir(stopwords_folder):
    filepath = os.path.join(stopwords_folder, filename)
    if filename.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                word = ''
                for char in line:
                    if char == '|':
                        break
                    if char != '\n':
                        word += char
                if word.strip():
                    stop_words_list.append(word.strip())

print(stop_words_list)

def clean_text(text, stopwords):
    cleaned_tokens = [token.lower() for token in text.split() if token.lower() not in stopwords and token.isalnum()]
    cleaned_text = ' '.join(cleaned_tokens)
    return cleaned_text

tqdm.pandas(desc="Cleaning Text")
dff['Cleaned_Text'] = dff['Extracted_Text'].progress_apply(lambda x: clean_text(x, stop_words_list))

dff.iloc[10:20]

"""Positive/Negative/PPolarity"""

def calculate_positive_score(text, positive_words):
    positive_count = sum(1 for word in text.split() if word in positive_words)
    return positive_count

def calculate_negative_score(text, negative_words):
    negative_count = sum(1 for word in text.split() if word in negative_words)
    return negative_count

def calculate_polarity_score(positive_score, negative_score):
    denominator = (positive_score + negative_score) + 0.000001
    return (positive_score - negative_score) / denominator

positive_words_file = '/content/drive/MyDrive/20211030 Test Assignment/MasterDictionary/positive-words.txt'
negative_words_file = '/content/drive/MyDrive/20211030 Test Assignment/MasterDictionary/negative-words.txt'

with open(positive_words_file, "r", encoding="utf-8", errors="ignore") as file:
    positive_words = set(file.read().splitlines())

with open(negative_words_file, "r", encoding="utf-8", errors="ignore") as file:
    negative_words = set(file.read().splitlines())

dff['POSITIVE SCORE'] = dff['Cleaned_Text'].apply(lambda x: calculate_positive_score(x, positive_words))
dff['NEGATIVE SCORE'] = dff['Cleaned_Text'].apply(lambda x: calculate_negative_score(x, negative_words))
dff['POLARITY SCORE'] = dff.apply(lambda row: calculate_polarity_score(row['POSITIVE SCORE'], row['NEGATIVE SCORE']), axis=1)

dff.iloc[10:20]

"""Subjectivity Score"""

dff['Word Count'] = dff['Cleaned_Text'].apply(lambda x: len(x.split()))

dff['Subjectivity Score'] = (dff['POSITIVE SCORE'] + dff['NEGATIVE SCORE']) / (dff['Word Count'] + 0.000001)
dff['Subjectivity Score'] = dff['Subjectivity Score'].apply(lambda x: min(max(x, 0), 1))

dff.iloc[10:20]

"""Average sentence length"""

def count_sentences(text):
    sentences = text.split('.')
    total_sentences = len(sentences)
    return total_sentences

dff['Word Count RAW'] = dff['Extracted_Text'].apply(lambda x: len(x.split()))

dff['Sentence count RAW'] = dff['Extracted_Text'].apply(count_sentences)

dff['AVERAGE SENTENCE LENGTH'] = (dff['Word Count RAW']) / (dff['Sentence count RAW'])

dff.iloc[10:20]

def calculate_average_word_length(text):
    words = text.split()
    total_characters = sum(len(word) for word in words)
    total_words = len(words)
    if total_words == 0:
        return 0
    return total_characters / total_words

def calculate_personal_pronouns(text):
    pattern = r'\b(I|we|my|ours|us)\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    count = len(matches)
    return count

def count_syllables(word):
    word = re.sub(r'(es|ed)$', '', word, flags=re.IGNORECASE)
    vowels = 'aeiouAEIOU'
    syllable_count = sum(1 for char in word if char in vowels)
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    syllable_count = max(1, syllable_count)
    return syllable_count

def calculate_syllable_count_per_word(text):
    words = text.split()
    syllable_counts = [count_syllables(word) for word in words]
    return syllable_counts

def count_complex_words(text):
    words = text.split()
    complex_word_count = sum(1 for word in words if count_syllables(word) > 2)
    return complex_word_count

dff['Average Word Length'] = dff['Extracted_Text'].apply(calculate_average_word_length)
dff['Personal Pronouns'] = df['Extracted_Text'].apply(calculate_personal_pronouns)
dff['Syllable Count Per Word'] = dff['Extracted_Text'].apply(calculate_syllable_count_per_word)
dff['Complex Word Count'] = dff['Cleaned_Text'].apply(count_complex_words)

dff.iloc[10:20]

dff.columns

dff['PERCENTAGE OF COMPLEX WORDS'] = (dff['Complex Word Count']) / (dff['Word Count RAW'])
dff['FOG INDEX']=(dff['PERCENTAGE OF COMPLEX WORDS']+dff['AVERAGE SENTENCE LENGTH'])*(0.4)
dff['AVG NUMBER OF WORDS PER SENTENCE']=dff['Word Count RAW']/dff['Sentence count RAW']

dff.columns

dff = dff.rename(columns={
    'POSITIVE SCORE': 'Positive Score',
    'NEGATIVE SCORE': 'Negative Score',
    'POLARITY SCORE': 'Polarity Score',
    'SUBJECTIVITY SCORE': 'Subjectivity Score',
    'Avg Sentence Length': 'Avg Sentence Length',
    'PERCENTAGE OF COMPLEX WORDS': 'Percentage of Complex Words',
    'FOG INDEX': 'Fog Index',
    'AVG NUMBER OF WORDS PER SENTENCE': 'Avg Number of Words per Sentence',
    'Complex Word Count': 'Complex Word Count',
    'Word Count': 'Word Count',
    'Syllable Count Per Word': 'Syllable Per Word',
    'Personal Pronouns': 'Personal Pronouns',
    'Average Word Length': 'Avg Word Length'
})

dff = dff[['File_Name','Title','Extracted_Text','Cleaned_Text','Positive Score', 'Negative Score', 'Polarity Score', 'Subjectivity Score',
         'AVERAGE SENTENCE LENGTH', 'Percentage of Complex Words', 'Fog Index',
         'Avg Number of Words per Sentence', 'Complex Word Count', 'Word Count',
         'Syllable Per Word', 'Personal Pronouns', 'Avg Word Length']]

dff.iloc[10:20]

dff.to_excel('/content/drive/MyDrive/Result.xlsx', index=False)

