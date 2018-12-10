#!/usr/bin/python3

from dockerfile_parse import DockerfileParser
import argparse
import sys
import os

def check_this_recipe (path, tag, instruction, output):
	with open(path, 'r') as content_file:
		content = content_file.read()
	dfp = DockerfileParser()
	dfp.content = content
	#print (dfp.labels['software.version'])
	#if 'base_image' in dfp.labels.keys() :
	#	base_image = dfp.labels['base_image']
	#	if base_image.endswith(tag):
	#		print (path +"\t--->\t"+base_image, file=output)
	#		return True
	for crt_inst in dfp.structure:
		if not crt_inst['instruction']==instruction:
			continue
		if tag in crt_inst['value']:
			#print (crt_inst['value'])
			print (path +"\t--->\t found "+tag+" in "+instruction, file=output)
			return True
	return False

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Tests whether Dockerfiles in your system use a specific tag")
parser.add_argument('-r','--rootdir', help="Path from which to search recursively", required="true")
parser.add_argument('-t','--tag', help="Tag to look for", default="latest")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
parser.add_argument('-i','--instruction', help="Instruction in which to look for TAG", default="LABEL")
args = parser.parse_args()

if args.output is not None:
        output = open (args.output, "w")
else:
        output = sys.stdout

ctr=0
for root, dirs, files in os.walk (args.rootdir):
	for file in files:
		if file.endswith("Dockerfile"):
			#print (os.path.join(root,file))
			if check_this_recipe(os.path.join(root,file), args.tag, args.instruction, output):
				ctr+=1

if output is not sys.stdout:
        output.close()

print ("Found "+str(ctr)+" recipes fitting the request")


