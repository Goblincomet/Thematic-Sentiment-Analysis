import sys, re
import matplotlib.pyplot as plt
import networkx as nx
from neo4j.v1 import GraphDatabase, basic_auth

from json_helper import get_old_alchemy_data, get_test_json, get_single_json_to_play_with
from article_data_extraction import perform_article_theme_extraction, get_alchemy_langauge_obj
from article_graph_builder import build_article_graph_from_data
from article_graph_visualization import export_graph_to_neo4j

def check_command_line_args():
	if len(sys.argv) > 3 or len(sys.argv) < 2:
		print "error: usage. Please input AlchemyAPI key to use."
		exit(1)
	build_graph_p = False
	if len(sys.argv) == 3:
		if sys.argv[2] == "-B" or sys.argv[2] == "--buildGraph":
			build_graph_p = True
		else:
			print "error: usage: '$ python main.py [api key] [-B/--buildGraph]' second parameter optional"
			exit(1)
	alchemy_language, err_code = get_alchemy_langauge_obj(sys.argv[1])
	if err_code == 1 or err_code == 2 and not build_graph_p:
		if err_code == 1:
			print "Alchemy error: Incorrect API key! (dumbass)"
		else:
			print "Alchemy error: out of API calls for the day! (rip)"
		exit(1)
	return alchemy_language, build_graph_p

######################################################################################
# Main function

def main():
	alchemy_language, build_graph_p = check_command_line_args()

	all_json_files_dir = get_test_json()
	old_alchemy_data = get_old_alchemy_data()
	# print "loaded all test files"

	if not build_graph_p:
		# loop to go over all articles and extract article themes and sentiment
		for i, json_filename in enumerate(all_json_files_dir.keys()):
			json_file_data = all_json_files_dir[json_filename]["Data"]
			if json_filename in old_alchemy_data:
				print "already extracted data for article: ", json_filename
			else:
				print "on article[", i, "] article name:", json_filename
				curr_alchemy_data, can_continue_p = perform_article_theme_extraction(json_file_data, json_filename, alchemy_language)
				if not can_continue_p:
					print "ran out of API calls on article: " + json_filename + ", exiting program.."
					return
				old_alchemy_data[json_filename] = curr_alchemy_data
		print "finished all articles!"
	else:
		print "skipping article data extraction and going right to graph construction"
		article_graph = build_article_graph_from_data(old_alchemy_data)
		export_graph_to_neo4j(article_graph)
		
		#labels = nx.draw_networkx_labels(article_graph, pos=nx.spring_layout(article_graph))
		#plt.show()
	#test_file, test_filename = get_single_json_to_play_with(all_json_files_dir)
	#test_file_data = test_file["Data"] # this gives us the actual article text
	#perform_article_theme_extraction(test_file_data, test_filename.split('.')[0], alchemy_language)

if __name__ == "__main__":
	main()

	

######################################################################################
