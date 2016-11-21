import nltk, sys, json

from watson_developer_cloud import AlchemyLanguageV1
from parseHelper import parse_article
from jsonHelper import get_old_alchemy_data, get_test_json, get_single_json_to_play_with, write_json_to_file

######################################################################################
# Functions defined to get alchemy data

def call_alchemy(sentence, alchemy_language):
	"""Called by perform_article_theme_extraction, calls AlchemyAPI for data that is TBD"""
	# print sentence
	# make alchemyAPI call here, insert data returned into Sentence class fields
	# construct api call based on data from sentence

	d = alchemy_language.combined(text=sentence, extract=['doc-sentiment', 'doc-emotion', 'entities', 'keywords', 'taxonomy'], sentiment=1)
	d = {key: d[key] for key in ['docSentiment', 'docEmotions', 'entities', 'keywords', 'taxonomy']}

	elist = ('|').join([e['text'] for e in d['entities']]+[k['text'] for k in d['keywords']])
	emotions = alchemy_language.targeted_emotion(text=sentence, targets=elist)['results']
	for i in range(len(d['entities'])):
		d['entities'][i]['emotions'] = emotions[i]['emotions']
	for i in range(len(d['keywords'])):
		d['keywords'][i]['emotions'] = emotions[i+len(d['entities'])]['emotions']

	return d

def perform_article_theme_extraction(article_data, filename, alchemy_language):
	"""Called by main, 
	Takes in one article to extract themes from and tag those themes with sentiment
	What exactly theme means is TBD (either entity, or keyword, or both)
	What exactly sentiment means is TBD (either normal sentiment or potentially emotion)"""

	article_data = parse_article(article_data)

	alchemy_data = []
	for i, sentence in enumerate(article_data):
		sentence_data = call_alchemy(sentence[0], alchemy_language)
		sentence_data['sentence'] = sentence[1]
		sentence_data['number'] = i
		alchemy_data.append(sentence_data)
	write_json_to_file(alchemy_data, '_'+filename)

######################################################################################
# Main function

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "error: usage. Please input AlchemyAPI key to use."
		exit(1)
	alchemy_language = AlchemyLanguageV1(api_key=sys.argv[1])

	all_json_files_dir = get_test_json()
	old_alchemy_data = get_old_alchemy_data()
	# print "loaded all test files"

	# loop to go over all articles and extract article themes and sentiment
	for i, json_filename in enumerate(all_json_files_dir.keys()):
		json_file_data = all_json_files_dir[json_filename]["Data"]
		if json_filename in all_json_files_dir:
			print "already extracted data for article: ", json_filename
		else:
			print "now extraacting data for article:", json_filename
		#print "on article[", i, "] article name:", json_filename
		#perform_article_theme_extraction(json_file_data, json_filename, alchemy_language)

	#test_file, test_filename = get_single_json_to_play_with(all_json_files_dir)
	#test_file_data = test_file["Data"] # this gives us the actual article text
	#perform_article_theme_extraction(test_file_data, test_filename.split('.')[0], alchemy_language)

######################################################################################
