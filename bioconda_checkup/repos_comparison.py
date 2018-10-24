#!/usr/bin/python3

from bs4 import BeautifulSoup
from packaging import version
from collections import defaultdict
import difflib
import argparse
import wget
import sys
import os
import requests
import re

##################################################################################################
####################Importing (probably) out-of-date tools list (BioContainers####################
##################################################################################################

#There are a couple of things to remove from the version number so it can be compared with what's stored$
#Examples : XXX1-1-deb XXXlgpl-5-deb XXX9-9-deb-py2 XXXdfsg-1-deb
def clean_version_number (original_version):
        #myRegex = "(dfsg|lgpl).*$"
        myRegex = "((ds[\d]*|dfsg[\d]*|lgpl)?(-[^-]+)*-deb.*$)|(-SNAPSHOT$)"
        #Testing regex:
        #matchRes = re.search(myRegex, original_version)
        #if matchRes is not None:
        #       print (matchRes.group())
        original_version = re.sub(myRegex, '', original_version)

        return original_version

def import_out_of_date_list (url):
	print ("Importing (supposedly) outdated tools from "+url)
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
			##Cleaning version number of superfluous parts (ie: -deb*, dfsg*, lgpl*)
			version=clean_version_number(version)
			#print (version)
			biocont_tools[tool].append(version)
	return biocont_tools

########################################################################################
####################Importing (theoretically) newer tools (BioConda)####################
########################################################################################

def import_newer_list (url):
	print ("Importing (theoretically) newer tools from "+url)
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

##############################################################
####################Comparing the two sets####################
##############################################################

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
		#print(softwareName+"'s top version "+refVersion+" is outdated by "+targetName+"'s versions:", file=output)
		#print(targetList[idx:], file=output)
		print(softwareName+" ("+refVersion+") BEHIND "+targetName+" versions: "+" ".join(targetList[idx:]), file=output)
	#else:
		#print(softwareName+" is up-to-date compared to "+targetName, file=output)

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Tests whether a given set of softwares have more up-to-date recipes in BioConda")
parser.add_argument('-u','--uptodate', default="https://bioconda.github.io/recipes.html", help="The url where the html table to parse can be found")
parser.add_argument('-t','--outdated', default="https://api.github.com/repos/BioContainers/containers/git/trees/b21f5cdff0d9fcc9ff54d23f8be058b9fb5f45b6?recursive=1", help="The url to download the list of paths containing Dockerfiles")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

###Getting BioContainers tools
biocont_tools = import_out_of_date_list(url=args.outdated)

##Getting BioConda tools
bioconda_tools = import_newer_list(url=args.uptodate)

##And now to compare reference and BioConda
if args.output is not None:
	output = open (args.output, "w")
else:
	output = sys.stdout

for crt_biocont_tool in biocont_tools.keys():
	crt_biocont_versions=order_version_list(biocont_tools[crt_biocont_tool])
	#Let's find the best suitable tool in BioConda
	best_match = difflib.get_close_matches(crt_biocont_tool, bioconda_tools.keys(), n=1, cutoff=0.8)
	if len(best_match)!=0:
		print ("\t--->"+crt_biocont_tool+"<--- was found to be similar to --->"+best_match[0]+"<---")
		is_reference_outdated (crt_biocont_tool, crt_biocont_versions[-1], best_match[0], bioconda_tools[best_match[0]], output)


if output is not sys.stdout:
	output.close()
