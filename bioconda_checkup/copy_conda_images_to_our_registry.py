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
	if tags==None:
		print ("Nothing to do here")
		return False
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
		newRepo = "docker-registry.local:30750/bioconda/"+tool_name
		try:
			if crt_image.tag (repository = newRepo,
				tag = crt_tag):
				print ("\tImage retagged")
			else:
				print ("\tImage NOT retagged")
		except docker.errors.APIError:
			print ("\tCould not retag image "+tool_name+":"+crt_tag)
		print (crt_image.tags) ###<- I've interrupted the script and seen that the new tag was indeed created but this doesn't return it...

		##3) Pushing images to new registry
		try:
			for line in client.images.push(newRepo, tag=crt_tag, stream=True, decode=True):
				print (line)
		except docker.errors.APIError:
			print ("\tCould not push image "+new_repo+":"+crt_tag)

	##4) Removing all images, another loop since removing each tag may waste time when different versions share layers
	for crt_image in images:
		print ("Removing image")
		client.images.remove(crt_image.id, force=True)
	return True

def update_tool_tags_list (url, list_of_tags):
	if list_of_tags == None:
		return None
	print ("\tTags in "+url)

	##Making sure it doesn't exist in a docker registry
	try:
		 r2 = requests.get(url)
	except requests.exceptions.RequestException:
		print ("Error while checking tags availability")
		return list_of_tags

	if r2.status_code !=200:
		print (None)
		return list_of_tags
	else:
		cont_tags = r2.json()['tags']
		print (cont_tags)
		diff_of_images = list(set(list_of_tags) - set(cont_tags))
		if len(diff_of_images) < 1:
			return None
		else:
			return diff_of_images

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
		print ("TREATING TOOL:"+crt_tool, file = output)

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

		##Checking that tool isn't already in biocontainers
		url = "https://containers.biocontainers.pro/v2/biocontainers/"+crt_tool+"/tags/list"
		crt_tags = update_tool_tags_list(url, crt_tags)

		##Checking that tool isn't already imported in biocontainers 'bioconda' subrepo
		url2 = "https://containers.biocontainers.pro/v2/bioconda/"+crt_tool+"/tags/list"
		crt_tags = update_tool_tags_list(url2, crt_tags)

		print ("After checking redundancy, here is the list of tags that need to be imported:")
		print (crt_tags)

		pull_retag_and_push_images (client, crt_tool, crt_tags)
		##For testing:
		if testCtr > 5:
			sys.exit()

print ("Total size required to store images: "+str(totalSize), file = output)

if output is not sys.stdout:
        output.close()

#print ("Found "+str(ctr)+" tools in common")


