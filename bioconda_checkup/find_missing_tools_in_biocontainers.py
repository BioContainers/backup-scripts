#!/usr/bin/python3

from bs4 import BeautifulSoup
from packaging import version
from collections import defaultdict
from collections import OrderedDict
import difflib
import argparse
import wget
import sys
import os
import requests
import re

##########################################################################
####################Importing BioContainers tools list####################
##########################################################################

def import_comparison_list (url):
	print ("Importing BioContainers tools list from "+url)
	biocont_tools = defaultdict(list)

	r = requests.get(url)
	#print (r.status_code)
	tree=r.json()['tree']
	for crt in tree:
		if (crt['path'].endswith("/Dockerfile")):
			#print (crt['path'])
			parts = crt['path'].split("/")
			tool=parts[0]
			version=parts[1]
			biocont_tools[tool].append(version)
	return biocont_tools

#####################################################################
####################Importing BioConda tools list####################
#####################################################################

def import_reference_list (url):
	print ("Importing BioConda tools list from "+url)
	##Downloading the recipes
	in_file=wget.download (url)
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
	os.remove(in_file)
	return bioconda_recipes

######################
###Sorting versions###
######################

def versionKey (e):
	return version.parse(e)

def order_version_list (versionList):
	versionList.sort(key=versionKey)
	return versionList

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Tests whether a given set of softwares exist in another repo")
parser.add_argument('-r','--reference', default="https://bioconda.github.io/recipes.html", help="The url where the html table to parse can be found")
parser.add_argument('-c','--comparison', default="https://api.github.com/repos/BioContainers/containers/git/trees/b21f5cdff0d9fcc9ff54d23f8be058b9fb5f45b6?recursive=1", help="The url to download the list of paths containing Dockerfiles")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

###Getting BioContainers tools
comparison_tools = import_comparison_list(url=args.comparison)

##Getting BioConda tools
reference_tools = import_reference_list(url=args.reference)

##And now to compare reference and BioConda
if args.output is not None:
	output = open (args.output, "w")
else:
	output = sys.stdout

#toolsList = defaultdict(list)
toolsList = dict()

print ("\nComparing both tools lists")
for crt_reference_tool in reference_tools.keys():
	crt_reference_versions=order_version_list(reference_tools[crt_reference_tool])
	#Let's find the best suitable tool in BioConda
	best_match = difflib.get_close_matches(crt_reference_tool, comparison_tools.keys(), n=1, cutoff=0.8)
	latest_version = order_version_list(reference_tools[crt_reference_tool])[0]
	#print ("Latest version for "+crt_reference_tool+" is "+latest_version)
	if len(best_match)==0:
		toolsList[crt_reference_tool]=latest_version

sortedTools = OrderedDict(sorted(toolsList.items()))
for key in sortedTools:
	versions = sortedTools[key]
	text = "\t--->"+key+"<--- NOT found (example version "+versions+")"
	if args.output is not None:
		text = key+"\t"+versions
	print (text, file=output)


print ("There seems to be "+str(len(sortedTools.keys()))+" tools in the reference missing from the other repo")

if output is not sys.stdout:
	output.close()
