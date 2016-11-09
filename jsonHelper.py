######################################################################################
# Functions defined to parse json article files and write data to json file

import os, json

def get_old_alchemy_data():
	"""Called by main, gets all the old alchemy data for all previously run and saved articles"""
	file_data = {}
	for subdir, dirs, files in os.walk('./'):
		for curr_file in files:
			if os.path.isfile(curr_file):
				if curr_file[:11] == "AlchemyData":
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

######################################################################################

def write_json_to_file(json_data, data_ext_str):
	"""Called by perform_article_theme_extraction, just writes alchemy data for an article to file"""
	with open("AlchemyData" + data_ext_str + ".txt", 'w') as json_file:
		json.dump(json_data, json_file)

######################################################################################
