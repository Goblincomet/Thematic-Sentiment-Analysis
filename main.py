import sys
import os, wxversion
import json
import nltk
import unicodedata

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


punct_arr = ['.', ':', '!', '?', ';'] ## this array denotes sentence boundary marking punctuation characters


class Sentence:
	def __init__(self, sentence_elt, sentence_arr, start_pos, end_pos):
		self.sentence_elt = sentence_elt
		self.sentence_arr = sentence_arr
		self.start_pos = start_pos
		self.end_pos = end_pos

	def __str__(self):
		return "sentence[" + str(self.sentence_elt) + "], data[" + str(self.sentence_arr) + "]"

def read_json_from_file(json_filepath):
	if os.path.isfile(json_filepath):
		with open(json_filepath) as json_file:
			data = json.load(json_file)
			return data

def get_test_json():
	json_dir_path = "testDocs"
	all_json_files_dir = {}
	if os.path.isdir(json_dir_path):
		for curr_file in os.listdir(json_dir_path):
			curr_json_filepath = json_dir_path + "/" + curr_file
			curr_json_data = read_json_from_file(curr_json_filepath)
			all_json_files_dir[curr_file] = curr_json_data
	return all_json_files_dir

def get_single_json_to_play_with(all_json_files_dir):
	the_json_filename = ""
	for json_filename in all_json_files_dir:
		the_json_filename = json_filename
	return all_json_files_dir[the_json_filename]

def detect_interior_token_punct(curr_token):
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

def perform_article_theme_extraction(curr_article_data):
	curr_article_data_ascii = unicodedata.normalize('NFKD', curr_article_data).encode('ascii', 'ignore')
	token_arr = nltk.word_tokenize(curr_article_data_ascii)
	corrected_token_arr = fix_token_arr(token_arr) # some punctuaton is embedded in tokens, must find and correct that
	all_sentence_arr = []
	sent_start_pos = 0
	curr_pos = 0
	sentence_elt = 0
	for curr_token in corrected_token_arr: # first pass, we are chunking the text by sentence
		if curr_token in punct_arr and not sent_start_pos == curr_pos:
			sentence_arr = corrected_token_arr[sent_start_pos:curr_pos+1]
			curr_sentence = Sentence(sentence_elt, sentence_arr, sent_start_pos, curr_pos+1)
			print curr_sentence
			all_sentence_arr.append(curr_sentence)
			sent_start_pos = curr_pos +1
			sentence_elt+=1
		curr_pos +=1


def main():
	all_json_files_dir = get_test_json()
	print "loaded all test files"
	test_file = get_single_json_to_play_with(all_json_files_dir)
	test_file_data = test_file["Data"] # this gives us the actual article text
	perform_article_theme_extraction(test_file_data)

if __name__ == "__main__":
	main()