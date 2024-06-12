# ADFTool

This is a Final Year Project for APD3F2311CS(CYB). This tool is mainly developed from my own needs when tackling Digital Forensics CTF challenges. The main aim for this tool is to have all the Digital Forensics-related tools in one 'toolbox'. The tool is aimed to be offline/desktop-based, however, due to certain limitations, it will be running at localhost in a browser instead of a standalone desktop application.

## Tools to include

### Steganalysis tools

- [x] zsteg
- [x] stegoveritas
- [x] outguess
- [x] binwalk

### Network Packet analysis tools

- [x] tshark

### Memory analysis

- [ ] Volatility
- [ ] The Sleuth Kit

## User Interface

This tool will include a Graphical User Interface (GUI), mainly to satisfy my FYP requirement. The GUI is to be built using Python Flask.

### TODO

- [ ] Implement a GUI
- [ ] Store results into a SQLite database instead of a results/ folder

## USAGE

To use ADFTool, you will need to first pull the image from Docker using the command below:<br>
`docker pull docker push bryanhor/adftool:cmd-only`

Currently, ADFTool only includes a CMD interface.

### CMD Usage

Once the docker image has been pulled into your local machine, you can run start the docker container by using the
commands below:<br>

```bash
docker build -t bryanhor/adftool:cmd-only .
docker run -it -v <local_folder>:/home/data -v <local_folder>:/home/results --name <container_name> --rm bryanhor/adftool:cmd-only
```

There are 2 `-v` flags because the first one is to load the folder that has the files that you wish to analyze. This folder is bound to the `/home/data` in the docker container. The second `-v`` flag is to bind the results generated in the docker container to one of your local folders.

The `--name` and `--rm` are optional.<br>

- The `--name` flag will provide a specific name to the new container (however, if this flag is not provided, a name will be randomly generated).
- The `--rm` flag will automatically remove the container when you exit from the docker container.

Once you are inside the docker container, you will be in the `/home/bin` directory. Ther eis only 1 file in that directory, which is `analyze.py`. This python script requires the following input:

1. A file or a directory
2. `-v` for verbosity (optional)

The full command to run the script is `python3 analyze.py <file_or_directory>`

The python script will perform the following tasks:

1. When provided with a file with an extension (e.g. `.bmp`, `.jpg`, `.png`, etc.), it will check the magic bytes of the file and compare with a list of magic bytes found in the `src` folder.
   1. If there are no differences (which means the file is really what its extension implies it is), it will move on to the next task.
   2. If there are differences in the magic bytes, then it will inform you about the difference and request you to change the bytes manually. the python script will not change the magic bytes of a file for you.
2. Assuming the file passes the first check, the python script will then use bash scripts to analyse the provided file depending on the type of file.
   1. If the file is an image file, then it will perform steganalysis.
   2. If the file is a PCAP or PCAPNG file, then it will use tshark to extract information from the network packet capture file.
3. If a directory is provided, it will perform steps 1 and 2 on all the files found in the directory.
4. If a file with no extension is provided, the python script will guess the file type based on its magic bytes and then compare it with the correct magic bytes (based on the sources in the `src` folder) and then inform the user if any changes need to be made to the magic bytes.

The output will be stored in the `/home/results/` directory.

## REMOVAL

To remove the docker container, you can use the following steps:<br>

### Step1

This step is to remove the docker container that was being used. This step is necessary if the `--rm` was not included in the `docker run` command above.

```bash
docker ps -a # To obtain the CONTAINER ID, 
docker rm <CONTAINER ID>
```

### Step 2

This step is to remove the docker image from your system.

```bash
docker images # To obtain the IMAGE ID
docker rmi <IMAGE ID>
```
## IMAGES

![Docker Images](README_pictures/docker_images.png)

![Docker Containers](README_pictures/docker_container_1.png)

![Docker Build](README_pictures/docker_build.png)

![Docker Analyze Directory](README_pictures/docker_analyze_directory.png)

![Docker Results](README_pictures/docker_results.png)