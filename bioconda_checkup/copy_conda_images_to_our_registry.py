#!/usr/bin/python3

import argparse
import requests
import os
import sys
import docker
import wget
from bs4 import BeautifulSoup
from collections import defaultdict

########################################
###Download docker image from quay.io###
########################################

def download_image_from_quayio (tool_name):
	print ("Importing page image image from quay.io")
	url = "https://quay.io/repository/biocontainers/"+tool_name+"?tab=tags"
	print (url)
	in_file=wget.download (url)
	html_doc = open (in_file, "r")

	parsed_page = BeautifulSoup(html_doc, features="html.parser")
	print (parsed_page.prettify())
	print ("\nLooking for versions")
	lookfor = {
		'span': '',
		'bo-text': 'tag.name'
	}
	for row in parsed_page.find_all(**lookfor):
	#for row in parsed_page.find_all('bo-text'='tag.name'):
		print (row)

	html_doc.close()
	os.remove(in_file)

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Builds BioConda tools from local copy of repo based on list and pushes the images")
parser.add_argument('-l','--listoftools', help="Path to a file containing the list of tools needing to be built and pushed", required="true")
parser.add_argument('-o','--output', help="Where the logs are printed, defaults to stdout")
args = parser.parse_args()

if args.output is not None:
        output = open (args.output, "w")
else:
        output = sys.stdout

totalSize = 0
testCtr = 0

with open(args.listoftools, 'r') as listfile:
	tools = listfile.readlines()
	#tools = sorted(tools)
	for crt_line in tools:
		testCtr += 1
		crt_line = crt_line.rstrip().split("\t")
		crt_tool = crt_line[0]
		crt_version = crt_line[1]
		print (crt_tool, file = output)

		##Getting/checking bioconda's image availability
		params = {'onlyActiveTags': 'true', 'limit': '100'}
		url = "https://quay.io/api/v1/repository/biocontainers/"+crt_tool+"/tag"
		r = requests.get(url, params = params)
		if r.status_code != 200:
			continue
		ret = r.json()
		for tag in ret['tags']:
			print ("\t"+tag['name'], file=output)
			totalSize += tag['size']
			#print ("Current size: "+str(totalSize))

		##Making sure it doesn't exist in our docker registry
		url = "https://containers.biocontainers.pro/v2/biocontainers/"+crt_tool+"/tags/list"
		r2 = requests.get(url)
		if r2.status_code !=200:
			print ("Not found in biocontainers", file=output)
		else:
			print ("Already exists in biocontainers registry", file=output)
			print (r2.text)
		#print (r2.headers)

		##For testing:
		if testCtr > 100:
			sys.exit()

print ("Total size required to store images: "+str(totalSize), file = output)

if output is not sys.stdout:
        output.close()

#print ("Found "+str(ctr)+" tools in common")


