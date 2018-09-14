#!/bin/bash

echo "Bootstrap: docker" > Singularity    
echo "From: $IMAGE_REPO:$IMAGE_TAG" >> Singularity    

cat Singularity    
echo "Convert docker image to singularity image"    
mkdir -p /convertdir/${SOFTWARE_NAME}    
echo "singularity -q build /convertdir/${SOFTWARE_NAME}/${SOFTWARE_NAME}_${IMAGE_TAG}.img Singularity"    
singularity -q build /convertdir/${SOFTWARE_NAME}/${SOFTWARE_NAME}_${IMAGE_TAG}.img Singularity  
#singularity -v build ./TESTING.img Singularity  

