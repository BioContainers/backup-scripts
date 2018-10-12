#!/usr/bin/python3

from bs4 import BeautifulSoup
from packaging import version
from collections import defaultdict
import argparse

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

def is_reference_outdated (refVersion, targetList) :
	#print ("Comparing "+refVersion+" and "+ " ".join(targetList))
	idx=0
	while idx < len(targetList):
		if version.parse(refVersion) < version.parse(targetList[idx]) :
			break
		idx += 1
	if idx != len(targetList) :
		print("Tool's version is behind")
		print(targetList[idx:])

#################
###Main method###
#################

parser = argparse.ArgumentParser(description="Looks for higher version number of input tool in allRecipes.html")
parser.add_argument('software')
parser.add_argument('-v', nargs='*')
parser.add_argument('-f', action="store_true")
args = parser.parse_args()

html_doc = open ("allRecipes.html","r")

bioconda_recipes = defaultdict(list)

##Getting all BioConda's recipes

recipes = BeautifulSoup(html_doc, features="html.parser")
for row in recipes.find_all('tr'):
	crtTool=row.get_text(" ").split(" ")
	crtSoft=crtTool[0]
	crtVersion=crtTool[1]
	bioconda_recipes[crtSoft].append(crtVersion)

##Getting software names to compare

ref_soft = defaultdict(list)
if (args.f):
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
else:
	print ("Using input as reference")
	ref_soft[args.software]=args.v

#print (bioconda_recipes)
#print (ref_soft)

##And now to compare reference and BioConda
for crt_ref in ref_soft.keys():
	crt_ref_versions=order_version_list(ref_soft[crt_ref])
	crt_biocond=bioconda_recipes[crt_ref]
	print ("Testing "+crt_ref)
	if len(crt_biocond)!=0 :
		is_reference_outdated (crt_ref_versions[-1], bioconda_recipes[crt_ref])



#testVersion=["1.2.10","1.12.1","2","2.13"]
#sortedVersions=order_version_list(testVersion)
#print (vars(args)['v'])
#sortedVersions=order_version_list(vars(args)['v'])
#print (sortedVersions)
#print (version.parse("1.2.10")<version.parse("1.12.1"))

#print(len(bioconda_recipes.keys()))
