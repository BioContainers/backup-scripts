#!/bin/bash

. ./venv/bin/activate

LAST_SHA=
if [ ! -e bioconda-recipes ]; then
    echo "new clone"
    git clone https://github.com/bioconda/bioconda-recipes.git
    cd bioconda-recipes
else
    cd bioconda-recipes
    LAST_SHA=`git show HEAD | sed -n 1p | cut -d " " -f 2`
    echo "Last sha: $LAST_SHA"
fi

git pull origin master

if [ "a$LAST_SHA" == "a" ]; then
    find . -name "meta.yaml" > /tmp/recipes.txt
else
    NEW_SHA=`git show HEAD | sed -n 1p | cut -d " " -f 2`
    echo "New sha: $NEW_SHA"
    git diff --name-only $LAST_SHA $NEW_SHA | grep "meta.yaml" > /tmp/recipes.txt
fi

while read p; do
    python backup.py $p
done </tmp/recipes.txt

rm /tmp/recipes.txt
