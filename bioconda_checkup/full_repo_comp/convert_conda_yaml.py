#!/usr/bin/python3

import docker
import argparse

parser = argparse.ArgumentParser(description="Converts a Conda meta.yaml into a yaml with correct syntax")
parser.add_argument('-i','--input', help="Path to directory where meta is stored", required="true")
parser.add_argument('-o','--output', help="Output yaml file", default="rendered_meta.yaml")
args = parser.parse_args()

client = docker.from_env()

#print (client.images.list())
volume_part = "-v "+args.input+":/data"
result = client.containers.run("bioconda/bioconda-utils-build-env:latest"
	, "conda-render -f /data/"+args.output+" /data"
	, volumes={args.input:{'bind': '/data', 'mode': 'rw'}})
#print (result)
