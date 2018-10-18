#!/usr/bin/python3

import requests
from pprint import pprint

r = requests.get('https://api.github.com/repos/BioContainers/containers/git/trees/b21f5cdff0d9fcc9ff54d23f8be058b9fb5f45b6?recursive=1')
#print (r.status_code)
tree=r.json()['tree']

for crt in tree:
	if (crt['path'].endswith("/Dockerfile")):
		print (crt['path'])
