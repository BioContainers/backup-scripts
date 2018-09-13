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

RUN git clone --single-branch -b release-2.6 https://github.com/singularityware/singularity.git    
RUN cd singularity && \
	./autogen.sh && \
	./configure --prefix=/usr/local --sysconfdir=/etc && \
	make && \
	make install    

WORKDIR /convertscript
COPY ./convert.sh /convertscript/
COPY ./docker-entrypoint.sh /

RUN mkdir /convertdir
VOLUME /convertdir

ENV PLUGIN_REPO= \
	PLUGIN_TAG= \
	SOFTWARE_NAME=

ENTRYPOINT ["/docker-entrypoint.sh"]
#CMD ["/convertscript/convert"]
