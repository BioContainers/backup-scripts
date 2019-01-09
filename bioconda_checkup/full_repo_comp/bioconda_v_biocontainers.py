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
	print ("Treating "+path)
	###We can't load raw meta files that easily since 
	###conda's yaml files use a non-standard variables syntax 
	###Therefore we must 'render' those yaml files before they can be parsed

	##Step #1: rendering meta.yaml into a standard yaml file
	pathDir = os.path.dirname(path)
	newName = "cleanMeta.yaml"
	cleanMeta = os.path.join(pathDir, newName)
	os.system("./convert_conda_yaml.py -i "+pathDir+" -o "+newName)

	##Step #2: parsing the yaml file for content
	with open(cleanMeta, 'r') as content_file:
		clean_meta = yaml.safe_load(content_file)
	#print (clean_meta)
	if 'package' not in clean_meta.keys():
		print ("Missing package info in conda recipe ("+path+")")
		return None
	elif 'name' not in clean_meta['package'].keys() or 'version' not in clean_meta['package'].keys():
		print ("Missing package name or version in conda recipe ("+path+")")
		return None
	else:
		software = clean_meta['package']['name']
		version = clean_meta['package']['version']
		return {"soft":software,"ver":version}

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
bioconda_tools = defaultdict(list)
for root, dirs, files in os.walk (args.bioconDa):
	for file in files:
		if file.endswith("meta.yaml"):
			this_tool=parse_bioconda_recipes(os.path.join(root,file))
			bioconda_tools = add_tool_to_dict(this_tool, bioconda_tools)
print (bioconda_tools)

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


