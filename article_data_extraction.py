import nltk, sys, json

from watson_developer_cloud import AlchemyLanguageV1
from watson_developer_cloud import WatsonException
from parse_helper import parse_article
from json_helper import write_json_to_file

######################################################################################
# Functions defined to get alchemy data

class BadAPIKeyError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr("Error: bad API key!: " + self.value)

def get_alchemy_langauge_obj(the_api_key):
	alchemy_language = AlchemyLanguageV1(api_key=the_api_key)
	try:
		alchemy_language.emotion(text="I love cats! Dogs are smelly.")
	except WatsonException as err:
		if str(err) == "Error: invalid-api-key" or str(err) == "Error: invalid-permissions-for-call":
			return None, 1
		else:
			print "Alchemy error:", err
			return None, 2
	return alchemy_language, 0


def call_alchemy(sentence, alchemy_language):
	"""Called by perform_article_theme_extraction, calls AlchemyAPI for data that is TBD"""
	# print sentence
	# make alchemyAPI call here, insert data returned into Sentence class fields
	# construct api call based on data from sentence
	success_p = True
	d = None
	try:
		print "beginning Alchemy call"
		d = alchemy_language.combined(text=sentence, extract=['doc-sentiment', 'doc-emotion', 'entities', 'keywords', 'taxonomy'], sentiment=1)
		d = {key: d[key] for key in ['docSentiment', 'docEmotions', 'entities', 'keywords', 'taxonomy']}
		
		elist = ('|').join([e['text'] for e in d['entities']]+[k['text'] for k in d['keywords']])
		emotions = alchemy_language.targeted_emotion(text=sentence, targets=elist)['results']
	except WatsonException as err:
		if str(err) == "Error: daily-transaction-limit-exceeded":
			success_p = False
		else:
			print "Watson error:", err
	if success_p:
		for i in range(len(d['entities'])):
			d['entities'][i]['emotions'] = emotions[i]['emotions']
		for i in range(len(d['keywords'])):
			d['keywords'][i]['emotions'] = emotions[i+len(d['entities'])]['emotions']
	
	return d, success_p

def perform_article_theme_extraction(article_data, filename, alchemy_language):
	"""Called by main, 
	Takes in one article to extract themes from and tag those themes with sentiment
	What exactly theme means is TBD (either entity, or keyword, or both)
	What exactly sentiment means is TBD (either normal sentiment or potentially emotion)"""

	article_data = parse_article(article_data)

	alchemy_data = []
	can_continue_p = True
	for i, sentence in enumerate(article_data):
		sentence_data, success_p = call_alchemy(sentence[0], alchemy_language)
		if not success_p:
			return False
		else:
			sentence_data['sentence'] = sentence[1]
			sentence_data['number'] = i
			alchemy_data.append(sentence_data)
	if can_continue_p:
		write_json_to_file(alchemy_data, '_'+filename)
		return True
	else:
		return False