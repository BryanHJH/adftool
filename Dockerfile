FROM kalilinux/kali-rolling

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    binwalk \
    outguess \
    python3 \
    python3-pip \
    ruby \
    tshark \
    zsteg

# Install stegoveritas
RUN pip3 install stegoveritas

# Create a directory for the scripts
RUN mkdir /scripts

# Copy the scripts to the container
COPY outguess_analysis.sh /scripts/
COPY binwalk_analysis.sh /scripts/
COPY pcap_analysis.sh /scripts/
COPY stegoveritas_analysis.sh /scripts/
COPY zsteg_analysis.sh /scripts/

# Make the scripts executable
RUN chmod +x /scripts/*

# Set the working directory
WORKDIR /scripts