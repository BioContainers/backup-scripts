###BASE IMAGE###
FROM debian:latest


###INSTALLATION###

RUN apt-get update && \
        apt-get -y install curl git unzip man-db && \
	apt-get clean && \
        apt-get purge && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl https://rclone.org/install.sh | bash

RUN adduser rcloneuser
USER rcloneuser

ENV SOURCEPATH= \
	DESTPATH= 

CMD ["rclone sync sourceremote:$SOURCEPATH destremote:$DESTPATH"]
#CMD ["rclone lsd destremote:$DESTPATH"]
