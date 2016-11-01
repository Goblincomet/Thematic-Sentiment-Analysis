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
