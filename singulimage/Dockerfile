FROM debian

RUN apt-get update && \
    apt-get install -y \
    python \
    dh-autoreconf \
    build-essential \
    squashfs-tools \
    git \
    libarchive-dev

ENV SINGULARITY_MESSAGELEVEL="-3"
ENV PYTHONIOENCODING="UTF-8"

###Had to use a specific version (ie a release) of Singularity since the master branch doesn't have the autogen, configure etc.
RUN git clone --single-branch -b release-2.6 https://github.com/singularityware/singularity.git
RUN cd singularity && \
	./autogen.sh && \
	./configure --prefix=/usr/local --sysconfdir=/etc && \
	make && \
	make install

###Where the script doing the conversion will be
WORKDIR /convertscript
COPY ./convert.sh /convertscript/

###We need this to change the default umask (tip found in a github issue)
COPY ./docker-entrypoint.sh /

###Where the output can be accessed
RUN mkdir /convertdir
VOLUME /convertdir

###The 3 need environment variables
ENV IMAGE_REPO= \
	IMAGE_TAG= \
	SOFTWARE_NAME=

ENTRYPOINT ["/docker-entrypoint.sh"]
#CMD ["/convertscript/convert"]
