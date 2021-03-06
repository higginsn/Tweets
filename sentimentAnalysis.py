import preprocess
import sys
import os
import math
import re

#original classifications of training data (trainingdata.csv)
negsentiments = {"empty", "anger", "boredom", "hate", "sadness", "worry"}
possentiments = {"enthusiasm", "fun", "happiness", "love", "relief"}

class Date:
	def __init__(self, month = 0, day = 0, year = 0):
		self.month = month
		self.day = day
		self.year = year

	# used to properly analyze stock data files. DST changes the timestamp labels
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
		self.correctsentiment = ""

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
		self.maxchange = 0.0

	def calculate(self):
		self.average = self.total / self.minutes
		self.trend = self.trend / (self.minutes - 1)

# use training data to computer conditional probabilities, same as assignment 4
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

		#add to count dictionaries for positive or negatives
		if sentiment in negsentiments:
			numnegtweets += 1
			for token in tokens:
				negwordcount += 1
				# vocab contains unique words of both dictionaries
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

	return positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize

# classify tweet's sentiment based on Naive Bayes and given training set
def doshit(positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize):
	inputfile = open(os.path.dirname(__file__) + "trumptweets.csv", "r")
	# used to compute accuracy
	pcount = 0
	ncount = 0
	count = 1

	alldata = []

	for line in inputfile:
		line = line[:-2]
		line = line.strip("\"")

		# read in custom file
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
		data.correctsentiment = sentiment
		
		if probpos >= probneg:
			data.sentiment = "positive"
			if sentiment != "positive":
				pcount += 1
		else:
			data.sentiment = "negative"
			if sentiment != "negative":
				ncount += 1
		count += 1
		alldata.append(data)
	print "Text Sentiment Accuracy: ", float(count - pcount - ncount) / float(count)
	return alldata

# returns a populated Analysis object, which provides important statistical values about the given raw data
def recordshit(start, lines, after):
	hoursummary = Analysis()
	previousprice = 0.0
	currentchange = 0.0
	# only use one hour intervals
	for i in range(start, 781):
		# read in price from stock_data/ file
		price = float(lines[i-1].split(" ")[-1])
		hoursummary.total += price
		if i == start:
			hoursummary.start = price
			hoursummary.min = price
		elif i == 780: #780 is end of file
			hoursummary.end = price
			hoursummary.trend += price - previousprice
		else:
			hoursummary.trend += price - previousprice
		if i != start and after:
			tempdiff = price - previousprice

			# if direction of change is consistent, continue summation, otherwise reset
			if (tempdiff >= 0 and currentchange >= 0) or (tempdiff <= 0 and currentchange <= 0):
				currentchange += tempdiff
			else:
				if abs(currentchange) > abs(hoursummary.maxchange):
					hoursummary.maxchange = currentchange
				currentchange = 0

		previousprice = price
		hoursummary.min = min(hoursummary.min, price)
		hoursummary.max = max(hoursummary.max, price)
		hoursummary.minutes += 1

	# use calculate() to finalize analysis
	hoursummary.calculate()
	return hoursummary

# Use two-day stock data and tweet's timestamp to classify tweet's sentiment
def comparetostock(alldata, folder):
	countgood = 0.0
	count = 0.0
	outputfile = open(os.path.dirname(__file__) + "stock_results.txt", "w")
	prettyoutput = open(os.path.dirname(__file__) + "classifications.txt", "w")

	for filename in os.listdir(os.path.dirname(__file__) + folder):
		stockfile = open(os.path.dirname(__file__) + folder + "/" + filename, "r")
		lines = stockfile.readlines()

		# format information from filename
		filename = filename[:-4]
		index, symbol, filedate = filename.split("_")
		filedate = filedate.split("-")
		filedate = Date(filedate[1], filedate[0], filedate[2])

		# account for daylight savings
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

		#find starting line in file based on tweet time
		if alldata[int(index)-1].time > closetime or alldata[int(index)-1].time < opentime:
			startpoint = 390 - 60 #390 lines per day
		else:
			hour, minute = alldata[int(index)-1].time.split(":")
			startpoint = 390 + 60 * (float(hour) - openhour) + (float(minute) - 31) - 60

		#loop through hour before and after tweet
		beforehour = recordshit(startpoint, lines, False)
		afterhour = recordshit(startpoint + 60, lines, True)

		classify(alldata[int(index)-1], beforehour, afterhour, prettyoutput)

		#output
		outputfile.write(index + " " + alldata[int(index)-1].symbol + " " + alldata[int(index)-1].sentiment + "\n")
		outputfile.write("Hour Before Tweet\n")
		outputfile.write("Minimum	Maximum		Trend 	Average Price\n")
		outputfile.write(str(beforehour.min) + " " + str(beforehour.max) + " " + str(beforehour.trend) + " " + str(beforehour.average) + "\n")
		outputfile.write("Hour After Tweet\n")
		outputfile.write("Minimum	Maximum		Trend 	Average Price 	Maximum Change\n")
		outputfile.write(str(afterhour.min) + " " + str(afterhour.max) + " " + str(afterhour.trend) + " " + str(afterhour.average) + " " + str(afterhour.maxchange/beforehour.average*100) + "\n\n")
		count += 1
		if alldata[int(index)-1].correctsentiment == "positive" and afterhour.maxchange > 0:
			countgood += 1
		elif alldata[int(index)-1].correctsentiment == "negative" and afterhour.maxchange < 0:
			countgood += 1

	print "Stock Sentiment Accuracy: ", countgood / count

		
# outputs sentiment scores across classification methods for comparison
def classify(datapoint, beforehour, afterhour, outputfile):
	outputfile.write("Symbol: " + datapoint.symbol + "\n")
	outputfile.write("Tweet: \"" + datapoint.tweet + "\"\n")
	outputfile.write("Text Sentiment: " + datapoint.sentiment + "\n")

	# we found maxchange, or longest consecutive change, to be the most reflective statistic for sentiment classification.
	# if the maxchange is positive, it generally corresponds to a peak or jump in the graph, which is correlated to a positive tweet.
	if afterhour.maxchange > 0:
		outputfile.write("Stock Sentiment: positive\n")
	else:
		outputfile.write("Stock Sentiment: negative\n")
	outputfile.write("Correct Sentiment: " + datapoint.correctsentiment + "\n\n")

# run shit
def main():
	positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize = train()
	alldata = doshit(positives, poswordcount, numpostweets, negatives, negwordcount, numnegtweets, vocabsize)
	comparetostock(alldata, "stock_data")

main()
