#!/bin/bash

echo "Bootstrap: docker" > Singularity    
echo "From: $PLUGIN_REPO:$PLUGIN_TAG" >> Singularity    

cat Singularity    
echo "Convert docker image to singularity image"    
mkdir -p /convertdir/${SOFTWARE_NAME}    
echo "singularity -q build /convertdir/${SOFTWARE_NAME}/${SOFTWARE_NAME}_${PLUGIN_TAG}.img Singularity"    
singularity -q build /convertdir/${SOFTWARE_NAME}/${SOFTWARE_NAME}_${PLUGIN_TAG}.img Singularity  
#singularity -v build ./TESTING.img Singularity  

