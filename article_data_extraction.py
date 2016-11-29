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
		elif str(err) == "Error: daily-transaction-limit-exceeded":
			return None, 2
		else:
			print "Alchemy error:", err
			return alchemy_language, 3
	return alchemy_language, 0


def build_emotions_hash(emotions):
	emotions_hash = {}
	for curr_emotion in emotions:
		if curr_emotion[u'text'] not in emotions_hash:
			emotions_hash[curr_emotion[u'text']] = curr_emotion
	return emotions_hash

def call_alchemy(sentence, alchemy_language):
	"""Called by perform_article_theme_extraction, calls AlchemyAPI for data that is TBD"""
	# print sentence
	# make alchemyAPI call here, insert data returned into Sentence class fields
	# construct api call based on data from sentence
	success_p = True
	d = None
	emotions = []
	transactions_used = 0
	try:
		d = alchemy_language.combined(text=sentence, extract=['doc-sentiment', 'doc-emotion', 'entities', 'keywords', 'taxonomy'], sentiment=1)
		transactions_used += int(d['totalTransactions'])
		d = {key: d[key] for key in ['docSentiment', 'docEmotions', 'entities', 'keywords', 'taxonomy']}
		elist = ('|').join([e['text'] for e in d['entities']]+[k['text'] for k in d['keywords']]) # this list is sometimes empty when no keywords or entities were found
		if not (len(d['keywords']) == 0 and len(d['entities']) == 0): # need to check here if theres anything to actually tag with emotions
			emotions_full_return = alchemy_language.targeted_emotion(text=sentence, targets=elist)
			transactions_used += int(emotions_full_return['totalTransactions'])
			emotions = emotions_full_return['results']
			#print json.dumps(emotions_full_return, indent=2)
		else:
			print "NO KEYWORDS AND ENTITIES FOUND"
	except WatsonException as err:
		if str(err) == "Error: daily-transaction-limit-exceeded":
			print "reached daily api call limit"
			success_p = False
		else:
			#print "NO KEYWORDS AND ENTITIES FOUND (reaffirmed as the error)"
			print "Watson error:", err
			success_p = False
	break_this_shit_p = False
	if success_p and len(emotions) > 0:
		emotions_hash = build_emotions_hash(emotions)
		for i in range(len(d['entities'])):
			#print "i for entity is now:", i, ", entity is:", d['entities'][i][u'text'], ", emotion keyword is:", emotions[i][u'text']
			#d['entities'][i]['emotions'] = emotions[i]['emotions']
			if d['entities'][i][u'text'] in emotions_hash:
				#print "will now hash entity[", d['entities'][i][u'text'], "] to emotion[", emotions_hash[d['entities'][i][u'text']][u'text']
				d['entities'][i]['emotions'] = emotions_hash[d['entities'][i][u'text']]['emotions']
			else: ## TODO: this quick fix may need some more looking into 
				#print "failed to tag entity[", d['entities'][i][u'text'], "] with an emotion, removing it"
				del d['entities'][i]
		for i in range(len(d['keywords'])):
			#print "len emotions:", len(emotions), ", index to be accessed:", i+len(d['entities']), ", keyword:", d['keywords'][i][u'text']
			if d['keywords'][i][u'text'] in emotions_hash:
				#print "will now hash keyword[", d['keywords'][i][u'text'], "] to emotion[", emotions_hash[d['keywords'][i][u'text']][u'text']
				d['keywords'][i]['emotions'] = emotions_hash[d['keywords'][i][u'text']]['emotions']
			else: ## TODO: this quick fix may need some more looking into 
				#print "failed to tag keyword[", d['keywords'][i][u'text'], "] with an emotion"
				del d['keywords'][i]
			#if i+len(d['entities']) < len(emotions):
				#print "emotion keyword[", i+len(d['entities']), "]:", emotions[i+len(d['entities'])][u'text']
				#print "emotions[i+len(d['entities'])]['emotions']:", emotions[i+len(d['entities'])]['emotions']
			#	d['keywords'][i]['emotions'] = emotions[i+len(d['entities'])]['emotions']
			#else:
			#	break_this_shit_p = True
	if break_this_shit_p:
		print "breaking this shit"
		exit(1)
	return d, success_p, transactions_used

def perform_article_theme_extraction(article_data, filename, alchemy_language):
	"""Called by main, 
	Takes in one article to extract themes from and tag those themes with sentiment
	What exactly theme means is TBD (either entity, or keyword, or both)
	What exactly sentiment means is TBD (either normal sentiment or potentially emotion)"""
	article_data = parse_article(article_data)
	alchemy_data = []
	can_continue_p = True
	print "\tarticle has", len(article_data), "sentences"
	tot_transactions_used = 0
	for i, sentence in enumerate(article_data):
		sentence_data, success_p, transactions_used = call_alchemy(sentence[0], alchemy_language)
		if not success_p:
			return alchemy_data, False
		else:
			sentence_data['sentence'] = sentence[1]
			sentence_data['number'] = i
			alchemy_data.append(sentence_data)
			tot_transactions_used+=transactions_used
	if can_continue_p:
		write_json_to_file(alchemy_data, '_'+filename)
		print "\tfinished extracting article data, used", tot_transactions_used, "api transactions"
		return alchemy_data, True
	else:
		return alchemy_data, False