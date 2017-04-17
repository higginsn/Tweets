# Tweets
Goal: Use stock prices of companies to classify the sentiment of President Trump's tweets. Compare accuracy to Naive Bayes (NB) sentiment analysis.

# How to use
run sentimentAnalysis.py in Python

# Code
preprocess.py and porter.py are taken from earlier course projects, optimized for processing tweets.

sentimentAnalysis.py computes sentiment analysis using stock price data from stock_data/ and Naive Bayes. It outputs the accuracy of each method to the console and generates the classifications.txt and stock_results.txt

# Output files
classifications.txt shows each tweet's classifications (stocks and NB) compared to its actual sentiment. For reference, it includes the respective tweet and company symbol.

stock_results.txt shows some of each tweet's stock analysis data that we used to create a classifier.

# Datasets
trumptweets.csv contains a manually generated list of all tweets targeting a publicly traded company from July 21, 2016 to April 1, 2017, including either "positive" or "negative" sentiment tags. This list is used as the test data for the NB method and to collect stock_data.

stock_data/ contains a file of stock prices corresponding to a company's stock on the days surrounding each tweet. The file contains a line for the stock price at every minute of the two-day span. These stock prices are analyzed to classify the tweet.

trainingdata.csv - publicly accessed training data of 40K random tweets with labeled sentiments. This was used to train our NB classifier.

# Results
Stock price classification accuracy: 73%
Naive Bayes accuracy: 76%