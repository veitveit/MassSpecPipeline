if 'import' == 'import':
	import json
	import os
	import glob
	import sys
	import shutil
	import random
	import re
	import numpy as np
	from collections import defaultdict

#Pathfinding
datapath = "/data/ProteomeToolsRaw/Images/"
trainpath = datapath+'training/'
valpath = datapath+'validation/'

if not os.path.exists(datapath):
	os.mkdir(datapath)

#Reset images
dirs = [os.path.dirname(p) for p in glob.glob(datapath+"/*/*")]
udirs = np.unique(dirs)

if dirs != [] and (dirs[0] == trainpath[:-1] or dirs[0] == valpath[:-1]):
	dirs = [os.path.dirname(p) for p in glob.glob(datapath+"/*/*/*")]
	udirs = np.unique(dirs) 

if len(udirs) != 0:
	print("Do you want to reset image folders? y/n")
	reset = input()
	if reset == "yes" or reset == "y":
		for files in udirs:
			images = [f for f in glob.glob(files + "**/*.png", recursive=True)]
			print(range(0,len(images),10000))
			#print(images[0:10000])
			#for imgs in images:
			#	os.system("mv "+imgs+" "+datapath)
			#shutil.rmtree(files) 	 
quit()
#Move images
def classifyImages(classes):
	print("Do you wanna split the data into training and validation? y/n")
	split = input()
	if split == "yes" or split == "y":

		print("What should the validation % be?")
		splitratio = input()

		if not os.path.exists(trainpath):
			os.mkdir(trainpath)
		if not os.path.exists(valpath):
			os.mkdir(valpath)

		imgdata = {}
		#CREATING TRAINING DATA
		print("Sorting into training data")
		for line in open(datapath+'metadata.json'):
			data = json.loads(line)

			if data['m/z'] > 360 or data['m/z'] < 370: #Filter m/z 

				names = data[imClass]+"/"+data['image']+".png"
				imgdata[names] = data[imClass]

				if not os.path.exists(trainpath+data[imClass]):
					os.mkdir(trainpath+data[imClass])
				if not os.path.exists(valpath+data[imClass]):
					os.mkdir(valpath+data[imClass])
				os.system("mv "+datapath+data['image']+".png "+trainpath+data[imClass]+"/")
			else:
				continue
		
		#CREATING VALIDATION DATA
		print("Sorting into Validation data")
		imgadata = defaultdict(list)
		for k, v in imgdata.items():
			imgadata[v].append(k)
		for f in imgadata:
			splits = round(len(imgadata[f])*(int(splitratio)/100))
			mlist = random.sample(imgadata[f],k=splits)
			for elements in mlist:
				os.system("mv "+trainpath+elements+" "+valpath+elements)

	elif split == "no" or split == "n":
		for line in open(datapath+'metadata.json'):
			data = json.loads(line)
			if not os.path.exists(datapath+data[imClass]):
				os.mkdir(datapath+data[imClass])
			os.system("mv "+datapath+data['image']+".png "+datapath+data[imClass]+"/")	
	else: quit()


if __name__ == '__main__':

	imClass = sys.argv[1]

	if imClass == "reset":
		quit()
	else:
		classifyImages(classes = imClass)


