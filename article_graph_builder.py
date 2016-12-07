from __future__ import division
import networkx as nx
import json
import operator
import re

class Article:
	def __init__(self, name, data):
		self.name = name
		self.entities = {}
		self.sentiment = 0
		self.emotions = {'anger': 0, 'joy': 0, 'fear': 0, 'sadness': 0, 'disgust': 0}

		n = len(data)
		for sentence in data:
			self.addSentiment(sentence['docSentiment'], n)
			self.addEmotion(sentence['docEmotions'], n)

			words = sentence['entities']+sentence['keywords']
			for w in words:
				self.addEntity(w, n*len(words))

	def addEntity(self, w, n=1):
		weight = float(w['relevance'])
		self.addSentiment(w['sentiment'], n, weight)
		self.addEmotion(w['emotions'], n, weight)

		text = w['text'].lower()
		if text not in self.entities:
			self.entities[text] = 0
		self.entities[text] = max(self.entities[text], weight)

	def addSentiment(self, data, n=1, weight=1):
		if data['type'] != 'neutral':
			self.sentiment += weight*float(data['score'])/n

	def addEmotion(self, data, n=1, weight=1):
		for m in self.emotions:
			self.emotions[m] += weight*float(data[m])/n

def compareEntities(a1, a2):
	set1 = set(a1.entities)
	set2 = set(a2.entities)

	matches = set1 & set2
	misses  = set1 ^ set2

	matchWeight = sum([a1.entities[t]+1 for t in a1.entities if t in matches])
	missWeight  = sum([a1.entities[t]+1 for t in a1.entities if t in misses ]) + sum([a2.entities[t]+1 for t in a2.entities if t in misses])

	p = 1.0*matchWeight/(1+matchWeight+missWeight)
	if p > 0.06:
		return p
	return 0

def compareSentiment(a1, a2):
	return abs(a1.sentiment-a2.sentiment)

def compareEmotions(a1, a2):
	return max([abs(a1.emotions[e] - a2.emotions[e]) for e in a1.emotions])

def addEdges(graph, articles):
	for i in range(len(articles)):
		for j in range(i+1, len(articles), 1):
			a1 = articles[i]
			a2 = articles[j]
			e = compareEntities(a1, a2)
			if e > 0:
				graph.add_edge(a1, a2,
					entity_weight=e,
					sentiment_weight=compareSentiment(a1, a2),
					emotion_weight=compareEmotions(a1, a2))

def build_article_graph_from_data(data):
	articles = []
	for article in data:
		articles.append(Article(article, data[article]))

	graph = nx.Graph()
	addEdges(graph, articles)

	for e in graph.edges(data=True):
		print e[0].name
		print e[1].name
		if 'entity_weight' in e[2]:
			print 'e', e[2]['entity_weight']
		if 'sentiment_weight' in e[2]:
			print 's', e[2]['sentiment_weight']
		if 'emotion_weight' in e[2]:
			print 'm', e[2]['emotion_weight']
		print
	return graph
