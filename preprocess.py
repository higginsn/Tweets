#Nick Higgins (higginsn)
import re, os, glob, sys
from porter import PorterStemmer

#contraction dictionary originally from http://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python
contractions = { 
	"ain't": "am not",
	"aren't": "are not",
	"can't": "cannot",
	"can't've": "cannot have",
	"'cause": "because",
	"could've": "could have",
	"couldn't": "could not",
	"couldn't've": "could not have",
	"didn't": "did not",
	"doesn't": "does not",
	"don't": "do not",
	"hadn't": "had not",
	"hadn't've": "had not have",
	"hasn't": "has not",
	"haven't": "have not",
	"he'd": "he would",
	"he'd've": "he would have",
	"he'll": "he will",
	"he'll've": "he will have",
	"he's": "he is",
	"how'd": "how did",
	"how'd'y": "how do you",
	"how'll": "how will",
	"how's": "how is",
	"i'd": "i would",
	"i'd've": "i would have",
	"i'll": "i will",
	"i'll've": "i will have",
	"i'm": "i am",
	"i've": "i have",
	"isn't": "is not",
	"it'd": "it would",
	"it'd've": "it would have",
	"it'll": "it will",
	"it'll've": "it will have",
	"it's": "it is",
	"let's": "let us",
	"ma'am": "madam",
	"mayn't": "may not",
	"might've": "might have",
	"mightn't": "might not",
	"mightn't've": "might not have",
	"must've": "must have",
	"mustn't": "must not",
	"mustn't've": "must not have",
	"needn't": "need not",
	"needn't've": "need not have",
	"o'clock": "of the clock",
	"oughtn't": "ought not",
	"oughtn't've": "ought not have",
	"shan't": "shall not",
	"sha'n't": "shall not",
	"shan't've": "shall not have",
	"she'd": "she would",
	"she'd've": "she would have",
	"she'll": "she will",
	"she'll've": "she will have",
	"she's": "she is",
	"should've": "should have",
	"shouldn't": "should not",
	"shouldn't've": "should not have",
	"so've": "so have",
	"so's": "so is",
	"that'd": "that would",
	"that'd've": "that would have",
	"that's": "that is",
	"there'd": "there would",
	"there'd've": "there would have",
	"there's": "there is",
	"they'd": "they would",
	"they'd've": "they would have",
	"they'll": "they will",
	"they'll've": "they will have",
	"they're": "they are",
	"they've": "they have",
	"to've": "to have",
	"wasn't": "was not",
	"we'd": "we would",
	"we'd've": "we would have",
	"we'll": "we will",
	"we'll've": "we will have",
	"we're": "we are",
	"we've": "we have",
	"weren't": "were not",
	"what'll": "what will",
	"what'll've": "what will have",
	"what're": "what are",
	"what's": "what is",
	"what've": "what have",
	"when's": "when is",
	"when've": "when have",
	"where'd": "where did",
	"where's": "where is",
	"where've": "where have",
	"who'll": "who will",
	"who'll've": "who will have",
	"who's": "who is",
	"who've": "who have",
	"why's": "why is",
	"why've": "why have",
	"will've": "will have",
	"won't": "will not",
	"won't've": "will not have",
	"would've": "would have",
	"wouldn't": "would not",
	"wouldn't've": "would not have",
	"y'all": "you all",
	"y'all'd": "you all would",
	"y'all'd've": "you all would have",
	"y'all're": "you all are",
	"y'all've": "you all have",
	"you'd": "you would",
	"you'd've": "you would have",
	"you'll": "you will",
	"you'll've": "you will have",
	"you're": "you are",
	"you've": "you have"
}

stopwords = {
	"a",
	"all",
	"an",
	"and",
	"any",
	"are",
	"as",
	"at",
	"be",
	"been",
	"but",
	"by ",
	"few",
	"from",
	"for",
	"have",
	"he",
	"her",
	"here",
	"him",
	"his",
	"how",
	"i",
	"in",
	"is",
	"it",
	"its",
	"many",
	"me",
	"my",
	"none",
	"of",
	"on ",
	"or",
	"our",
	"she",
	"some",
	"the",
	"their",
	"them",
	"there",
	"they",
	"that ",
	"this",
	"to",
	"us",
	"was",
	"what",
	"when",
	"where",
	"which",
	"who",
	"why",
	"will",
	"with",
	"you",
	"your"
}

# def main():
# 	with open('stopwords') as f:
# 		for line in f:
# 			key = line
# 			key = key.replace('\r', '')
# 			key = key.replace('\n', '')
# 			key = key.replace(' ', '')
# 			value = 1
# 			stopwords[key] = value

# 	files = glob.glob(sys.argv[1] + "*")
# 	vocab = {}
	
# 	for filename in files:
# 		f = open(filename, 'r')
# 		words = f.read()

# 		#From spec: "apply, in order: removeSGML, tokenizeText, removeStopwords, stemWords"
# 		tagless = removeSGML(words)
# 		wordList = tokenizeText(tagless.lower())
# 		wordList = removeStopwords(wordList)
# 		wordList = stemWords(wordList)

# 		for word in wordList:
# 			if word != '': # don't add ' ' characters to vocab
# 				vocab[word] = vocab[word] + 1 if word in vocab else 1

# 	# sort by frequency, then alphabetical order
# 	sortedVocab = sorted(vocab.items(), key=lambda x: (-x[1], x[0]))
	
# 	totalWordCount = sum(vocab.values())
# 	totalVocab = len(sortedVocab)

# 	# output to file
# 	f = open('preprocess.output', 'w')

# 	f.write("Words " + str(totalWordCount) + "\n")
# 	f.write("Vocabulary " + str(totalVocab) + "\n")
# 	f.write("Top 50 words" + "\n")

# 	for index in range(1, min(51, len(sortedVocab))):
# 		f.write(str(sortedVocab[index-1][0]) + " " + str(sortedVocab[index-1][1]) +"\n")

def preprocess(input):
	input = removeSGML(input)
	input = tokenizeText(input.lower())
	input = removeStopwords(input)
	input = stemWords(input)
	return input


def removeSGML(input):
	cleaner = re.compile('<.*?>')
	tagless = re.sub(cleaner, '', input)
	return tagless

def tokenizeText(input):
	#remove lone characters mostly for periods
	input = re.compile('\s+[^a-z0-9]\s+').sub(' ', input)

	#remove leading and trailing slashes (slashes should only occur inside of numbers/letters for dates)
	input = re.compile(r'\s+/|\s+\\|/\s+|\\\s+').sub(' ', input)

	#remove leading and trailing apostrophe's. Covers quoted words and words with trailing possessive
	input = re.compile(r"\s+\'+|\'+\s+").sub(' ', input)

	#remove parentheses
	input = input.replace("(", ' ')
	input = input.replace(")", ' ')

	input = re.compile(r'[!|?]+').sub(' ', input)
	input = re.compile(r'\.+').sub('', input)


	#split words on spaces, remove commas that aren't in the format 1,400
	words = re.split('\s+|(?<!\d)[,]|[,](?!\d)', input.strip())


	#remove lone periods
	#words = list(filter(('.').__ne__, words))

	for index, word in enumerate(words):
		#removes ending periods after NUMBERS only (letters followed by a period are acronyms/abbr/initials)
		try:
			if word.endswith('.') and word.count('.') == 1 and (word == '.' or word[-2].isdigit()):
				words[index] = word[:-1]
		except:
			print word

		#expands contractions
		if word in contractions:
			expanded = re.split('\s+', contractions[word])
			words[index] = expanded[0];
			for word in expanded[1:]:
				words.append(word)

		#turns possessive into two tokens, word and 's
		elif word.count("'s") > 0 and word != "'s":
			words[index].replace("'s", '')
			words.append("'s")
	
	return words

def removeStopwords(input):
	words = input

	indexesToRemove = []
	for index, word in enumerate(words):
		if word in stopwords:
			indexesToRemove.append(index)
		if word.startswith("@"):
			indexesToRemove.append(index)
		if word == "":
			indexesToRemove.append(index)

	for index in reversed(indexesToRemove):
		del words[index]

	return words


def stemWords(input):
	porter = PorterStemmer()
	words = input

	for index, word in enumerate(words):
		words[index] = porter.stem(word, 0, len(word) - 1)
	return words
