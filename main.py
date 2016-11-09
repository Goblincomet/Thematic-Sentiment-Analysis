import sys
import os, wxversion
import json
import nltk
import unicodedata
from watson_developer_cloud import AlchemyLanguageV1

## NOTES:
##	-> AlchemyLanguage:
##		- Concept tagging: can identify non explicitly mentioned concepts from input, higher level than keyword extraction 	
##			and would allow us to find more general themes across many articles
##		- Emotion Analysis: If we can target phrases, entities, or keywords from a sentence, can tag them with emotions like
##			anger, disgust, fear, joy, and sadness.  In order for this to be useful, each emotion would need known opposites
##		- (Typed?) Relations: extracting relations would give us the ability to identify more complex themes such as a bill 
##			trying to be passed through Congress, and perform our sentiment analysis comparison on that as well. Look into this.
##		- Sentiment Analysis:  5 levels of targetted sentiment analysis is possible:
##			* Document level: (should not use, since we are doing analysis on the sentence level)
##			* entity level: Has promise, may be what we are looking for
##			* quotation level: Probably literal quotations, possibly useful if one quote comes up in many articles
##			* directional level: Not sure what exactly this is, or its usefulness
##			* keyword level: Maybe too low level? Worst case senario, we use this level. 
##		- Combined calls: can probably use this to minimize the number of API calls we make, keeping it at least to the document level
##			* UPDATE: Would not save us API calls, would just potentially save us time and make data easier to organize


## We have two options (as I see it).  Base senteiment analysis on entities or keywords (or both)
## Entities are more sparse than keywords, but keywords have the danger of being irrelivant
## Also, could use senteiment or emotion (more meterics) as basis for how we compare themes within and between articles
##		-> For this, further discussion with the squirrel is necessary

## Dependency Notes:
## -> need watson developer cloud: run command '$ sudo pip install --upgrade watson-developer-cloud'
## -> API key: 
##{
##  "url": "https://gateway-a.watsonplatform.net/calls",
##  "note": "It may take up to 5 minutes for this key to become active",
##  "apikey": "d0d23b0df6ff757a6546557f8a7076f0c83f3b7d"
##}



punct_arr = ['.', ':', '!', '?', ';'] ## this array denotes sentence boundary marking punctuation characters
alchemy_language = None


class Sentence:
	def __init__(self, sentence_elt, sentence_arr, start_pos, end_pos):
		self.sentence_elt = sentence_elt
		self.sentence_arr = sentence_arr
		self.start_pos = start_pos
		self.end_pos = end_pos
		self.sentence_str = ""
		for curr_sen_elt in sentence_arr:
			self.sentence_str += curr_sen_elt + " "

	def __str__(self):
		return "sentence[" + str(self.sentence_elt) + "], data[" + str(self.sentence_arr) + "]"


def get_old_alchemy_data():
	"""Called by main, gets all the old alchemy data for all previously run and saved articles"""
	file_data = {}
	for subdir, dirs, files in os.walk('./'):
		for curr_file in files:
			if os.path.isfile(curr_file):
				filename_list = curr_file.split("_")
				if len(filename_list) > 0:
					if filename_list[0] == "AlchemyData":
						with open(curr_file, 'r') as open_file:
							curr_json_data = json.load(open_file)
							file_data[filename_list[1]] = curr_json_data
	return file_data

def read_json_from_file(json_filepath):
	"""Called by get_test_json, returns data from a single json file"""
	if os.path.isfile(json_filepath):
		with open(json_filepath) as json_file:
			data = json.load(json_file)
			return data

def get_test_json():
	"""Called by main, returns all json files in a dict with the key being article name and value being the json data for that article"""
	json_dir_path = "testDocs"
	all_json_files_dir = {}
	if os.path.isdir(json_dir_path):
		for curr_file in os.listdir(json_dir_path):
			curr_json_filepath = json_dir_path + "/" + curr_file
			curr_json_data = read_json_from_file(curr_json_filepath)
			all_json_files_dir[curr_file] = curr_json_data
	return all_json_files_dir

def get_single_json_to_play_with(all_json_files_dir):
	"""Called by main, just a test function to get one json file from the larger dict"""
	the_json_filename = ""
	for json_filename in all_json_files_dir:
		the_json_filename = json_filename
	return all_json_files_dir[the_json_filename], the_json_filename

def detect_interior_token_punct(curr_token):
	"""Called by fix_token_arr, detects any punctuation in the interior of a token, if any exists"""
	curr_pos = 0
	for token_elt in curr_token:
		if token_elt in punct_arr and not curr_pos == 0: # account for actual punctuation case
			first_token = curr_token[:curr_pos]
			second_token = curr_token[curr_pos+1:]
			punct_token = curr_token[curr_pos]
			return True, first_token, second_token, punct_token
		curr_pos +=1
	return False, None, None, None

def fix_token_arr(token_arr):
	"""Called by perform_article_theme_extraction, just performs larger punctuation tokenization correction to the original 
	token array"""
	corrected_token_arr = []
	for curr_token in token_arr:
		interior_punct_p, first_token, second_token, punct_token = detect_interior_token_punct(curr_token)
		if interior_punct_p:
			corrected_token_arr.append(first_token)
			corrected_token_arr.append(punct_token)
			corrected_token_arr.append(second_token)
		else:
			corrected_token_arr.append(curr_token)
	return corrected_token_arr

def write_json_to_file(json_data, data_ext_str):
	"""Called by perform_article_theme_extraction, just writes alchemy data for an article to file"""
	json_filepath = "AlchemyData" + data_ext_str + ".txt"
	with open(json_filepath, 'w') as json_file:
		json.dump(json_data, json_file)


def call_alchemy(curr_sentence):
	"""Called by perform_article_theme_extraction, calls AlchemyAPI for data that is TBD"""
	print curr_sentence
	# make alchemyAPI call here, insert data returned into Sentence class fields
	# construct api call based on data from sentence
	combined_operations = ['entity', 'keyword', 'concept', 'doc-emotion']
	#print(json.dumps(alchemy_language.combined(text=curr_sentence.sentence_str, extract=combined_operations), indent=2))
	# Get sentiment and emotion information results for detected entities/keywords:
	alchemy_json_data = alchemy_language.entities(text=curr_sentence.sentence_str, sentiment=True, emotion=True)
	return alchemy_json_data

def perform_article_theme_extraction(curr_article_data, curr_filename, cntr):
	"""Called by main, 
	Takes in one article to extract themes from and tag those themes with sentiment
	What exactly theme means is TBD (either entity, or keyword, or both)
	What exactly sentiment means is TBD (either normal sentiment or potentially emotion)"""
	curr_article_data_ascii = unicodedata.normalize('NFKD', curr_article_data).encode('ascii', 'ignore')
	token_arr = nltk.word_tokenize(curr_article_data_ascii)
	corrected_token_arr = fix_token_arr(token_arr) # some punctuaton is embedded in tokens, must find and correct that
	all_sentence_arr = []
	alchemy_data = {}
	sent_start_pos = 0
	curr_pos = 0
	sentence_elt = 0
	for curr_token in corrected_token_arr:
		if curr_token in punct_arr and not sent_start_pos == curr_pos:
			sentence_arr = corrected_token_arr[sent_start_pos:curr_pos+1]
			curr_sentence = Sentence(sentence_elt, sentence_arr, sent_start_pos, curr_pos+1)
			curr_alchemy_data = call_alchemy(curr_sentence)
			curr_alchemy_data["orig sentence"] = sentence_arr
			alchemy_data["sentence" + str(sentence_elt)] = curr_alchemy_data
			all_sentence_arr.append(curr_sentence)
			sent_start_pos = curr_pos +1
			sentence_elt+=1
		curr_pos +=1
	write_json_to_file(alchemy_data, "_" + curr_filename.split('.')[0] + "_EKCD")
	return cntr+1


def main():
	## anders AlchemyAPI key: "d0d23b0df6ff757a6546557f8a7076f0c83f3b7d"
	print sys.argv
	if len(sys.argv) == 2:
		alchemy_language = AlchemyLanguageV1(api_key=sys.argv[1])
	else:
		print "error: usage.  Please input AlchemyAPI key to use."
		return
	all_json_files_dir = get_test_json()
	get_old_alchemy_data()
	print "loaded all test files"
	cntr = 0
	#for curr_json_filename in all_json_files_dir: # loop to go over all articles and extract article themes and sentiment
	#	curr_json_file = all_json_files_dir[curr_json_filename]
	#	curr_json_file_data = curr_json_file["Data"]
	#	print "on article[", cntr, "] article name:", curr_json_filename
	#	cntr = perform_article_theme_extraction(curr_json_file_data, curr_json_filename, cntr)
	test_file, test_filename = get_single_json_to_play_with(all_json_files_dir)
	test_file_data = test_file["Data"] # this gives us the actual article text
	#perform_article_theme_extraction(test_file_data, test_filename, 0)

if __name__ == "__main__":
	main()