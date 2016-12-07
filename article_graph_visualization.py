import sys, re
import matplotlib.pyplot as plt
import networkx as nx

from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship


## HOW TO SET UP NEO4J:
## You need to start neo4j before running the program, using the line '$ sudo neo4j start'
## The first time you do this, open web page 'http://localhost:7474/browser/' and log in and change the password to 1happydog



def make_new_graph_node(new_node):
	entity_list = [e[0] for e in new_node[1]['node_data'].sorted_entity_list]
	#make_new_node_str = "CREATE (a:Article {title:\'" + new_node[0] + "\', entities:" + str(entity_list) + "})"
	new_graph_node = Node("Article", title = new_node[0], entities=entity_list)
	return new_graph_node

def try_py2neo():
	graph = Graph(password="1happydog")
	graph.run("CREATE (person:Person {name:'Alice'}) RETURN person")
	

def export_graph_to_neo4j(article_graph):
	empty_graph() # delete all old nodes in the graph db
	graph = Graph(password="1happydog")
	tx = graph.begin()
	graph_node_dict = {}
	#for n in article_graph.nodes(data=True):
	#	new_graph_node = make_new_graph_node(n)
	#	tx.create(new_graph_node)
	#	graph_node_dict[n[0]] = new_graph_node
	for e in article_graph.edges(data=True):
		#print e[0], e[1]
		if e[0] not in graph_node_dict:
			new_graph_node = make_new_graph_node(n)
		g_node1 = graph_node_dict[e[0]]
		g_node2 = graph_node_dict[e[1]]
		new_edge = Relationship(g_node1, "KNOWS", g_node2)
		tx.create(new_edge)
	tx.commit()
  	#empty_graph()

def empty_graph():
  	graph = Graph(password="1happydog")
	graph.run("MATCH(n) DETACH DELETE n;")