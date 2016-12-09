# Opinionated NLP Analysis

## Summary ##

To objectively determine the semantic relationship between different selections of text has
proven itself to be a difficult problem. Specifically, a computational method for identify-
ing and quantifying the bias between news articles written on the same topic has yet to
be implemented. Methods for sentiment and thematic extraction of textual articles have
been previously explored. However, these algorithms have not been applied together in a
comprehensive application to form any relationship between articles.

We propose a novel solution that leverages natural language processing methods including
theme extraction and sentiment analysis to graph a set of articles into clusters based on their
themes and to convey the sentimental differences between articles. This can be applied to
display a side-by-side comparison of two articles presenting opposing viewpoints on a specific
topic.

## Dependencies ##

* Linux Python package manager, pip.
* Watson Developer Cloud 
	* You will need a Watson developer API key and an open AlchemyAPI application in your account to run the app.
		* Go to http://www.ibm.com/watson/developercloud/ and make an account if you do not have one already.
		* Create an AlchemyAPI application and use the API key from that when running this app.
	* For Linux users, run command `sudo pip install -- upgrade watson-developer-cloud`
	* Link to github: https://github.com/watson-developer-cloud/python-sdk
* networkx, python graph library
	* For Linux users, run command `sudo pip install networkx`
	* Documentation: https://networkx.readthedocs.io/en/stable/overview.html
* neo4j, for graph visualization
	* For Linux users, run the following commands:
		* `wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -`
		* `echo 'deb http://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list`
		* `sudo apt-get update`
		* `sudo apt-get install neo4j`
	* Documentation: https://neo4j.com/
* py2neo, for interfacing neo4j with Python
	* For Linux users, run command: `sudo pip install py2neo`
	* Documentation: http://py2neo.org/v3/index.html

## Usage / How To Make It Go ##

There are two functionalities included in the implementation, one to collect article data from  AlchemyAPI, and one to build the article graph.
* To collect article data, run command: `python main.py [AlchemyAPI key]`
* To build the article graph, run command `python main.py [AlchemyAPI key] [-B/--buildGraph]`
	* Before running this command, ensure the neo4j database is already running by running command `sudo neo4j start` (refer to notes.txt for more details)

If you built the graph using the second command, you can play with it using neo4j by opening the web adress http://localhost:7474/browser/ 

## Goals ##

We have two major objectives for our project:

1. Extract themes from articles
	* Weight each theme by significance and/or prevalence in the article
	* Categorize each extracted theme as being positive, negative, or neutral

2. Create links between articles that share common themes
	* Quantify the links by the weight of the shared themes in both articles
	* Categorize the link as being either positive or negative

The uniquely defining feature of this project is the use of themes to both relate and define
the relation between news articles. This is beneficial to the users (the Opinionated project)
since it gives a powerful and potentially more accurate way to cluster articles than simple
keyword extraction.

## Architecture and Approach ##

The algorithm will have two main parts; theme extraction and link creation.

In the theme extraction step, every article in the input set will be parsed by sentence and
have any themes and sentiments associated with them identified using either IBM’s Alchemy
API or Google’s Cloud Natural Language API. Each theme found will be stored and counted,
along with a sentiment score of either positive, negative, or neutral. After all sentences go
through this process, all the themes found will get sorted based on how many times they
appeared, and the overall sentiment for each will be decided based on most common score.
	
Once all articles have gone through the first step, a graph relating all of them can then
be created. Links will be formed between every pair of articles that share common themes,
where each link will have two critical attributes. The first is weight, which will be based on
the difference between the order of theme rankings, where higher weights come from more
shared themes being highly ranked in both articles. The second is sentiment, which will be
determined by how many shared themes have the same sentiment value, where if most do
then the articles agree, otherwise they do not.
	
After completion of the second step, a graph based around theme clusters will have been
formed with links stating the agreement or disagreement between a pair of articles.
