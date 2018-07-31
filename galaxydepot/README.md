# What it does
This container runs the *rclone sync* command to synchronise the content of two remote repositories.
To do this the user must setup the remotes at runtime. How to do this is explained below. 

# Setup credentials

Credentials and remote configuration must be set at runtime as environment variables. They can be input either in the command line or in a separate config file.

## Command-line

You can set the different environment variables in the command line using the `-e` flag as seen [here](https://docs.docker.com/engine/reference/run/#env-environment-variables).
Depending on the remote type though this might require an extremely long command line.

## Config file

You can also choose to define all (or some) of your environment variables in a config file as seen [here](https://docs.docker.com/compose/env-file/).
The syntax is simple enough, each line contains a single environment variable defined as:
VAR=VAL
To use your .env file simply add it to the command line this way:
```docker run --env-file config.env ...```

## Required information

The required environment variables for each remote depend on the remote type you want *rclone* to connect to.
The different remote types available in *rclone* can be found [here](https://rclone.org/overview/).

### Remote configuration

Once you know which variables must be set to properly configure your remote, use the naming convention defined [here](https://rclone.org/docs/#environment-variables) to set them up.
To make sure the command works as expected, the remotes are expected to be named **sourceremote** and **destremote**.

#### Source 

Required environment variables for the **source** remote should be set this way:
RCLONE_CONFIG_SOURCEREMOTE_VAR=val

#### Destination

Required environment variables for the **destination** remote should be set this way:
RCLONE_CONFIG_DESTREMOTE_VAR=val

### Path to data

If you only want to synchronize some part of your remotes, you must use the variables **SOURCEPATH** and **DESTPATH**.
Bucket names must be set in these variables.

# Example

## Config file

##Remote http Repository (Source)##   
RCLONE_CONFIG_SOURCEREMOTE_TYPE=http    
RCLONE_CONFIG_SOURCEREMOTE_URL=https://my_repo.my_project.org/   
SOURCEPATH=   

##Remote S3 Bucket (Destination)##   
RCLONE_CONFIG_DESTREMOTE_TYPE=s3   
RCLONE_CONFIG_DESTREMOTE_PROVIDER=Other   
RCLONE_CONFIG_DESTREMOTE_ACCESS_KEY_ID=XXX   
RCLONE_CONFIG_DESTREMOTE_SECRET_ACCESS_KEY=XXX   
RCLONE_CONFIG_DESTREMOTE_REGION=sa-east-1   
RCLONE_CONFIG_DESTREMOTE_ENDPOINT=s3.my-provider.org   
RCLONE_CONFIG_DESTREMOTE_ACL=private   
DESTPATH=MyBucket   

# Reference   
* **rclone**: <https://rclone.org/>   
