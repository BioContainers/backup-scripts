#!/usr/bin/python3

import argparse
import sys
import os
import requests
import json

#################################################################################
####################Importing BioContainers DockerHub library####################
#################################################################################

def get_repo_list (lib_name):
	url = "https://hub.docker.com/v2/repositories/"+lib_name
	r = requests.get(url = url)
	repos = []
	return recursive_content_extraction(r.json(), repos)

################
#####Shared#####
################

def recursive_content_extraction (res_json, content_list, property='name'):
	for crt_item in res_json['results']:
		content_list.append(crt_item[property])
	if res_json['next'] is not None:
		res = requests.get(url = res_json['next'])
		return recursive_content_extraction(res_json = res.json(), content_list = content_list, property=property)
	return content_list

########################################################################################
##########################Getting tag list for a specific repo##########################
########################################################################################

def get_repo_tag_list (lib_and_repo):
	url = "https://hub.docker.com/v2/repositories/"+lib_and_repo+"/tags"
	res = requests.get(url=url)
	taglist = []
	return recursive_content_extraction (res_json = res.json(), content_list = taglist)

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Tests whether a given set of softwares have more up-to-date recipes in BioConda")
parser.add_argument('-l','--library', help="DockerHub library name for the repo", default="biocontainers")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

###Getting library images list
print("#STEP 1: GETTING ALL REPOS/TOOLS FROM LIBRARY")
lib_repo_list = get_repo_list(args.library)
print (lib_repo_list)

###For each repo, find 'bad' tag: latest
if args.output is not None:
	output = open (args.output, "w")
else:
	output = sys.stdout

badly_tagged_tools_ctr=0

print("#STEP 2: CHECK IF TOOL HAS TAG=LATEST")
for crt_repo in lib_repo_list:
	crt_tags = get_repo_tag_list(args.library+"/"+crt_repo)
	if "latest" in crt_tags:
		print (crt_repo, file=output)
		badly_tagged_tools_ctr+=1

print ("I found "+str(badly_tagged_tools_ctr)+" tools tagged as 'latest'")

if output is not sys.stdout:
	output.close()
