FROM kalilinux/kali-rolling

# Update and install necessary packages
RUN apt update && apt install -y \
    outguess \
    'python3.12' \
    python3-pip \
    python3-setuptools \
    ruby \
    tshark \
    dos2unix

# Install binwalk
RUN pip3 install binwalk
RUN apt install -y mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract squashfs-tools sleuthkit default-jdk lzop srecord

# Install zsteg
RUN gem install zsteg

# Install stegoveritas
RUN pip3 install stegoveritas
RUN stegoveritas_install_deps

# Create a directory to store uploaded files
RUN mkdir /home/data

# Create a directory to store results generated from the scripts
RUN mkdir /home/results

# Installing python libraries
COPY requirements.txt /home
WORKDIR /home
RUN pip3 install -r requirements.txt

# Copy the scripts to the container
COPY . .

# Make the scripts executable
RUN dos2unix /home/modules/*
RUN chmod +x /home/modules/*
RUN dos2unix *.sh

# Set the working directory
WORKDIR /home/
RUN echo 'export PATH=/home/modules:$PATH' > /home/.bashrc
RUN echo "alias cls='clear'" >> /root/.bashrc
RUN echo "alias full_analyze='python3 /home/bin/full_analyze.py'" >> /root/.bashrc
RUN echo "alias image_analyze='python3 /home/bin/image_analyze.py'" >> /root/.bashrc
RUN echo "alias pcap_analyze='python3 /home/bin/pcap_analyze.py'" >> /root/.bashrc
RUN echo "alias magic_byte_analyze='python3 /home/modules/magic_byte_analysis.py'" >> /root/.bashrc

# Exposing the port that the Flask application will be running on
EXPOSE 5001

#  Set the entry point to run the Flask app
CMD ["python3", "app.py"]

ENV SHELL=/bin/bash
