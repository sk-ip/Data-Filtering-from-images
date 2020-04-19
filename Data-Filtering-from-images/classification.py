import os
import re
import nltk
import spacy
from nltk.tree import Tree
from geotext import GeoText
from nltk.tag import pos_tag
from address_parser import Parser
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk
from generate_csv import generate_csv
from nltk.tokenize import word_tokenize
from nameparser.parser import HumanName
from nltk.tokenize import SpaceTokenizer
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk import sent_tokenize, word_tokenize, pos_tag

stop = stopwords.words("english")

def preprocess(sent):
	sent = nltk.word_tokenize(sent)
	sent = nltk.pos_tag(sent)
	return sent

def getCompanyName(filename):
	with open(filename, "r") as text_file:
		lines = text_file.read()

	addrs = []
	nlp = spacy.load('en_core_web_sm')
	ne_tree = ne_chunk(pos_tag(word_tokenize(lines)))
	doc = nlp(lines)
	for chunk in doc.ents:
		if chunk.label_ == "ORG":
			addrs.append(chunk[0])
			break
	return addrs

def getRegexAddress(text):
	r = re.compile("^\d+\s[A-z]+\s[A-z]+")
	return r.findall(text)

def getItems(filename):
	with open(filename, "r") as text_file:
		lines = text_file.read()
	items = []
	nlp = spacy.load('en_core_web_sm')
	sent = preprocess(lines)
	pattern = 'NP: {<DT>?<JJ>*<NN>}'
	cp = nltk.RegexpParser(pattern)
	cs = cp.parse(sent)
	iob_tagged = tree2conlltags(cs)
	for tup in iob_tagged:
		if tup[1] == 'NNP' and tup[2] == 'O':
			items.append(tup[0])
	return items

def getNamesOfCompanies(filename):
	with open(filename, "r") as text_file:
		text = text_file.read()

	nlp = spacy.load('en_core_web_sm')
	sent = preprocess(text)
	pattern = 'NP: {<DT>?<JJ>*<NN>}'
	cp = nltk.RegexpParser(pattern)
	cs = cp.parse(sent)
	orgs = []
	iob_tagged = tree2conlltags(cs)
	ne_tree = ne_chunk(pos_tag(word_tokenize(text)))

	doc = nlp(text)
	for chunk in doc.ents:
		if chunk.label_ == "ORG":
			orgs.append(chunk[0])
	return orgs

def getAddress(filename):
	with open(filename,"r") as text_file:
		head = [next(text_file).rstrip('\r\n') for x in range(3)]
	return head

def getInvoiceNumber(filename):
	invoices = ["INVOICE NO #", "Invoice Number", "Bill ID", "Bill No:", "Bill No :", "Invoice Humber ", "Bill No. :", "Invoice No :"]
	with open(filename, "r") as text_file:
		ans = []
		for line in text_file.readlines():
			for sbstr in invoices:
				if sbstr in line:
					ans.append(line.split(sbstr)[-1])
	return ans

def getTotalAmount(filename):
	words = ["Total Amt :", "Total Amt", "Total :", "TOTAL:", "Net Amount:", "Subtotal", "Total Invoice Value", "SUBTOTAL", "Amount :", "Grand Total"]
	with open(filename, "r") as text_file:
		ans = []
		for line in text_file.readlines():
			for sbstr in words:
				if sbstr in line:
					allnumbers = re.findall(r'\d+', line)
					ans = list(map(int, allnumbers))

	ans[:] = (value for value in ans if value != 0)
	return ans

def getCityNames(text):
	places = GeoText(text)
	return places.cities

def getPhoneNumbers(text):
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(text)
    all_numbers = [re.sub(r'\D', '', number) for number in phone_numbers]
    ans = []
    for num in all_numbers:
        if len(num) == 10:
            ans.append(num)
    return ans

def amount(text):
	r = re.compile(r'(/^(?:0|[1-9]\d*)(?:\.(?!.*000)\d+)?$/)')
	return r.findall(text)

def extract_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

def ie_preprocess(document):
    document = ' '.join([i for i in document.split() if i not in stop])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)

def extract_names(document):
    names = []
    sentences = ie_preprocess(document)
    for tagged_sentence in sentences:
        for chunk in nltk.ne_chunk(tagged_sentence):
            if type(chunk) == nltk.tree.Tree:
                if chunk.label() == 'PERSON':
                    names.append(' '.join([c[0] for c in chunk]))
    return names

def getDates(text):
	r1 = r"[\d]{1,2}/[\d]{1,2}/[\d]{4}"
	r2 = r"[\d]{1,2}-[\d]{1,2}-[\d]{2}"
	r3 = r"[\d]{1,2} [ADFJMNOS]\w* [\d]{4}"
	r4 = r"[\d]{1,2} [ADFJMNOS]\w* [\d]{4}"
	r = re.compile("(%s|%s|%s|%s)" % (r1, r2, r3, r4))
	dates = r.findall(text)
	return dates


def classify_data():
	data_dict = {}
	for t_file in os.listdir("./text"):
		with open(os.path.join("./text", t_file), "r") as text_file:
			all_lines = text_file.read()
		data = {}
		data["phone_numbers"] = getPhoneNumbers(all_lines)
		data["emails"] = extract_email_addresses(all_lines)
		data["date"] = getDates(all_lines)
		data["totalamount"] = getTotalAmount(os.path.join("./text", t_file))
		data["invoice"] = getInvoiceNumber(os.path.join("./text", t_file))
		data["company"] = getCompanyName(os.path.join("./text", t_file))
		data["address"] = getAddress(os.path.join("./text", t_file))
		data_dict["{}".format(t_file)] = data

	generate_csv(data_dict, "bill_info.csv")
