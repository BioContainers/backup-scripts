#!/bin/bash

DATE=`date +%Y%m%d`
PREFIX="${0%/*}"
COMPFILE="${PREFIX}/comparison.txt"
LOGFILE="${PREFIX}/${DATE}_run.log"
OUTFILE="${PREFIX}/${DATE}_run.out"

MISSINGTOOLSSCRIPT="$PREFIX/find_missing_tools_in_biocontainers.py"
PULLNPUSHSCRIPT="$PREFIX/copy_conda_images_to_our_registry.py"

#Step 1: create the list of missing tools
printf "\nSTEP 1: Creating the list\n"
cmd="$MISSINGTOOLSSCRIPT -o $COMPFILE"
retval=eval $cmd
if [[ ! retval ]]; then
        printf "WARNING: Could not create the comparison list\n"
        return 0
fi

#Step 2: treat the list
printf "\nSTEP 2: Pulling and pushing (TODO)\n"
cmd="$PULLNPUSHSCRIPT -i $COMPFILE -l $LOGFILE"
retval=eval $cmd &> $OUTFILE
if [[ ! retval ]]; then
	printf "WARNING: Push'n'pull did not finish\n"
fi

#Step 3: remove the list
printf "\nSTEP 3: Removing the list\n"
cmd="rm -f $COMPFILE"
retval=eval $cmd
if [[ ! retval ]]; then
	printf "WARNING: Could not remove file\n"
	return 0
fi
