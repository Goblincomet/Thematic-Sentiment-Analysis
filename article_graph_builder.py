from __future__ import division
import networkx as nx
import json
import operator


class ArticleNode:
	def __init__(self, article_name, article_sentence_data, article_entity_data, article_keyword_data):
		self.article_name = article_name
		self.article_sentence_data = article_sentence_data
		self.article_entity_data = article_entity_data
		self.article_keyword_data = article_keyword_data
		self.sorted_entity_list = []
		self.total_entities = 0
		self.sorted_keyword_list = []
		self.total_keywords = 0

	def get_sorted_entity_list(self):
		if len(self.sorted_entity_list) == 0:
			entity_freq_dict = {}
			for curr_entity, curr_entity_data in self.article_entity_data.iteritems():
				entity_freq_dict[curr_entity] = len(curr_entity_data["all_entries_list"])
				self.total_entities+=len(curr_entity_data["all_entries_list"])
			for sorted_tuple in sorted(entity_freq_dict.items(), key=operator.itemgetter(1)):
				self.sorted_entity_list.append((sorted_tuple[0], sorted_tuple[1]/self.total_entities))
			self.sorted_entity_list.reverse()
		return self.sorted_entity_list

	def get_sorted_keyword_list(self):
		if len(self.sorted_keyword_list) == 0:
			keyword_freq_dict = {}
			for curr_entity, curr_entity_data in self.article_keyword_data.iteritems():
				keyword_freq_dict[curr_entity] = len(curr_entity_data["all_entries_list"])
				self.total_keywords+=len(curr_entity_data["all_entries_list"])
			for sorted_tuple in sorted(keyword_freq_dict.items(), key=operator.itemgetter(1)):
				self.sorted_keyword_list.append((sorted_tuple[0], sorted_tuple[1]/self.total_keywords))
			self.sorted_keyword_list.reverse()
		return self.sorted_keyword_list

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
	#print "sentence[", sentence_cntr,"] keywords:", len(curr_sentence_data[u'keywords'])
	#print json.dumps(curr_sentence_data[u'keywords'], indent=2)
	for curr_keyword in curr_sentence_data[u'keywords']: ## NEED TO CONSIDER DISAMBIGUATION HERE AS WELL
		condenced_keyword_name = str(curr_keyword[u'text'])
		#print "keyword[" + condenced_keyword_name + "]"
		if condenced_keyword_name not in all_keywords:
			all_keywords[condenced_keyword_name] = {}
			all_keywords[condenced_keyword_name]["combined_emotion"] = {"anger": 0, "joy": 0, "fear": 0, "sadness": 0, "disgust": 0}
			all_keywords[condenced_keyword_name]["all_entries_list"] = []
		all_keywords[condenced_keyword_name]["all_entries_list"].append(curr_keyword)
		combine_emotion_for_new_entity(all_keywords, condenced_keyword_name, curr_keyword[u'emotions'])

def build_article_node(curr_article_name, curr_article_data, node_cntr):
	"""Called by build_article_graph_from_data, takes Alchemy data for a single article and builds a node from it"""
	
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
	#if node_cntr == 1:
	#	print "on article:", curr_article_name
	#	for curr_entity in all_entities:
	#		print curr_entity
	return ArticleNode(curr_article_name, curr_article_data, all_entities, all_keywords)

def compare_sorted_lists(list1, list2):
	"""Called by find_closely_related_nodes, this is the function to find similarity between articles, should be reviewed."""
	matches_score = 0
	mismatches_score = 0
	num_matches = 0 # currently not used
	num_mismatches = 0 # currently not used
	completed_terms = []
	list1_dict = {curr_tuple[0]: curr_tuple[1] for curr_tuple in list1}
	list2_dict = {curr_tuple[0]: curr_tuple[1] for curr_tuple in list2}
	for curr_term_tuple in list1:
		curr_term = curr_term_tuple[0]
		curr_term_freq = curr_term_tuple[1]
		if curr_term in list2_dict: # if the term is present in both lists, add their frequencies to the score
			matches_score += (list2_dict[curr_term] + curr_term_freq)
			num_matches+=1
		else: # otherwise that frequency counts against the match score
			num_mismatches+=1
			mismatches_score += curr_term_freq
		completed_terms.append(curr_term)
	for curr_term_tuple in list2: ## add all terms from the second list not present in the first to the mismatch score
		if curr_term_tuple[0] not in completed_terms:
			num_mismatches+=1
			mismatches_score+=curr_term_tuple[1]
	return matches_score/(matches_score+mismatches_score) ## return the percent matches against the overall combined score


def find_closely_related_nodes(curr_article_name, curr_article_node, article_graph):
	"""Called by build_article_graph_from_data"""
	curr_node_sorted_entities = curr_article_node.get_sorted_entity_list()
	curr_node_sorted_keywords = curr_article_node.get_sorted_keyword_list()
	for other_article_name, other_article_data_hash in article_graph.nodes(data=True): # go over all other nodes
		if other_article_name != curr_article_name:
			other_article_node = other_article_data_hash['node_data']
			other_sorted_entities = other_article_node.get_sorted_entity_list() # just work with entities rn
			other_sorted_keywords = other_article_node.get_sorted_keyword_list()
			entity_relation_score = compare_sorted_lists(curr_node_sorted_entities, other_sorted_entities)
			keyword_relation_score = compare_sorted_lists(curr_node_sorted_keywords, other_sorted_keywords)
			if entity_relation_score > 0: # create entity edge if the two nodes are related through entities
				#print "article[" + curr_article_name + "] compared to article[" + other_article_name + "] relation score:", entity_relation_score
				if (curr_article_name, other_article_name) not in article_graph.edges():
					article_graph.add_edge(curr_article_name, other_article_name)
				article_graph[curr_article_name][other_article_name]['entity_weight'] = entity_relation_score
			if keyword_relation_score > 0: # create a keyword edge if the two nodes are related through keywords
				if (curr_article_name, other_article_name) not in article_graph.edges():
					article_graph.add_edge(curr_article_name, other_article_name)
				article_graph[curr_article_name][other_article_name]['keyword_weight'] = keyword_relation_score

def build_article_graph_from_data(all_alchemy_data):
	article_graph = nx.Graph()
	node_cntr = 0
	for curr_article_name, curr_article_data in all_alchemy_data.iteritems(): # build article nodes and put them in the graph
		curr_article_node = build_article_node(curr_article_name, curr_article_data, node_cntr)
		article_graph.add_node(curr_article_name, node_data=curr_article_node)
		node_cntr +=1
	for curr_article_name, curr_article_data_hash in article_graph.nodes(data=True): # add edges between article nodes
		curr_article_node = curr_article_data_hash['node_data']
		find_closely_related_nodes(curr_article_name, curr_article_node, article_graph)
	for e in article_graph.edges(data=True):
		print e[0], e[1],
		if 'entity_weight' in e[2]:
			print 'e', e[2]['entity_weight'],
		if 'keyword_weight' in e[2]:
			print 'k', e[2]['keyword_weight'],
		print
	return article_graph