######################################################################################
# Functions defined to help parse json article

import nltk, re, unicodedata

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def fix_punct(article_data):
	for p in ['.', ',', ':', '!', '?', ';']:
		article_data = re.sub('[%s]'%p, p+' ', article_data)
	return article_data

def parse_article(article_data):
	article_data = unicodedata.normalize('NFKD', article_data).encode('ascii', 'ignore')
	return [(sentence, nltk.word_tokenize(sentence)) for sentence in tokenizer.tokenize(fix_punct(article_data), realign_boundaries=True)]

######################################################################################
