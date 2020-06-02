# about

* fetch bioconda images and tags from git repo and quay.io
* check if already present in internal registry
* if not present, re-tag container and push to internal registry
* add to anchore for security scan

# setup

create virtualenv and install requirements:

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

# Run

On web proxy server run

    sudo ./backup.sh
