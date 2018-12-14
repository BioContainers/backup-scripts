#!/usr/bin/python3

from dockerfile_parse import DockerfileParser
import yaml
import argparse
import sys
import os
from collections import defaultdict

def parse_biocontainer_recipe (path):
	with open(path, 'r') as content_file:
		content = content_file.read()
	dfp = DockerfileParser()
	dfp.content = content

	if 'software' not in dfp.labels.keys() or 'software.version' not in dfp.labels.keys():
		print ("Missing required label in Dockerfile ("+path+")")
		#print (dfp.labels.keys())
		return None
	else:
		software = dfp.labels['software']
		version = dfp.labels['software.version']
		return {"soft":software,"ver":version}

def parse_bioconda_recipes (path):
	with open(path, 'r') as content_file:
		meta = yaml.safe_load(content_file)
	print (meta)

def add_tool_to_dict (tool, dict):
	if tool is not None:
		dict[tool["soft"]].append(tool["ver"])
	return dict

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

parser = argparse.ArgumentParser(description="Compares BioConda and BioContainers local git clones to compare available tools")
parser.add_argument('-d','--bioconDa', help="Path to BioConda's local repo copy", required="true")
parser.add_argument('-t','--bioconTainers', help="Path to BioContainer's local repo copy", required="true")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

if args.output is not None:
        output = open (args.output, "w")
else:
        output = sys.stdout

#ctr=0
##We first list all tools from BioConda
for root, dirs, files in os.walk (args.bioconDa):
	for file in files:
		if file.endswith("meta.yaml"):
			print ("Parsing "+os.path.join(root,file))
			parse_bioconda_recipes(os.path.join(root,file))

##Then all tools fomr BioContainers
biocont_tools = defaultdict(list)
for root, dirs, files in os.walk (args.bioconTainers):
	for file in files:
		if file.endswith("Dockerfile"):
			None
			#this_tool=parse_biocontainer_recipe(os.path.join(root,file))
			#biocont_tools = add_tool_to_dict(this_tool, biocont_tools)
#print (biocont_tools)

if output is not sys.stdout:
        output.close()

#print ("Found "+str(ctr)+" tools in common")


