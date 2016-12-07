######################################################################################
# Functions defined to parse json article files and write data to json file

import os, json, unicodedata

def get_old_alchemy_data():
	"""Called by main, gets all the old alchemy data for all previously run and saved articles"""
	file_data = {}
	curr_dirpath = os.getcwd()
	for subdir, dirs, files in os.walk(curr_dirpath + '/testData'):
		for curr_file in files:
			curr_filepath = curr_dirpath + '/testData/' + curr_file
			if os.path.isfile(curr_filepath):
				if curr_file[:11] == "AlchemyData":
					with open(curr_filepath, 'r') as open_file:
						curr_data_filename = curr_file[12:].split(".txt")[0]
						#print "reading in data from article: " + curr_data_filename
						curr_json_data = json.load(open_file)
						#curr_data_filename_ascii = unicodedata.normalize('NFKD', curr_data_filename).encode('ascii', 'ignore')
						file_data[curr_data_filename] = curr_json_data
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
			curr_filename = curr_file.split(".json")[0]
			#print "reading data json file: " + curr_filename
			all_json_files_dir[curr_filename] = curr_json_data
	return all_json_files_dir

def get_single_json_to_play_with(all_json_files_dir):
	"""Called by main, just a test function to get one json file from the larger dict"""
	the_json_filename = ""
	for json_filename in all_json_files_dir:
		the_json_filename = json_filename
	return all_json_files_dir[the_json_filename], the_json_filename

######################################################################################

def write_json_to_file(json_data, data_ext_str):
	"""Called by perform_article_theme_extraction, just writes alchemy data for an article to file"""
	with open("testData/AlchemyData" + data_ext_str + ".txt", 'w') as json_file:
		json.dump(json_data, json_file)

######################################################################################
