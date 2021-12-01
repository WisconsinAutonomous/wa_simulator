FROM continuumio/miniconda3

LABEL maintainer="Wisconsin Autonomous <wisconsinautonomous@studentorg.wisc.edu"

ARG DEBIAN_FRONTEND=noninteractive

# Use mirrors instead of main server
RUN sed -i 's|deb http://.*ubuntu.com.* \(focal.*\)|deb mirror://mirrors.ubuntu.com/mirrors.txt \1|g' /etc/apt/sources.list

# Check for updates
RUN apt update && apt upgrade -y

# Install some packages
RUN apt install -y wget bash

# Add the WA simulator env file
RUN wget https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml -O /root/environment.yml
RUN conda env update --name base -f /root/environment.yml
RUN rm -f /root/environment.yml

WORKDIR /root/

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
