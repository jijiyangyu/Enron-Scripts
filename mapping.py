__author__ = 'Xiang to map different verb tense to ver base'


import MySQLdb
import pattern.en

db = MySQLdb.connect(host='localhost', # your host, usually localhost
                     user="root", # your username
                      passwd="", # your password
                      db="enronrpi") # name of the data base

def build_word_tags_list(cur):
    cur.execute('SELECT word, id FROM word_tags where tag_id = 27')
    word_tags={}
    for row in cur.fetchall():
        word_tags[row[0]] = row[1]
    return word_tags

def get_word_tags_id(cur):
    cur.execute('SELECT max(id) FROM word_tags')
    return int(cur.fetchone()[0])

def create_words_mapping(cur):
    words_mapping=[]
    new_word_tags={}
    verb_base = build_word_tags_list(cur)
    word_tag_id = get_word_tags_id(cur)
    cur.execute('SELECT word, id FROM word_tags where tag_id in (28,29,30,31,32)')
    for row in cur.fetchall():
        print pattern.en.lemma(row[0])
        if verb_base.has_key(pattern.en.lemma(row[0])):
            words_mapping.append([row[1], verb_base[pattern.en.lemma(row[0])]])
        else:
            word_tag_id = word_tag_id + 1
            new_word_tags[pattern.en.lemma(row[0])] = word_tag_id
            verb_base[pattern.en.lemma(row[0])] = word_tag_id
            words_mapping.append([row[1], word_tag_id])
    db.commit()
    for word in new_word_tags.keys():
        print "inserting..."
        cur.execute('insert into word_tags (id, word, tag_id) values(%s,%s,%s);',[new_word_tags[word], word, 27])
    cur.executemany('insert into words_mapping (word_id, mapping_id) values (%s, %s)', words_mapping)

def main():
    cur = db.cursor()
    create_words_mapping(cur)
    db.commit()
    cur.close()
    print "done"

if __name__ == '__main__':
    main()