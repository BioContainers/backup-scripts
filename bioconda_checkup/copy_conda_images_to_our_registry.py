#!/usr/bin/python3

import argparse
import requests
import os
import sys
import docker
import wget
from bs4 import BeautifulSoup
from collections import defaultdict

##########
###Misc###
##########

def get_tags_from_response (response):
	content = response.json()
	res = list()
	#print (content['tags'])
	for tag in content['tags']:
		res.append(tag['name'])
	return res

def pull_retag_and_push_images (client, tool_name, tags):
	images = list()

	##1) Pulling images
	for crt_tag in tags:
		try:
			img_repo = "quay.io/biocontainers/"+tool_name
			print ("Pulling "+img_repo+":"+crt_tag)
			crt_image = client.images.pull(img_repo, tag = crt_tag)
			images.append(crt_image)
		except docker.errors.APIError:
			print ("\tCould not pull image "+tool_name+":"+crt_tag)
			continue
			#return False

		##2) Changing tags
		try:
			if crt_image.tag (repository = "containers.biocontainers.pro/bioconda/"+tool_name,
				tag = crt_tag):
				print ("\tImage retagged")
			else:
				print ("\tImage NOT retagged")
		except docker.errors.APIError:
			print ("\tCould not retag image "+tool_name+":"+crt_tag)
		print (crt_image.tags) ###<- I've interrupted the script and seen that the new tag was indeed created but this doesn't return it...

		##3) Pushing images to new registry
		#TODO

	##4) Removing all images, another loop since removing each tag may waste time when different versions share layers
	for crt_image in images:
		print ("Removing image")
		client.images.remove(crt_image.id, force=True)
	return True

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
	client = docker.from_env()

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
			#print ("\t"+tag['name'], file=output)
			totalSize += tag['size']
			#print ("Current size: "+str(totalSize))
		crt_tags = get_tags_from_response(r)
		print (crt_tags)
		images = None

		##Making sure it doesn't exist in our docker registry
		url = "https://containers.biocontainers.pro/v2/biocontainers/"+crt_tool+"/tags/list"
		r2 = requests.get(url)
		if r2.status_code !=200:
			print ("\tNot found in biocontainers, copy and push everything", file=output)
			#Means we have to copy all images
			pull_retag_and_push_images (client, crt_tool, crt_tags)
		else:
			print ("\tAlready exists in biocontainers registry:", file=output)
			cont_tags = r2.json()['tags']
			print (cont_tags)
			#print (r2.headers)
			#Means we must only push the images whose tags differ
			diff_of_images = list(set(crt_tags) - set(cont_tags))
			if len(diff_of_images) < 1:
				print ("\tNothing to do here")
			else:
				print ("\tOnly copy and push the difference:")
				print (diff_of_images)
				pull_retag_and_push_images (client, crt_tool, diff_of_images)


		##For testing:
		if testCtr > 5:
			sys.exit()

print ("Total size required to store images: "+str(totalSize), file = output)

if output is not sys.stdout:
        output.close()

#print ("Found "+str(ctr)+" tools in common")


