#!/usr/bin/python3

from dockerfile_parse import DockerfileParser
import yaml
import argparse
import sys
import os
from collections import defaultdict

###################################################
####################Main method####################
###################################################

parser = argparse.ArgumentParser(description="Builds BioConda tools from local copy of repo based on list and pushes the images")
parser.add_argument('-d','--bioconDa', help="Path to BioConda's local repo copy", required="true")
parser.add_argument('-l','--listoftools', help="Path to a file containing the list of tools needing to be built and pushed", required="true")
parser.add_argument('-o','--output', help="Output file where the results are stored, defaults to stdout")
args = parser.parse_args()

if args.output is not None:
        output = open (args.output, "w")
else:
        output = sys.stdout

with open(args.listoftools, 'r') as listfile:
	tools = listfile.readlines()
	tools = sorted(tools)
	for crt_line in tools:
		crt_line = crt_line.rstrip().split("\t")
		crt_tool = crt_line[0]
		print (crt_tool)

if output is not sys.stdout:
        output.close()

#print ("Found "+str(ctr)+" tools in common")


