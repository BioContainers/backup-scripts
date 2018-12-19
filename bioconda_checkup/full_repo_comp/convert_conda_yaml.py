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
result = client.containers.run("lbesoft/conda-build:latest" ##This image can't download source so rendering fails, need to find another conda image, maybe our own
	, "conda-render -f "+args.output+" /data"
	, volumes={args.input:{'bind': '/data', 'mode': 'rw'}})
print (result)
