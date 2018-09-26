#!/bin/bash

PROG_NAME=$(basename $0)

####################
# Global variables #
####################

DEBUG=0
REPO="BioContainers/containers"
GITHUB_STATUS_TOKEN=$GITHUB_AUTH_TOKEN
COMMIT=$GIT_COMMIT
SOFTWARE=$CONTAINER
HDR1="Accept: application/vnd.github.v3+json"
HDR2="Authorization: token $GITHUB_STATUS_TOKEN"

CONTEXT="misc" #default value

##############
# Print help #
##############

function print_help {
	echo "Usage: $PROG_NAME [options] container_image"
	echo
	echo "   -g, --debug                Debug mode."
	echo "   -h, --help                 Print this help message."
	echo "   -c, --context		    Status' context."
	echo "   -s, --status		    Status value."
	echo "   -m, --message		    Status description message."
}

#######
# Msg #
#######

function msg {

	local tag=$1
	shift
	local code_level=1
	is_numeric=$(echo $1 | grep '^[0-9]*$')
	if [ -n "$is_numeric" ] ; then
		code_level=$1
		shift
	fi
	local msg=$1

	# Check tag
	if [ -z "$tag" -o \( "$tag" != INFO -a "$tag" != DEBUG -a "$tag" != ERROR \) ] ; then
		echo "ERROR: Unvalid message tag \"$tag\"." >&2
		exit 999
	fi

	# Print message
	[ "$tag" = DEBUG -a "$DEBUG" -lt "$code_level" ] || echo "$tag: $msg" >&2

	# Exit
	[ $tag = ERROR ] && exit $code_level
}


#############
# Read args #
#############

function read_args {

	local args="$*" # save arguments for debugging purpose

	# Read options
	while true ; do
		shift_count=1
		case $1 in
			-g|--debug) DEBUG=$((DEBUG + 1)) ;;
			-h|--help)              print_help ; exit 0 ;;
			-c|--context)		shift; CONTEXT=$1 ;;
			-s|--status)		shift; STATUS=$1 ;;
			-m|--message)		shift; MESSAGE=$1 ;;
			-|--|--*)               msg ERROR "Illegal option $1." ;;
			-?)                     msg ERROR "Unknown option $1." ;;
			-[^-]*) split_opt=$(echo $1 | sed 's/^-//' | sed 's/\([a-zA-Z]\)/ -\1/g') ; set -- $1$split_opt "${@:2}" ;;
			*) break
		esac
		shift $shift_count
	done
	shift $((OPTIND - 1))

	# Debug
	msg DEBUG 1 "Arguments are : $args"
}

########
# MAIN #
########

# Read arguments
read_args "$@"

# Sending the status
# send status $CONTAINER_IMAGE $STATUS $MESSAGE $CONTEXT
json="{\"description\": \"$MESSAGE\",\"state\": \"$STATUS\",\"context\": \"biocontainers/status/$CONTEXT/$SOFTWARE\"}"
githuburl="https://api.github.com/repos/$REPO/statuses/$COMMIT"
case "$STATUS" in
	"s" | "success")
                status="success"
                ;;
        "f" | "failure")
                status="failure"
                ;;
        "n" | "none")
                status="pending";;
        *)
        	msg ERROR "Unknown conversion status: $STATUS"
                return 1;;
esac
#echo "Curl command:"
#echo "curl -H '$HDR1' -H '$HDR2' -d '$json' $githuburl"
curl -H "$HDR1" \
        -H "$HDR2" \
        -d "$json" \
        "$githuburl"

