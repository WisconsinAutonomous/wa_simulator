FROM ubuntu:20.04

LABEL maintainer="Wisconsin Autonomous <wisconsinautonomous@studentorg.wisc.edu"

# Use mirrors instead of main server
RUN sed -i 's|deb http://.*ubuntu.com.* \(focal.*\)|deb mirror://mirrors.ubuntu.com/mirrors.txt \1|g' /etc/apt/sources.list

# Check for updates
RUN apt update && apt upgrade -y

# Install some packages
RUN apt install -y tmux vim ssh git git-lfs zsh python3-pip gxmessage wget

# Various arguments and user settings
ARG USERSHELL
ARG USERSHELLPATH="/bin/${USERSHELL}"
ARG USERSHELLPROFILE="/root/.${USERSHELL}rc"

# Install miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b
ENV PATH=/root/miniconda3/bin:${PATH}
RUN rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda init

# Add the WA simulator env file
COPY environment.yml /tmp/environment.yml
RUN conda env create --name wa -f /tmp/environment.yml
RUN rm -f /tmp/environment.yml

# Run the customize script so people can customize their shell, if they desire
COPY docker/files/* /tmp/
RUN [ -f /tmp/customize.sh ] && $USERSHELL /tmp/customize.sh || $USERSHELL /tmp/customize.sh.template

WORKDIR /root/

ENV USERSHELLPATH=$USERSHELLPATH
CMD $USERSHELLPATH
