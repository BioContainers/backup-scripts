#!/usr/bin/python3

from bs4 import BeautifulSoup
from packaging import version
from collections import defaultdict
import difflib
import argparse
import wget
import sys
import os

######################
###Sorting versions###
######################

def versionKey (e):
	return version.parse(e)

def order_version_list (versionList):
	versionList.sort(key=versionKey)
	return versionList

########################
###Not classified yet###
########################

def is_reference_outdated (softwareName, refVersion, targetName, targetList, output) :
	#print ("Comparing "+refVersion+" and "+ " ".join(targetList))
	idx=0
	targetList = order_version_list(targetList)
	while idx < len(targetList):
		if version.parse(refVersion) < version.parse(targetList[idx]) :
			break
		idx += 1
	if idx != len(targetList) :
		print(softwareName+"'s top version "+refVersion+" is outdated by "+targetName+"'s versions:", file=output)
		print(targetList[idx:], file=output)
	else:
		print(softwareName+" is up-to-date compared to "+targetName, file=output)

#################
###Main method###
#################

parser = argparse.ArgumentParser(description="Tests whether a given set of softwares have more up-to-date recipes in BioConda")
parser.add_argument('software', help="Either a single software name or a file containing software names and versions")
parser.add_argument('-v','--versions', nargs='*', help="If testing a single software, a series of versions separated by blank spaces")
parser.add_argument('-f','--use-file', action="store_true", help="If used, the script will expect a file containing one software name and one or more version numbers per line as input")
parser.add_argument('-u','--url',default="https://bioconda.github.io/recipes.html", help="The url where the html table to parse can be found")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

##Downloading the recipes
in_file=wget.download (url=args.url)

##Opening it
html_doc = open (in_file,"r")

##Getting all BioConda's recipes
#Parsing the html doc
recipes = BeautifulSoup(html_doc, features="html.parser")
#Initialising the list to contain dicts by default
bioconda_recipes = defaultdict(list)
for row in recipes.find_all('tr'):
	crtTool=row.get_text(" ").split(" ")
	crtSoft=crtTool[0]
	crtVersion=crtTool[1]
	bioconda_recipes[crtSoft].append(crtVersion)
html_doc.close()

##Getting software names to compare
ref_soft = defaultdict(list)
if (args.use_file):
	print ("Using a file as reference")
	ref_file = open( args.software, "r")
	line=ref_file.readline()
	while line:
		parts=line.rstrip().split(" ")
		crt_soft=parts[0]
		#print(crt_soft)
		crt_version=parts[1:]
		#print (crt_version)
		ref_soft[crt_soft]=crt_version
		line=ref_file.readline()
	ref_file.close()
else:
	print ("Using input as reference")
	ref_soft[args.software]=args.v

##And now to compare reference and BioConda
if args.output is not None:
	output = open (args.output, "w")
else:
	output = sys.stdout

for crt_ref in ref_soft.keys():
	crt_ref_versions=order_version_list(ref_soft[crt_ref])
	#Let's find the best suitable tool in BioConda
	best_match = difflib.get_close_matches(crt_ref, bioconda_recipes.keys(), n=1, cutoff=0.8)
	if len(best_match)!=0:
		print ("--->"+crt_ref+"<--- was found to be similar to --->"+best_match[0]+"<---")
		is_reference_outdated (crt_ref, crt_ref_versions[-1], best_match[0], bioconda_recipes[best_match[0]], output)


if output is not sys.stdout:
	output.close()


##Cleanup
#The downloaded file needs to be removed
os.remove(in_file)
