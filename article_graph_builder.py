from __future__ import division
import networkx as nx
import json


class ArticleNode:
	def __init__(self, article_name, article_sentence_data, article_entity_data, article_keyword_data):
		self.article_name = article_name
		self.article_sentence_data = article_sentence_data
		self.article_entity_data = article_entity_data
		self.article_keyword_data = article_keyword_data

	def __str__(self):
		return "article[" + self.article_name + "]"

def combine_emotion_for_new_entity(all_entities, condenced_entity_name, new_emotion_entry):
	"""Called by extract_entity_data_for_curr_sentence, adds emotion scores to running totals for the current entity/keyword"""
	for curr_emotion, curr_emotion_str_val in new_emotion_entry.iteritems():
		curr_emotion_float = float(curr_emotion_str_val)
		all_entities[condenced_entity_name]["combined_emotion"][str(curr_emotion)] += curr_emotion_float

def aggregate_emotion_entries_into_final_scores(all_entities):
	"""Called by build_article_node, finishes aggregation of emotion data for entities and keywords"""
	for curr_entity_name, curr_entity_data in all_entities.iteritems():
		curr_entity_combined_emotion = curr_entity_data["combined_emotion"]
		curr_emotion_divisor = len(curr_entity_data["all_entries_list"])
		for curr_emotion_name in curr_entity_combined_emotion:
			curr_entity_combined_emotion[curr_emotion_name] = curr_entity_combined_emotion[curr_emotion_name]/curr_emotion_divisor
		#print "for entity[" + curr_entity_name + "] freq is", curr_emotion_divisor

def extract_entity_data_for_curr_sentence(curr_sentence_data, all_entities):
	"""Called by build_article_node, takes the entity data from the current sentence and starts to aggregate its entity data"""
	for curr_entity in curr_sentence_data[u'entities']:
		condenced_entity_name = str(curr_entity[u'text'])
		if curr_entity[u'type'] == u'Person': # TODO: this is a quick fix to a real disambiguation problem with named person entities
			entity_name_list = condenced_entity_name.split(' ')
			condenced_entity_name = entity_name_list[len(entity_name_list)-1]
		if condenced_entity_name not in all_entities:
			all_entities[condenced_entity_name] = {}
			all_entities[condenced_entity_name]["combined_emotion"] = {"anger": 0, "joy": 0, "fear": 0, "sadness": 0, "disgust": 0}
			all_entities[condenced_entity_name]["all_entries_list"] = []
		all_entities[condenced_entity_name]["all_entries_list"].append(curr_entity)
		combine_emotion_for_new_entity(all_entities, condenced_entity_name, curr_entity[u'emotions'])

def extract_keyword_data_for_curr_sentence(curr_sentence_data, all_keywords, sentence_cntr):
	"""Called by build_article_node, works the same as extract_entity_data_for_curr_sentence, may discard this at one point"""
	print "sentence[", sentence_cntr,"] keywords:", len(curr_sentence_data[u'keywords'])
	#print json.dumps(curr_sentence_data[u'keywords'], indent=2)
	for curr_keyword in curr_sentence_data[u'keywords']: ## NEED TO CONSIDER DISAMBIGUATION HERE AS WELL
		condenced_keyword_name = str(curr_keyword[u'text'])
		print "keyword[" + condenced_keyword_name + "]"
		if condenced_keyword_name not in all_keywords:
			all_keywords[condenced_keyword_name] = {}
			all_keywords[condenced_keyword_name]["combined_emotion"] = {"anger": 0, "joy": 0, "fear": 0, "sadness": 0, "disgust": 0}
			all_keywords[condenced_keyword_name]["all_entries_list"] = []
		all_keywords[condenced_keyword_name]["all_entries_list"].append(curr_keyword)
		combine_emotion_for_new_entity(all_keywords, condenced_keyword_name, curr_keyword[u'emotions'])

def build_article_node(curr_article_name, curr_article_data):
	"""Called by build_article_graph_from_data, takes Alchemy data for a single article and builds a node from it"""
	print "on article:", curr_article_name
	all_entities = {}
	all_keywords = {}
	sentence_cntr = 0
	for curr_sentence_data in curr_article_data:
		extract_entity_data_for_curr_sentence(curr_sentence_data, all_entities)
		extract_keyword_data_for_curr_sentence(curr_sentence_data, all_keywords, sentence_cntr)
		#for curr_sent_field in curr_sentence_data:
		#	print "curr field:", curr_sent_field
		sentence_cntr+=1
	aggregate_emotion_entries_into_final_scores(all_entities)
	curr_article_node = ArticleNode(curr_article_name, curr_article_data, all_entities, all_keywords)
	

def build_article_graph_from_data(all_alchemy_data):
	article_graph = nx.Graph()
	for curr_article_name, curr_article_data in all_alchemy_data.iteritems(): # build article nodes and put them in the graph
		curr_article_node = build_article_node(curr_article_name, curr_article_data)
		article_graph.add_node(curr_article_node)
	return article_graph