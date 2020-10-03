# Portfolling
A simple portfolio site, in which you can create your account, add your projects and images to it. Beside that you can search for other users profiles, and see their projects.

##How to install and run:
Pre-requisites:
  Docker/Docker Desktop installed and running.
  
1. Open your command prompt, then create or open the folder where you want to clone the repo:
```
cd path/to/your/dev/folder/
mkdir portfolling
cd portfolling
```
2. Clone this repository, it will download all the necessary files to you run this project in your localhost:
```
git clone https://github.com/Mikael-Caetano/Portfolling/ .
```

3. Navigate to portfoling:
```
cd portfoling
```

4. Run the `docker-compose up` command:
```
docker-compose up
```
If you get an "standard_init_linux.go:211: exec user process caused "no such file or directory" error:
Checkout that the "End of line sequence" setting of the file docker-entrypoint.sh is LF, otherwise change it to LF.

5. Open your browser and go to 127.0.0.1:8000 or localhost, the application should be running.