__author__ = 'Aakash'

import re
import sqlite3
from collections import Counter
from string import punctuation
from math import log
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet


# initialize the connection to the database
connection = sqlite3.connect('wrcdb123.sqlite')
cursor = connection.cursor()

# create the tables needed by the program
try:
    # create the table containing the wordsh
    cursor.execute('''
        CREATE TABLE newquestions (
            newquestion TEXT,
            numb INT NOT NULL DEFAULT 0
        )''')

    cursor.execute('''

        CREATE TABLE words (
            word TEXT UNIQUE
        )
    ''')



    # create the table containing the sentences
    cursor.execute('''
        CREATE TABLE sentences (
            sentence TEXT UNIQUE,
            used INT NOT NULL DEFAULT 0
        )''')
    # create association between weighted words and the next sentence
    cursor.execute('''
        CREATE TABLE associations (
            word_id INT NOT NULL,
            sentence_id INT NOT NULL,
            weight REAL NOT NULL)
    ''')
except:
    pass


def get_id(entityName, text):
    """Retrieve an entity's unique ID from the database, given its associated text.
    If the row is not already present, it is inserted.
    The entity can either be a sentence or a word."""
    tableName = entityName + 's'
    columnName = entityName

    # print(tableName)
    #print(text)
    cursor.execute('SELECT rowid FROM ' + tableName + ' WHERE ' + columnName + ' = ?', (text,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO ' + tableName + ' (' + columnName + ') VALUES (?)', (text,))
        return cursor.lastrowid


def get_words(text):
    """Retrieve the words present in a given string of text.
    The return value is a list of tuples where the first member is a lowercase word,
    and the second member the number of time it is present in the text."""

    # sky
    # wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
    #
    # wordsRegexp = re.compile(wordsRegexpString)
    # wordsList = wordsRegexp.findall(text.lower())
    sentence = text
    conjunction = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('C')]
    adverbs = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('R')]
    prep = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('I')]
    adj = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('J')]
    MV = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('MD')]
    pronoun = [token for token, pos in pos_tag(word_tokenize(sentence)) if pos.startswith('P')]
    stoken =((word_tokenize(sentence)))

    list = ['is', 'am', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'shall', 'would', 'should', 'been','i']
    nlist=['not','never','no','neither','nor','noone']
    a = stoken
    result1  = [word for word in a if word.lower() not in conjunction]
    result2  = [word for word in result1 if word.lower() not in adverbs]
    result3  = [word for word in result2 if word.lower() not in prep]
    #result4  = [word for word in result3 if word.lower() not in adj]
    result4 = result3
    result5  = [word for word in result4 if word.lower() not in MV]
    result6  = [word for word in result5 if word.lower() not in pronoun]
    result  = [word for word in result6 if word.lower() not in list]
    resultwords = result
    b = [word for word in stoken if word.lower() in nlist]
    if b:
        resultwords = resultwords + nlist
    # print (resultwords)
    #print (list)
    synonyms = []
    for n in resultwords:
        for syn in wordnet.synsets(n):
            for l in syn.lemmas():
                aa=synonyms.append(l.name())





# print (resultwords)

#wordsList = nouns + verbs
#sky
#print(wordsList)
#print (Counter(wordsList).items())

    # return Counter(resultwords).items()
    resultwords = synonyms + resultwords
    if not resultwords:
        bemorespecific = ['bemorespecific']
        resultwords = resultwords + bemorespecific
    # print (resultwords)
    return Counter(resultwords).items()

B = 'Hello'
while True:
    # output bot's message
    print('B: ' + B)
    # ask for user input; if blank line, exit the loop
    H = input('H: ').strip()
    if H == '':
        break


    # store the association between the bot's message words and the user's response
    # words = get_words(B)
    # sentence_id = get_id('sentence', H)
    #

    # for word, n in words:
    #    word_id = get_id('word', word)
    #
    #
    #    test = word.lower()
    #    sum = 0
    #    a = 1
    #    for character in test:
    #         num = ord(character) - 96
    #         sum = sum + num *a
    #         a = a*10
    #         out= (abs(sum))
    #    weight = log(out, 5)
    #    cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
    #    connection.commit()
    # retrieve the most likely answer from the database
    cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    words = get_words(H)
    #words_length = sum([n * len(word) for word, n in words])
    for word, n in words:
        test = word.lower()
        sum = 0
        a = 1
        for character in test:
            num = ord(character) - 96
            sum = sum + num * a
            a = a * 10
            out = (abs(sum))
        weight = log(out, 5)


        #weight = sqrt(n / float(words_length))
        cursor.execute(
            'INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?',
            (weight, word,))
    # if matches were found, give the best one
    cursor.execute(
        'SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    row = cursor.fetchone()
    cursor.execute('DROP TABLE results')
    # otherwise, just randomly pick one of the least used sentences
    if row is None:
        newquestion_id = get_id('newquestion', H)
        # cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        cursor.execute('Update newquestions SET numb=numb+1 WHERE rowid=?', (newquestion_id,))
        cursor.execute('SELECT rowid, sentence FROM sentences WHERE rowid = 10')
        row = cursor.fetchone()
    # tell the database the sentence has been used once more, and prepare the sentence
    B = row[1]
    # cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))




