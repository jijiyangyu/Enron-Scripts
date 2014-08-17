__author__ = 'Xiang to break email into words'

import MySQLdb, nltk, re
import pysentencizer

db = MySQLdb.connect(host='localhost', # your host, usually localhost
                     user="root", # your username
                      passwd="", # your password
                      db="enronrpi") # name of the data base

tag = {'CC': 1, 'CD': 2, 'DT': 3, 'EX': 4, 'FW': 5, 'IN': 6, 'JJ': 7, 'JJR': 8, 'JJS': 9, 'LS': 10,
       'MD': 11, 'NN': 12, 'NNS': 13, 'NNP': 14, 'NNPS': 15, 'PDT': 16, 'POS': 17, 'PRP': 18, 'PRP$': 19, 'RB': 20,
       'RBR': 21, 'RBS': 22, 'RP': 23, 'SYM': 24, 'TO': 25, 'UH': 26, 'VB': 27, 'VBD': 28, 'VBG': 29, 'VBN': 30,
       'VBP': 31, 'VBZ': 32, 'WDT': 33, 'WP': 34, 'WP$': 35, 'WRB': 36, 'NA': 0}

# if check the title of the mail or content of the mail
is_title = 0
# in UCB, use train_master for the following, other use master table, if is_train = "train_" else is_train=""
is_train = "train_"

def build_word_tags_list(cur):
    cur.execute('SELECT id, word, tag_id FROM word_tags')
    word_tags={}
    for row in cur.fetchall():
        word_tags[str(row[1])+'='+tag.keys()[tag.values().index(row[2])]]=int(row[0])
    return word_tags

def get_word_tags_id(word_tags):
    if len(word_tags)==0:
        return 0
    else:
        return max(word_tags.values())

def get_words_list_bk(content):
    text = [word.strip("'") for word in re.findall(r"[\w']+", content.lower())]
    return nltk.pos_tag(text)

def get_words_list(content):
    sentencizer = pysentencizer.Sentencizer()
    return [(word.value.lower(), word.brillTag) for word in sentencizer.sentencize(content)]

def break_words():
    cur = db.cursor()
    word_tags=build_word_tags_list(cur)
    #print word_tags
    #for word in word_tags:
    #   print word_tags[word], word
    if is_title==1:
       cur.execute('SELECT id, subject FROM ' + is_train + "master")
    else:
       cur.execute('SELECT id, content FROM ' + is_train + "master")
    i = 0
    for row in cur.fetchall():
        words={}
        for word in get_words_list(row[1]):
            if len(word[0]) > 0 and tag.has_key(word[1]):
               if not word_tags.has_key(word[0] + "=" + word[1]):
                  word_tags[word[0] + "=" + word[1]] = get_word_tags_id(word_tags) + 1
                  # print get_word_tags_id(word_tags), len(word[0] + "=" + word[1])
                  cur.execute('insert into word_tags (id, word, tag_id) values(%s,%s,%s);',[get_word_tags_id(word_tags), word[0], tag[word[1]]])
               if words.has_key(str(row[0])+ "=" + str(word_tags[word[0] + "=" + word[1]])):
                  words[str(row[0])+ "=" + str(word_tags[word[0] + "=" + word[1]])] = words[str(row[0])+ "=" + str(word_tags[word[0] + "=" + word[1]])] + 1
               else:
                  words[str(row[0])+ "=" + str(word_tags[word[0] + "=" + word[1]])] = 1
        print "Now working on mail-" + str(row[0])
        for key in words.keys():
            # in UCB, use train_words for the following, other use words table
            cur.execute('insert into ' + is_train + "words" + ' (mail_id, word_id, frequency, is_title) values(%s,%s,%s, %s);',[row[0], key.split("=")[1], words[key], is_title])
        if i < 300:
           i = i + 1
        else:
           print "commiting..."
           i = 0
           db.commit()
    db.commit()
    cur.close()

def main():
    break_words()

if __name__ == '__main__':
    main()
           
