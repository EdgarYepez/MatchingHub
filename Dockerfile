##############
## Setup OS ##
##############

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'root:root' | chpasswd

#####################
## Install tooling ##
#####################

# General
RUN apt-get update \
    && apt-get -y dist-upgrade \
    && apt-get install -y --no-install-recommends \
        software-properties-common \
        apt-utils \
        build-essential \
        ca-certificates \
        curl \
        unzip \
        unar \
        git \
        openjdk-8-jdk \
        gnupg \
        vim \
        less

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.10 \
        python3.10-distutils \
        python3.10-venv

# Set Python 3.10 as the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Clean up
RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

###################################
## Setup MatchingHub application ##
###################################

# Create directories and copy source files
RUN mkdir -p /root/.local/bin/matchinghub
WORKDIR /root/.local/bin/matchinghub
COPY src/ .
RUN chmod +x matchinghub.py
RUN ln -s /root/.local/bin/matchinghub/matchinghub.py /usr/local/bin/matchinghub

# Install dependencies
RUN pip install -r requirements.txt
RUN pip install matplotlib
RUN pip install seaborn
RUN rm requirements.txt

# Setup NLTK for Cupid algorithm
RUN pip install nltk==3.9.1
COPY prepare_nltk.py .
RUN python prepare_nltk.py
RUN rm prepare_nltk.py

########################
## Upload data sets ##
########################

# Grab Valentine data sets
WORKDIR /root/.local/bin/matchinghub/schema_matching_scenarios/data_sets/valentine
RUN unzip -q valentine.zip
RUN rm valentine.zip

# Grab Schematch data sets
WORKDIR /root/.local/bin/matchinghub/schema_matching_scenarios/data_sets/schematch
RUN unar schematch.zip
RUN mv schematch/* .
RUN rm -rf schematch schematch.zip

###################################
## Loading final experiment data ##
###################################

WORKDIR /home
COPY experiments/ .
WORKDIR /home/3_experiment_final_data_and_plots
RUN unzip -q qubo_qaoa_matchings.mt.zip
RUN rm qubo_qaoa_matchings.mt.zip

###########
## Entry ##
###########

WORKDIR /home
CMD ["bash"]
