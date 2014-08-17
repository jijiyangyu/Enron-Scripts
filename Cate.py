__author__ = 'Xiang to category email'

import MySQLdb, nltk, random, sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

db = MySQLdb.connect(host='localhost', # your host, usually localhost
                     user="root", # your username
                      passwd="", # your password
                      db="enronrpi") # name of the data base

tag = {'CC': 1, 'CD': 2, 'DT': 3, 'EX': 4, 'FW': 5, 'IN': 6, 'JJ': 7, 'JJR': 8, 'JJS': 9, 'LS': 10,
       'MD': 11, 'NN': 12, 'NNS': 13, 'NNP': 14, 'NNPS': 15, 'PDT': 16, 'POS': 17, 'PRP': 18, 'PRP$': 19, 'RB': 20,
       'RBR': 21, 'RBS': 22, 'RP': 23, 'SYM': 24, 'TO': 25, 'UH': 26, 'VB': 27, 'VBD': 28, 'VBG': 29, 'VBN': 30,
       'VBP': 31, 'VBZ': 32, 'WDT': 33, 'WP': 34, 'WP$': 35, 'WRB': 36, 'NA': 0}

train_size = 3000
feature_size = 500
use_train_set_only = True

def build_words_mapping(cur):
    cur.execute('SELECT word_id, mapping_id FROM words_mapping')
    word_tags={}
    for row in cur.fetchall():
        word_tags[row[0]] = row[1]
    return word_tags

def build_word_features(cur):
    cur.execute('SELECT word_id, total_frequency FROM words_stat where tag_id in (12, 13, 27, 28, 29, 30, 31, 32) order by total_frequency desc limit %s', [feature_size])
    word_tags={}
    for row in cur.fetchall():
        word_tags[row[0]] = row[1]
    return word_tags

def dic_mapping(dic, words_mapping):
    for key in dic.keys():
        if words_mapping.has_key(key):
            if dic.has_key(words_mapping[key]):
                dic[words_mapping[key]] = dic[words_mapping[key]] + dic[key]
            else:
                dic[words_mapping[key]] = dic[key]
            #Be sure there is no record of word_id = mapping_id
            del dic[key]
    return dic

def get_features(contents, word_features):
    features = {}
    for word in word_features:
        if contents.has_key(word):
            features[word] = contents[word]
        else:
            features[word] = 0
    return features

def get_mail_contents(email_id, cur, is_train_set):
    contents = {}
    if is_train_set:
        cur.execute('SELECT word_id, frequency from train_words where mail_id=%s and is_title=0', [email_id])
    else:
        cur.execute('SELECT word_id, frequency from words where mail_id=%s', [email_id])
    for row in cur.fetchall():
        contents[row[0]] = row[1]
    return contents

def get_train_cate_set(cur):
    cur.execute('SELECT id, sec_cate, frequency FROM train_cate where top_cate=1 limit %s', [train_size])
    return list(cur.fetchall())

def split_set(set):
    feature_list=[]
    class_list=[]
    item_list=[]
    i=0
    for item in set:
        i=i+1
        features=[]
        for key in sorted(item[0]):
            features.append(item[0][key])
        item_list.append(i)
        feature_list.append(features)
        class_list.append(item[1])
    return item_list, feature_list, class_list

def categorize_documents():
    cur = db.cursor()
    train_set = []
    test_set = []
    i = 0
    j = 1
    words_mapping = build_words_mapping(cur)
    word_features = build_word_features(cur)
    word_features = dic_mapping(word_features, words_mapping)
    train_cate_set = get_train_cate_set(cur)
    random.shuffle(train_cate_set)
    for mail in train_cate_set:
        #print "Getting features of Mail_" + str(mail[0]) + "..."
        for j in range(1, int(mail[2])+1):
            mail_features = get_features(dic_mapping(get_mail_contents(mail[0], cur, use_train_set_only), words_mapping), word_features)
            i = i + 1
            if (i%9)==0:
               test_set.append((mail_features, mail[1]))
            else:
               train_set.append((mail_features, mail[1]))
            j = j + 1
    classifier = sklearn.ensemble.RandomForestClassifier(n_estimators=1000)
    item_list, feature_list, class_list = split_set(train_set)
    classifier.fit(feature_list, class_list)
    item_list, feature_list, class_list = split_set(test_set)
    print train_size, feature_size, classifier.score(feature_list, class_list)
    #print list(classifier.predict(feature_list))
    #print class_list
    #print list(classifier.predict(feature_list)),class_list
    print train_size, feature_size, f1_score(list(classifier.predict(feature_list)), class_list, average='micro')
    cur.close()

def main():
    categorize_documents()

if __name__ == '__main__':
    main()