import nltk, sys, json

from watson_developer_cloud import AlchemyLanguageV1
from watson_developer_cloud import WatsonException
from parseHelper import parse_article
from jsonHelper import get_old_alchemy_data, get_test_json, get_single_json_to_play_with, write_json_to_file

######################################################################################
# Functions defined to get alchemy data

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

######################################################################################
# Main function

def main():
	## We have a main function instead of just having the code in the main if statement so we can return early in case of error
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
		if json_filename in old_alchemy_data:
			print "already extracted data for article: ", json_filename
		else:
			print "on article[", i, "] article name:", json_filename
			can_continue_p = perform_article_theme_extraction(json_file_data, json_filename, alchemy_language)
			if not can_continue_p:
				print "ran out of API calls on article: " + json_filename + ", exiting program.."
				return
	print "finished all articles!"

	#test_file, test_filename = get_single_json_to_play_with(all_json_files_dir)
	#test_file_data = test_file["Data"] # this gives us the actual article text
	#perform_article_theme_extraction(test_file_data, test_filename.split('.')[0], alchemy_language)

if __name__ == "__main__":
	main()

	

######################################################################################
