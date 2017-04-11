import preprocess
import sys
import os
import math
import re

negsentiments = {"empty", "anger", "boredom", "hate", "sadness", "worry"}
possentiments = {"enthusiasm", "fun", "happiness", "love", "relief"}

class Date:
	def __init__(self, month = 0, day = 0, year = 0):
		self.month = month
		self.day = day
		self.year = year

	def daylightsavings(self):
		if (self.month == 11 and self.day >= 6) or self.month == 12:
			return true
		if (self.month == 3 and self.day <= 12) or self.month < 3:
			return true
		return false

class TweetData:
	def __init__(self, symbol = "", date = Date(), time = "", tweet = "", sentiment = ""):
		self.symbol = symbol
		self.Date = date
		self.time = time
		self.tweet = tweet
		self.sentiment = sentiment

class Analysis:
	def __init__(self):
		self.start = 0.0
		self.end = 0.0
		self.max = 0.0
		self.min = 0.0
		self.total = 0.0
		self.minutes = 0.0
		self.average = 0.0
		self.trend = 0.0

	def calculate(self):
		self.average = self.total / self.minutes
		self.trend = (self.end - self.start) / self.minutes

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
	alldata = []
	for line in inputfile:
		line = line[:-2]
		line = line.strip("\"")
		symbol, date, time, tweet, sentiment = line.split("\",\"")
		date = date.split(" ")
		date = Date(date[1], date[0], date[2])
		data = TweetData(symbol, date, time, tweet)


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
			data.sentiment = "positive"
			print str(count) + " " + "positive " + sentiment
			if sentiment != "Positive":
				pcount += 1
		else:
			data.sentiment = "negative"
			print str(count) + " " + "negative " + sentiment
			if sentiment != "Negative":
				ncount += 1
		count += 1
		alldata.append(data)
	print pcount, ncount
	return alldata


def recordshit(start, lines):
	hoursummary = Analysis()
	for i in range(start, min(start + 60, 781)):
		price = float(lines[i].split(" ")[-1])
		hoursummary.total += price
		if i == start:
			hoursummary.start = price
			hoursummary.min = price
		if i == start + 59 or i == 780:
			hoursummary.end = price
		hoursummary.min = min(hoursummary.min, price)
		hoursummary.max = max(hoursummary.max, price)
		hoursummary.minutes += 1
	hoursummary.calculate()
	return hoursummary

def comparetostock(alldata, folder):
	outputfile = open(os.path.dirname(__file__) + "stock_stuff", "w")
	for filename in os.listdir(os.path.dirname(__file__) + folder):
		stockfile = open(os.path.dirname(__file__) + folder + "/" + filename, "r")
		lines = stockfile.readlines()
		filename = filename[:-4]
		index, symbol, filedate = filename.split("_")
		filedate = filedate.split("-")
		filedate = Date(filedate[1], filedate[0], filedate[2])
		#daylight savings
		if filedate.daylightsavings:
			opentime = "13:31"
			openhour = 13
			closetime = "20:00"
			closehour = 20
		else:
			opentime = "14:31"
			openhour = 14
			closetime = "21:00"
			closehour = 21
		#find starting line based on tweet time
		if alldata[int(index)-1].time > closetime or alldata[int(index)-1].time < opentime:
			startpoint = 390 - 60 #390 lines per day
		else:
			hour, minute = alldata[int(index)-1].time.split(":")
			startpoint = 390 + 60 * (float(hour) - openhour) + (float(minute) - 31) - 60
		#loop through hour before tweet
		beforehour = recordshit(startpoint, lines)
		#loop through hour after tweet
		afterhour = recordshit(startpoint + 60, lines)
		#output
		outputfile.write(index + " " + alldata[int(index)-1].symbol + " " + alldata[int(index)-1].sentiment + "\n")
		outputfile.write(str(beforehour.min) + " " + str(beforehour.max) + " " + str(beforehour.trend) + " " + str(beforehour.average) + "\n")
		outputfile.write(str(afterhour.min) + " " + str(afterhour.max) + " " + str(afterhour.trend) + " " + str(afterhour.average) + "\n\n")
		
		



positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize = train()
alldata = doshit(positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize)
comparetostock(alldata, "stock_data")

