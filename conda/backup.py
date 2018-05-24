from jinja2 import Environment, FileSystemLoader
from jinja2 import Template
import yaml
import requests
import json
import logging
import docker
import sys

if len(sys.argv) != 2:
    logging.error('must specify yaml file as input')
    sys.exit(1)

docker_client = docker.from_env()

logging.basicConfig(level=logging.INFO)

#Load Jinja2 template
env = Environment(loader = FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)

template = env.get_template(sys.argv[1])
res = template.render()
data= yaml.load(res)
#Render the template with data and print the output

'''
dhtags = []
try:
    dockerhub = requests.get('https://hub.docker.com/v2/repositories/biocontainers/' + data['package']['name']  + '/tags/')
    dhres = dockerhub.json()
    for dhtag in dhres['results']:
        dhtags.append(dhtag['name'])
except Exception as e:
    logging.info("Failed to get tag for " + data['package']['name'])

if dhtags:
    logging.warn("Container %s already exists in dockerhub, skipping...." %(data['package']['name']))
else:
    logging.info(data['package']['name'] + ' not found in dockerhub, uploading')
'''

regtags = []
try:
    reg = requests.get('http://localhost:30750/v2/biocontainers/' + data['package']['name'] + '/tags/list')
    if reg.status_code == 200:
      regjson = reg.json()
      regtags = regjson['tags']

    logging.info(data['package']['name'] + 'tags: ' + str(regtags))
      
except Exception:
    logging.exception('failed to get tags for container')

r = requests.get('https://quay.io/api/v1/repository/biocontainers/' + data['package']['name'])
if r.status_code != 200:
    logging.info("Can't access container %s" % (data['package']['name']))
    sys.exit(0)

rdata = r.json()
tags = rdata['tags']

cli = docker.APIClient(base_url='unix://var/run/docker.sock')
for key, tag in tags.iteritems():
    logging.info('bioconda container: ' + data['package']['name'] + ',tag: ' + tag['name'])

    if tag['name'] in regtags:
        logging.info('tag already present, skipping')
        continue

    pull_ok = False
    try:
        logging.info('pull quay.io/biocontainers/' + data['package']['name'] + ':' + tag['name'])
        docker_client.images.pull('quay.io/biocontainers/' + data['package']['name'], tag=tag['name'])
        logging.info('tag image to docker-registry.local:30750') 
        cli.tag('quay.io/biocontainers/' + data['package']['name'] + ':' + tag['name'], 'docker-registry.local:30750/biocontainers/' + data['package']['name'], tag=tag['name'])
        pull_ok = True
    except Exception as e:
        logging.error('Failed to pull/tag container %s:%s, %s' % (data['package']['name'], tag['name'], str(e)))
    try:
        if pull_ok:
            logging.info('push image docker-registry.local:30750/biocontainers/' + data['package']['name'] + ':' + tag['name'])        
            for line in docker_client.images.push('docker-registry.local:30750/biocontainers/' + data['package']['name'], tag=tag['name'], stream=True):
                logging.debug(str(line))
            logging.info('push ok')
    except Exception as e:
        logging.error('Failed to push container %s:%s, %s' % (data['package']['name'], tag['name'], str(e)))
    try: 
        logging.debug('cleanup of images') 
        docker_client.images.remove('quay.io/biocontainers/' + data['package']['name'] + ':' + tag['name'])
        docker_client.images.remove('docker-registry.local:30750/biocontainers/' + data['package']['name'] + ':' + tag['name'])
    except Exception:
        logging.warn('failed to delete images for %s:%s' % (data['package']['name'], tag['name']))

