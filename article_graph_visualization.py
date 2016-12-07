import sys, re
import matplotlib.pyplot as plt
import networkx as nx

from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph, Path


## HOW TO SET UP NEO4J:
## You need to start neo4j before running the program, using the line '$ sudo neo4j start'
## The first time you do this, open web page 'http://localhost:7474/browser/' and log in and change the password to 1happydog



def get_make_new_node_str(new_node):
	entity_list = [e[0] for e in new_node[1]['node_data'].sorted_entity_list]
	make_new_node_str = "CREATE (a:Article {title:\'" + new_node[0] + "\', entities:" + str(entity_list) + "})"
	return make_new_node_str

def try_py2neo():
	graph = Graph(password="1happydog")
	graph.run("CREATE (person:Person {name:'Alice'}) RETURN person")
	

def export_graph_to_neo4j(article_graph):
	driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "1happydog"))
	empty_graph(driver) # delete all old nodes in the graph db
	session = driver.session()
	#make_new_node_str = 'CREATE (a:Article {title:\'%s\', entities:\'%s\'})'
	for n in article_graph.nodes(data=True):
		make_new_node_str = get_make_new_node_str(n)
		session.run(make_new_node_str)
	for e in article_graph.edges(data=True):
		#print e[0], e[1]
		from_node_return = session.run("MATCH (a:Article) WHERE a.title = \'" + e[0] + "\' RETURN a.title AS title")
		from_node = None
		for r in from_node_return:
			from_node = r["title"]
		to_node_return = session.run("MATCH (a:Article) WHERE a.title = \'" + e[1] + "\' RETURN a.title AS title")
		to_node = None
		for r in to_node_return:
			to_node = r["title"]
		#print "cntr:", cntr
	#session.run("CREATE (a:Person {name:'Arthur', title:'King'})")

  	#result = session.run("MATCH (a:Person) WHERE a.name = 'Arthur' RETURN a.name AS name, a.title AS title")
  	#for record in result:
	#	print("%s %s" % (record["title"], record["name"]))

  	session.close()
  	empty_graph(driver)

def empty_graph():
  	graph = Graph(password="1happydog")
	graph.run("MATCH(n) DETACH DELETE n;")