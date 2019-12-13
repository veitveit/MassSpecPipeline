if __name__ == '__main__':
	import requests
	import json
	from zipfile import ZipFile
	from os.path import join
	import time
	import re
	import random
	from bs4 import BeautifulSoup
	import os
	from urllib import parse
	import pickle
	import pandas as pd
	import codecs
	import sys


def get_accessions(path):
	all_accessions = []
	accessions	 = 'accessions.txt'
	if os.path.exists(path+accessions):
		rm = validated_input('File already exists, overwrite?',('y','n'))
		if rm == 'y':
			os.remove(path+accessions)

	url  = 'http://ftp.pride.ebi.ac.uk/pride/data/archive/'
	page = requests.get(url).text	
	soup = BeautifulSoup(page, 'html.parser')
	#Level 1 - Getting the years
	for level1 in soup.find_all('a', href = True):
		if '20' not in level1['href']:
			continue #To avoid the non years
		page_2 = requests.get(url+level1['href']).text
		soup_2 = BeautifulSoup(page_2, 'html.parser')
		#Level 2 - year subfolders
		for level2 in soup_2.find_all('a', href = True):
			try:
				int(level2['href'][0:2]) #Only look at numerics...
			except Exception:
				continue
			print('Getting accessions from '+level1.text+level2.text, end = '\r')
			page_3 = requests.get(url+level1['href']+level2['href']).text
			soup_3 = BeautifulSoup(page_3, 'html.parser')

			#Level 3- actual accession numbers.
			for level3 in soup_3.find_all('a', href = True):
				accession = level3['href'].replace('/','')
				if len(accession) == len('PRD000000'):
					all_accessions.append(accession)

	with open(path+accessions, "wb") as pa:
		pickle.dump(all_accessions, pa)


def accessions_metadata(path):
	metadata = 'accessions.json'
	accessions	 = 'accessions.txt'
	if os.path.exists(path+metadata):
		overwrite = validated_input('Metadata already exists, wanna overwrite?',('y','n'))
		if overwrite == 'y':
			os.remove(path+metadata)	
		else:
			quit()

	with open(path+accessions, "rb") as pa:
		pride_accessions = pickle.load(pa) #Loading the data
	
	outfile = open(join(path,metadata),'a')

	for i, f in enumerate(pride_accessions):
		print('Progress {:2.1%}'.format(i / len(pride_accessions)), end='\r')
		api = 'https://www.ebi.ac.uk/pride/ws/archive/project/'+f
		apijson = requests.get(api).json()
		
		metadata = {}
		maxquant = False
		for g in apijson:
			metadata[g] = apijson[g]
			if 'maxquant' in str(apijson[g]).lower():
				maxquant = True
		metadata['maxquant'] = maxquant

		files = 'https://www.ebi.ac.uk/pride/ws/archive/file/list/project/'+f
		filesjson = requests.get(files).json()
		filetypes = []
		for f in filesjson['list']:
			filetype = f['fileName'][re.search('\.',f['fileName']).span()[1]:]
			if filetype not in filetypes:
				filetypes.append(filetype)
		metadata['filetypes'] = filetypes
		
		if metadata['maxquant'] == True and 'zip' in metadata['filetypes']:
			try:
				for f in filesjson['list']:
					filetype = f['fileName'][re.search('\.',f['fileName']).span()[1]:]
					if f['fileType'] == 'SEARCH' and filetype == 'zip':
						zipfile = f['downloadLink']
						break
				os.system('wget -q -O '+path+'file.zip '+zipfile)

				with ZipFile(path+'file.zip','r') as zipped:
					ziplist = zipped.namelist()
				os.remove(path+'file.zip')

				for xx in ziplist:
					if 'allPeptides.txt' in xx:
						metadata['allpeptides'] = True
						break
			except Exception:
				metadata['allpeptides'] = False
		else:
			metadata['allpeptides'] = False
		
		outfile.write(json.dumps(metadata)+'\n')


def replace_accessions():
	outfile = open(metapath+'accessions2.json','a')
	for line in open(metapath+'accessions.json','r'):
		data = json.loads(line)
		with open(metapath+'accessions.txt', "rb") as pa:
			pride_accessions = pickle.load(pa)
		for f in pride_accessions:
			if data['accession'] in f:
				data['accession'] = f
				outfile.write(json.dumps(data)+'\n')


def validated_input(prompt, valid_values):
	valid_input = False
	while not valid_input:
		value	   = input(prompt + ' | ' + ' / '.join(valid_values)+"\n")
		valid_input = value in valid_values
	return value


if __name__ == '__main__':
	# datapath = 'Data/'
	datapath = '/data/ProteomeToolsRaw/'
	metapath = datapath+'metadata/'

	cmd = sys.argv[1]
	
	#Download pride accession numbers.
	if cmd == 'accessions':
		get_accessions(path = metapath)

	#Get Metadata for all accession numbers
	if cmd == 'metadata':
		accessions_metadata(path = metapath)

	if cmd == 'replace':
		replace_accessions()

# python3 pwebscrape.py accessions
# python3 pwebscrape.py metadata
# python3 pwebscrape.py replace
