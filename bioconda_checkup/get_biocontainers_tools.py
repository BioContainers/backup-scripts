#!/usr/bin/python3

import requests
import re
from collections import defaultdict
import argparse


###################
###Extra methods###
###################

#There are a couple of things to remove from the version number so it can be compared with what's stored in BioConda
#Examples : XXX1-1-deb XXXlgpl-5-deb XXX9-9-deb-py2 XXXdfsg-1-deb
def clean_version_number (original_version):
	#myRegex = "(dfsg|lgpl).*$"
	myRegex = "((ds[\d]*|dfsg[\d]*|lgpl)?(-[^-]+)*-deb.*$)|(-SNAPSHOT$)"
	#Testing regex:
	#matchRes = re.search(myRegex, original_version)
	#if matchRes is not None:
	#	print (matchRes.group())
	original_version = re.sub(myRegex, '', original_version)

	return original_version

########
##Main##
########

parser = argparse.ArgumentParser(description="Creates a text file containing all tools and versions from BioContainers")
parser.add_argument('-o', '--output', default='bioconttools.txt', help="Output file name (default is bioconttools.txt)")

args=parser.parse_args()

biocont_tools = defaultdict(list)

r = requests.get('https://api.github.com/repos/BioContainers/containers/git/trees/b21f5cdff0d9fcc9ff54d23f8be058b9fb5f45b6?recursive=1')
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

#And now to save the output
output = open(args.output, "w")
for crt_tool in biocont_tools.keys():
	print (crt_tool+" "+" ".join(biocont_tools[crt_tool]), file=output)
output.close()
