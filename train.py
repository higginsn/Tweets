import preprocess
import sys
import os
import math
import re

negsentiments = {"empty", "anger", "boredom", "hate", "sadness", "worry"}
possentiments = {"enthusiasm", "fun", "happiness", "love", "relief"}

def train():
	positives = {}
	negatives = {}
	vocabsize = 0.0
	poswordcount = 0.0
	negwordcount = 0.0
	numpostweets = 0.0
	numnegtweets = 0.0
	inputfile = open(os.path.dirname(__file__) + "trainingdata.csv", "r")
	for line in inputfile:
		line = line[11:-1]
		line = line.strip("\"")
		sentiment, user, tweet = line.split("\",\"")
		tokens = preprocess.preprocess(tweet)
		#add to count dictionaries for truths or lies
		if sentiment in negsentiments:
			numnegtweets += 1
			for token in tokens:
				negwordcount += 1
				if token not in negatives and token not in positives:
					vocabsize += 1
				if token in negatives:
					negatives[token] += 1.0
				else:
					negatives[token] = 1.0
		elif sentiment in possentiments:
			numpostweets += 1
			for token in tokens:
				poswordcount += 1
				if token not in negatives and token not in positives:
					vocabsize += 1
				if token in positives:
					positives[token] += 1.0
				else:
					positives[token] = 1.0

	#turn dictionary counts into conditional probabilities
	for word, val in positives.items():
		newval = (positives[word] + 1) / (poswordcount + vocabsize)
		positives[word] = newval
	for word, val in negatives.items():
		newval = (negatives[word] + 1) / (negwordcount + vocabsize)
		negatives[word] = newval
	#output
	outputfile = open("positives.txt", "w")
	outputfile.write("vocab size, positive word count, number of positive tweets\n")
	outputfile.write(str(vocabsize) + ", " + str(poswordcount) + ", " + str(numpostweets) + "\n")
	for word, prob in positives.items():
		outputfile.write(word + " " + str(prob) + "\n")
	outputfile = open("negatives.txt", "w")
	outputfile.write("vocab size, negative word count, number of negative tweets\n")
	outputfile.write(str(vocabsize) + ", " + str(negwordcount) + ", " + str(numnegtweets) + "\n")
	for word, prob in negatives.items():
		outputfile.write(word + " " + str(prob) + "\n")
	#print sorted(positives.items(), key= lambda x:(x[1], x[0]))
	#print sorted(negatives.items(), key= lambda x:(x[1], x[0]))

	return positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize

def doshit(positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize):
	inputfile = open(os.path.dirname(__file__) + "trumptweets.csv", "r")
	pcount = 0
	ncount = 0
	count = 1
	for line in inputfile:
		line = line[:-2]
		line = line.strip("\"")
		symbol, date, time, tweet, sentiment = line.split("\",\"")
		tokens = preprocess.preprocess(tweet)
		probpos = math.log(numpostweets / (numpostweets + numnegtweets))
		probneg = math.log(numnegtweets / (numpostweets + numnegtweets))
		for token in tokens:
			if token in positives:
				probpos += math.log(positives[token])
			else:
				probpos += math.log(1.0 / (poswordcount + vocabsize))
			if token in negatives:
				probneg += math.log(negatives[token])
			else:
				probneg += math.log(1.0 / (negwordcount + vocabsize))
		#return
		if probpos >= probneg:
			print str(count) + " " + "positive " + sentiment
			if sentiment != "Positive":
				pcount += 1
		else:
			print str(count) + " " + "negative " + sentiment
			if sentiment != "Negative":
				ncount += 1
		count += 1
	print pcount, ncount

positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize = train()
doshit(positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize)