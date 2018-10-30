# Mount s3 in file system

Install, configure and use goofys:

sudo goofys -o allow_other  --file-mode=0666 --endpoint https://s3.embassy.ebi.ac.uk  BioContainers2   /mnt/goofys-s3
