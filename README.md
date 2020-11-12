# Portfolling
A simple portfolio site, in which you can create your account, add your projects and images to it. Beside that you can search for other users profiles, and see their projects. It includes and RESTful API.

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

## API documentation:
api/login/:
POST - Login in portfoller account - arguments: username, password

api/logout/:
POST - Logout

api/portfollers/:
GET - List portfollers
POST - Create portfoller - arguments: username, password, first_name, last_name, gender, birthdate, country_of_birth, career, email, profile_picture, biography

api/portfollers/(username)/:
GET - Retrieve portfoller by username
PUT/PATCH - Update portfoller
DELETE - Deletes portfoller

api/portfollers/(username)/projects/:
GET - list portfoller projects
POST - Create a project - arguments: project_name, project_description

api/portfollers/(username)/projects/(project_name)/:
GET - Retrieve portfoller project by project_name
PUT/PATCH - Update project
DELETE - Deletes project

api/portfollers/(username)/projects/(project_name)/images/:
GET - list project images
POST - Add a project image

api/portfollers/(username)/projects/(project_name)/images/(project image id):
GET - Retrieve project image by id
DELETE - Deletes project image

## Extras:

### Using Django admin interface:
All users, or better, portfollers, that you create in the base site or the API are simple users, they don't grant you access to the Django admin interface, so you cannot work with it with these common created users. To do that you need to create a superuser, that user will be allowed to sign in the admin interface and manage all your project data.
Create a superuser is simple, only one command is needed, you can add this command in the docker-entrypoint.sh file:
```
python manage.py createsuperuser --username example --password example --email example@example.com --first_name example --last_name example --birthdate 2000-01-01 --country_of_birth US --noinput
```

You can set all the example data to your preferences, can also change the birthdate and the country_of_birth to another country code.