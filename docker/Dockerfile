FROM ubuntu:noble

ARG UNAME=username
ARG REPO_PATH=/path/to/repo
ARG UID=1000
ARG GID=1000

RUN apt-get update
RUN apt-get install -y openjdk-17-jdk
RUN apt-get -y install software-properties-common
RUN apt-get -y install build-essential
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.10
RUN apt-get install -y python3.10-tk
RUN apt-get install -y python3.10-venv
RUN apt-get install -y python3.10-dev


# RUN groupadd -g ${GID} ${UNAME}
# RUN useradd -m -u ${UID} -g ${GID} -s /bin/bash ${UNAME} 
# RUN echo "${UNAME}:${UNAME}" | chpasswd
# RUN usermod -aG sudo ${UNAME}

WORKDIR ${REPO_PATH}

# USER ${UNAME}

CMD ["/bin/bash"]