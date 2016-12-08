import sys, re, unicodedata
import networkx as nx

from py2neo import Graph, Node, Relationship


## HOW TO SET UP NEO4J:
## You need to start neo4j before running the program, using the line '$ sudo neo4j start'
## The first time you do this, open web page 'http://localhost:7474/browser/' and log in and change the password to 1happydog
## Remember to run '$ sudo neo4j stop' when done with the database


def make_new_graph_node(new_node):
	entity_list = [unicodedata.normalize('NFKD', e).encode('ascii', 'ignore') for e in new_node.entities]
	taxonomy_list = [unicodedata.normalize('NFKD', e).encode('ascii', 'ignore') for e in new_node.taxonomies]
	new_graph_node = Node("Article", title = new_node.name, entities=entity_list, taxonomies=taxonomy_list)
	return new_graph_node

def export_graph_to_neo4j(article_graph):
	empty_graph() # delete all old nodes in the graph db
	graph = Graph(password="1happydog")
	tx = graph.begin()
	graph_node_dict = {}
	for e in article_graph.edges(data=True):
		if e[0].name not in graph_node_dict:
			new_graph_node = make_new_graph_node(e[0])
			graph_node_dict[e[0].name] = new_graph_node
		if e[1].name not in graph_node_dict:
			new_graph_node = make_new_graph_node(e[1])
			graph_node_dict[e[1].name] = new_graph_node
		g_node1 = graph_node_dict[e[0].name]
		g_node2 = graph_node_dict[e[1].name]
		new_edge = Relationship(g_node1, "RELATED TO", g_node2, entity_weight = e[2]['entity_weight'], taxonomy_weight = e[2]['taxonomy_weight'], sentiment_weight = e[2]['sentiment_weight'], emotion_weight = e[2]['emotion_weight'])
		tx.create(new_edge)
	tx.commit()
  	#empty_graph()

def empty_graph():
  	graph = Graph(password="1happydog")
	graph.run("MATCH(n) DETACH DELETE n;")