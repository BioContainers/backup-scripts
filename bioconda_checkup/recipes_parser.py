#!/usr/bin/python3

from bs4 import BeautifulSoup
from packaging import version
from collections import defaultdict
import argparse

def versionKey (e):
	return version.parse(e)

def order_version_list (versionList):
	versionList.sort(key=versionKey)
	return versionList

def compare_version_lists (refList, targetList):
	print ("TODO")


parser = argparse.ArgumentParser(description="Looks for higher version number of input tool in allRecipes.html")
parser.add_argument('software', metavar='S', nargs=1)
parser.add_argument('-v', nargs='*')
args = parser.parse_args()

print (args)

html_doc = open ("allRecipes.html","r")

bioconda_recipes = defaultdict(list)

recipes = BeautifulSoup(html_doc, features="html.parser")
for row in recipes.find_all('tr'):
	crtTool=row.get_text(" ").split(" ")
	crtSoft=crtTool[0]
	crtVersion=crtTool[1]
	bioconda_recipes[crtSoft].append(crtVersion)


#testVersion=["1.2.10","1.12.1","2","2.13"]
#sortedVersions=order_version_list(testVersion)
print (vars(args)['v'])
sortedVersions=order_version_list(vars(args)['v'])
print (sortedVersions)
#print (version.parse("1.2.10")<version.parse("1.12.1"))

#print(len(bioconda_recipes.keys()))
