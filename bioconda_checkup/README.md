# Requirements

* Docker

* Python3    

* Python packages:   
 * requests
 * docker
 * beautifulsoup4
 * wget
 * packaging

# Steps

There's a bash script (__compare\_and\_copy.sh__) that runs all steps and stores logs and outputs automatically in files named after the date when it is run.

## Part I: creating a list of differences     

Recycling an older script, this first part compares the tools publicly available from BioContainers and BioConda.
BioContainers list is lifted from the github repository tree. The tree contains tool names and versions that can be easily parsed.
BioConda list comes from the BioConda website which has a table containing all tools and their versions. It is parsed using BeautifulSoup.

This script is __find\_missing\_tools\_in\_biocontainers.py__.

## Part II: pull'n'push     

This step is the main one, it actually gets the images and pushes them to our registry (if necessary).
Images are pulled from BioConda's registry (__quay.io/biocontainers/__, yes the address is confusing) if they don't already exist in our own registry:

* tools already in biocontainers can be found using this prefix __containers.biocontainers.pro/v2/biocontainers/__

* tools added by this script use this prefix __containers.biocontainers.pro/v2/bioconda/__

If images using the same repo name (ie: tool name) and tag (ie: version number) are found, the pull and push is skipped.
Otherwise it is treated this way:     

* image is pulled from quay.io     

* image is retagged appropriately to be pushed on our registry     

 * the prefix is __docker-registry.local:30750/bioconda/__     

 * the registry is configured so images can only be pushed locally which is why this address is used and why no login/identification is required    

* image is pushed using this new tag into our registry    

* image is removed    

Command for testing:    
```nohup python3 copy[...].py -i [input].txt -l out.log &```

## Part III: removing temp file(s?)

The list created in the first step is deleted.
