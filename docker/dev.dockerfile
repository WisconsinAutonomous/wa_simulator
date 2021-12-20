FROM continuumio/miniconda3

LABEL maintainer="Wisconsin Autonomous <wisconsinautonomous@studentorg.wisc.edu"

ARG DEBIAN_FRONTEND=noninteractive

# Use mirrors instead of main server
RUN sed -i 's|deb http://.*ubuntu.com.* \(focal.*\)|deb mirror://mirrors.ubuntu.com/mirrors.txt \1|g' /etc/apt/sources.list

# Check for updates
RUN apt update && apt upgrade -y

# Install some packages
RUN apt install -y wget bash iputils-ping

# Add the WA simulator env file
COPY . /tmp/wa_simulator
RUN cd /tmp/wa_simulator && python setup.py develop 

# Add env variable
ENV DOCKER_ENV 1

WORKDIR /root/

COPY docker/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
