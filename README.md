# SIIT
a project to help you find routes between you interest points

## What is?
We have developed a tool to facilitate the discovery of the Douro region in Portugal. The average user will have access to touristic routes and interesting points to visit, with information about them. The project that we provide is cleaned from our database, you can only see the structure.

## What can it do?
You can adapt our project to the area or purpose that you want. It has the possibility to highlight points of interest and to draw paths between them, also can calculate distances in time and kilometers between the same points. We utilize our self-made API to enable you to integrate specific queries, like distance between points or the best route.

## How we did it?
We based our work in a Ubuntu server, with Apache and Gunicorn. With these servers we were able to create a virtual environment which runs our Python/Flask, HTML and Javascript files. If you want to facilitate de servers process, you would install Anaconda and run everything using its environment, we use it to install the Redis server. We use the OSRM map of Portugal, you must install OSRM with your area of interest.

## Getting started
### Requirements
- Python 3.6.1
- OSRM
- Requiremnts.txt :arrow_right: ```pip install -r requirements.txt```

### Server Configurations
Before you can start, you need to configure the servers for your project. Basically, you just need to define the paths of the files. 
Celery Server:
```
sudo nano /etc/systemd/system/celery.service
```
File contents:
```
[Unit]
Description=Celery Service
After=network.target
[Service]
User=your_user
Restart=on-failure
WorkingDirectory=/…your_path…/SIIT_Install/
ExecStart=/…your_path…/bin/celery worker -A app_core.celery
[Install]
WantedBy=multi-user.target
```
Redis Server:
```
sudo nano /etc/systemd/system/redis.service
```
File Contents:
```
[Unit]
Description=Redis In-Memory Data Store
After=network.target
[Service]
User=your_user
ExecStart=/…your_path…/anaconda3/bin/redis-server /…your_path…/SIIT_Install/redis/redis.conf
[Install]
WantedBy=multi-user.target
```
After services are done, you need to do this for both:
```
sudo systemctl daemon-reload
sudo systemctl enable [service name]
sudo systemctl start [service name]
```

Finally, you need to change the file **app_core.py** with your file paths and configurations.

### Starting a project
After you have installed and configured all servers and osrm maps, you have to initialize de database, creates all tables, and a super user (user: admin password: admin)
```
python initdb.py
```
When the database is created, just initialize the project
```
python run.py
```

## Directory Structure
```
|-- db			<= database files
|-- logs			<= logs files
|-- python_osrm	<= folder with python_osrm library files
|-- redis		<= redis server configuration files
|-- static		<= static files, css, fonts, javascript files
|-- shapefiles	<= place to store your region’s borders shapefile
|-- uploads	<= images upload folder
|-- templates		<= html template files
|-- admin	<= html template files for admin area
|-- app_admin.py	<= python module where the admin views are defined
|-- app_admin_function.py <= python module where the admin functions are defined
|-- app_api.py		<= python module where the API functions and views are defined
|-- app_core.py		<= core file with all the configuration variables
|-- gunicorn.conf	<= gunicorn config file
|-- ILS_testes_m_final_py3.cpython-36m-x86_64-linux-gnu.so <= Cython module of the ILS Heuristic algorythm
|-- initdb.py		<= database creation file
|-- manage.py		<= initializing the function manage migrate
|-- models.py		<= database models
|-- my_function_osrm.py	<= functions that use osrm
|-- My_functions.py 		<= general functions
|-- requirements.txt	<= installation libraries
|-- run.py		<= project running file
|-- settings.py 		<= settings like database path
|-- SIIT_API.py		<= library to facilitate the use of the API by building URI
|-- views.py 		<= manages the application’s views
```

## Project Basic Functions
Initially our project will allow you to create points of interest and routes between them. The frontend, in addition to describing and presenting the project, you can see the points of interest (POIS), your position on your map, also shows the routes created between POIS.
The backend works simply, you can create edit and delete almost everything in the database. You can manage: users, logs, images, categories, counties, points of interest and routes. A table is automatically created with the times of the points of interest and the duration of the visit. It also creates a table with the distances between the points and the times foreseen to travel between them.

## Notice
The project is too big and detailed to describe in a few lines. Most of the code is commented and it can help you to understand all the specificities.

## Links to references
- Flask :arrow_right: http://flask.pocoo.org/
- Redis :arrow_right: https://redis.io/
- Anaconda :arrow_right: https://anaconda.org/
- OSRM :arrow_right: http://project-osrm.org/
