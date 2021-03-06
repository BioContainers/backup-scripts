#!/usr/bin/python3

import logging
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
	for tag in content['tags']:
		res.append(tag['name'])
	return res

#def pull_retag_and_push_images (client, tool_name, tags, output):
def pull_retag_and_push_images (client, tool_name, tags):
	if tags==None:
		logging.info("Nothing to do here")
		return False
	images = list()

	##1) Pulling images
	for crt_tag in tags:
		try:
			img_repo = "quay.io/biocontainers/"+tool_name
			logging.info ("Pulling "+img_repo+":"+crt_tag)
			crt_image = client.images.pull(img_repo, tag = crt_tag)
			images.append(crt_image)
		except docker.errors.APIError:
			logging.warning ("\tCould not pull image "+tool_name+":"+crt_tag)
			continue

		##2) Changing tags
		newRepo = "docker-registry.local:30750/bioconda/"+tool_name
		try:
			if crt_image.tag (repository = newRepo,
				tag = crt_tag):
				logging.info ("\tImage retagged")
			else:
				logging.warning ("\tImage "+tool_name+":"+crt_tag+" NOT retagged")
		except docker.errors.APIError:
			logging.warning("\tError while retagging "+tool_name+":"+crt_tag)

		##3) Pushing images to new registry
		try:
			for line in client.images.push(newRepo, tag=crt_tag, stream=True, decode=True):
				logging.debug (line) ##Only for debug as it floods logs otherwise
			logging.info ("\tImage pushed")
		except docker.errors.APIError:
			logging.warning("\tCould not push image "+new_repo+":"+crt_tag)

	##4) Removing all images, another loop since removing each tag may waste time when different versions share layers
	for crt_image in images:
		try:
			logging.info ("Removing image")
			client.images.remove(crt_image.id, force=True)
		except docker.errors.ImageNotFound:
			logging.error ("Could not remove image hopefully it's already deleted but it may have to be deleted manually otherwise!")
	return True

#def update_tool_tags_list (url, list_of_tags, output):
def update_tool_tags_list (url, list_of_tags):
	if list_of_tags == None:
		return None
	logging.info("\tTags in "+url)

	##Making sure it doesn't exist in a docker registry
	try:
		 r2 = requests.get(url)
	except requests.exceptions.RequestException:
		logging.warning("Error while checking tags availability at "+url)
		return list_of_tags

	if r2.status_code !=200:
		logging.info(None)
		return list_of_tags
	else:
		cont_tags = r2.json()['tags']
		logging.info (cont_tags)
		diff_of_images = list(set(list_of_tags) - set(cont_tags))
		if len(diff_of_images) < 1:
			return None
		else:
			return diff_of_images

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Builds BioConda tools from local copy of repo based on list and pushes the images")
parser.add_argument('-i','--inputlist', help="Path to a file containing the list of tools needing to be built and pushed", required="true")
parser.add_argument('--debug', help="Displays debug level log", action="store_true")
parser.add_argument('-l','--logfile', help="Path to log file")
args = parser.parse_args()

testCtr = 1

if args.debug:
	level = logging.DEBUG
else:
	level = logging.INFO

if args.logfile:
	logging.basicConfig(
		level=level,
		format="%(levelname)s:%(message)s",
		filename=args.logfile
	)
else:
	logging.basicConfig(
		level=level,
		format="%(levelname)s:%(message)s"
		)

with open(args.inputlist, 'r') as listfile:
	tools = listfile.readlines()
	client = docker.from_env()

	for crt_line in tools:
		testCtr += 1
		crt_line = crt_line.rstrip().split("\t")
		crt_tool = crt_line[0]
		crt_version = crt_line[1]
		logging.info ("TREATING TOOL:"+crt_tool+" (number "+str(testCtr)+")")

		##Getting/checking bioconda's image availability
		params = {'onlyActiveTags': 'true', 'limit': '100'}
		url = "https://quay.io/api/v1/repository/biocontainers/"+crt_tool+"/tag"
		r = requests.get(url, params = params)
		if r.status_code != 200:
			continue
		ret = r.json()
		crt_tags = get_tags_from_response(r)
		logging.info(crt_tags)
		images = None

		##Checking that tool isn't already in biocontainers
		url = "https://containers.biocontainers.pro/v2/biocontainers/"+crt_tool+"/tags/list"
		crt_tags = update_tool_tags_list(url, crt_tags)


		##Checking that tool isn't already imported in biocontainers 'bioconda' subrepo
		url2 = "https://containers.biocontainers.pro/v2/bioconda/"+crt_tool+"/tags/list"
		crt_tags = update_tool_tags_list(url2, crt_tags)


		logging.info ("After checking redundancy, here is the list of tags that need to be imported:")
		logging.info (crt_tags)

		pull_retag_and_push_images (client, crt_tool, crt_tags)

		##For testing:
		#if testCtr > 50:
		#	sys.exit()


