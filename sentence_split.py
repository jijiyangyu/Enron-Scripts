#!/usr/local/bin/python
#
#  Author: Marti A. Hearst
#          UC Berkeley
#  
#  Description: Takes as input a string of text, produces as output
#               tokenized text subdivided into sentences 
#  Last modified: October 7, 2004
#
#
#  To use this code, simply run
#      toks = sentence_split.tokenize_sentences(string)
#
#  The results are stored in toks, and can be access as follows:
#  toks['SENTS'] returns a list of tokens of type sentence
#  toks['SENTS'][0] returns the first sentence token
#  toks['SENTS'][0]['WORDS'] returns the individual word tokens of that sentence
#  toks['SENTS'][0]['WORDS'][0] returns the token of the first word
#  toks['SENTS'][0]['WORDS'][0]['TEXT'] returns the text of the token of the first word
#
#  To use with newsgroup code, you need to get to the raw text.  Here is how to do it
#  using one file as an example.
#
#   from nltk.corpus import twenty_newgroups
#
#   items = twenty_newsgroups.items('rec.motorcycles')
#   fname = twenty_newsgroups.path(items[0])
#   s = open(fname).read()
#   toks = tokenize_sentence(s)
#   return toks

import re, string, nltk

from nltk.tokenize.regexp import RegexpTokenizer

def tokenize_sentences(s):
   l = prep_string(s)
   b = scan_words(l)
   ss = insert_boundaries(l, b)
   toks = ss #Token(TEXT=ss, LOC=CharSpanLocation(0, len(ss), 'ss'))
   sents = create_sents(toks)
   return sents

   
def prep_string(s):
   s = re.sub("\n", " ",s)
   s = re.sub("\>", " ",s)
   #toks = Token(TEXT=s, LOC=CharSpanLocation(0, len(s), 's'))
   wordre = r"\w+@[\w.]+|'s|[0-9]+[.0-9]+|[0-9]+|^\w+:|([A-Z][.]+)+|(\w+[-']?)+|[.!?]|:\w*\n"
   toks = RegexpTokenizer(wordre).tokenize(s)
   word_list = []
   for tok in toks:
      word_list.append(tok)
   return word_list


def insert_boundaries(words, boundaries):
   newstr = ""
   for i in range(len(words)):
      newstr = string.join([newstr, words[i]], " ")
      if i in boundaries:
         newstr = string.join([newstr, "[.?!]\s*"], " ")
   return newstr

      
def create_sents(toks):
   wordre = r"\w+@[\w.]+|'s|[0-9]+[.0-9]+|[0-9]+|^\w+:|([A-Z][.]+)+|(\w+[-']?)+|[.!?]|:\w*\n"
   s=RegexpTokenizer(wordre).tokenize(toks)
   wordre = r"\w+@[\w.]+|'s|[0-9]+[.0-9]+|[0-9]+|^\w+:|([A-Z][.]+)+|(\w+[-']?)+|[.!?]|:\w*\n"
   for sentence in s:
      RegexpTokenizer(wordre).tokenize(sentence)
   return toks
   
def is_potential_endpunct(word):
   if word == "." or word == "!" or word == "?" or word == "\"":
      return True
   return False

def is_potential_conjunction(word):
   if word == "and" or word == "or" or word == "but":
      return True
   return False

def is_potential_preposition(word):
   prep_list = ["at", "in", "on", "under", "out", "inside", "outside", "by", "of", "near", "within", "with", "over", "between"]
   if word in prep_list: return True
   return False

def start_with_capital(word):
   if re.match("[A-Z]", word[0]): return True
   return False

def is_potential_abbrev(word):
   abbrev_list = ["Mr", "Ms", "Dr", "Prof", "Co", "Inc", "Sen", "dept", "dr", "eg", "ie", ]
   if word in abbrev_list: return True
   return False

def is_potential_verb(word):
   return False

def is_potential_modifier(word):
   return True

def is_right_paren(word):
   if word == ")": return True
   return False

def scan_words (words):
   buffersize = 7
   max = len(words)
   current = 4
   found = 0
   boundaries = []
   while current < (max - 4):
      if  start_with_capital(words[current-1]) and start_with_capital(words[current+1]) and is_potential_abbrev(words[current-1]):
         found = 1
      elif (words[current+1] == "Subject:") or (words[current+1] == "From:"):
         boundaries.append(current)
      elif is_potential_endpunct(words[current]):
         if not (start_with_capital(words[current+1])):
            if is_right_paren(words[current+1]):
               boundaries.append(current)
         else:
            if not (is_potential_endpunct(words[current-3])):
               if not (is_potential_conjunction(words[current+1])):
                  if not (is_potential_endpunct(words[current+2])):
                     if is_potential_modifier(words[current-2]):
                        boundaries.append(current)
                  elif is_potential_preposition(words[current+1]):
                     boundaries.append(current)
                  else:
                     if is_potential_abbrev(words[current-3]):
                        boundaries.append(current)
                     elif not (is_potential_verb(words[current+1])):
                        if is_potential_conjunction(words[current-2]):
                           boundaries.append(current)
                        elif not (is_potential_endpunct(words[current+3])):
                           if not (is_potential_preposition(words[current+2])):
                              if is_potential_modifier(words[current-2]):
                                 boundaries.append(current)
      current += 1
   boundaries.append(max-1)
   return boundaries



def tryit():
   from nltk.corpus import twenty_newsgroups

   items = twenty_newsgroups.items('rec.motorcycles')
   fname = twenty_newsgroups.path(items[0])
   s = open(fname).read()
   toks = tokenize_sentence(s)
   return toks
