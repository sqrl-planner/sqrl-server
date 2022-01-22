# sqrl-server
 Backend API server for sqrl, a timetable planner for the University of Toronto, Faculty of Arts & Science. 
 
 ## Running the server
 You'll need to have [Docker installed](https://docs.docker.com/get-docker/). 
 
 #### Clone this repo and move into the directory
 ```shell
 git clone https://github.com/sqrl-planner/sqrl-server.git
 cd sqrl-server
 ```
 
 #### Copy starter files
 ```shell
 cp .env.example. .env
 cp docker-compose.example.yml docker-compose.yml
 ```
 The defaults are for running in *development* mode. Go through each variable in the file and make sure it is properly set. You will likely need to update the 
 credentials.
 
 #### Build the Docker image
 
 *The first time you run this, it's going to take 5-10 minutes depending on your internet connection and hardware.*
 ```shell
 docker-compose -f docker-compose.yml up --build
 ```
 Once the image is built, Docker will automatically spin up a container with the image. The server is now running!
 
 #### Starting and stopping the Docker container
 
 You can stop running the container by running ``docker-compose down`` and similarly, you can start it back up with ``docker-compose up``. This should only take a few seconds since we've already built the image!

#### Setting up the database

sqrl-server uses MongoDB, a NoSQL database program. You can run a MongoDB instance locally or use a number of database providers. Create an empty database on your MongoDB instance and update the ``.env`` file with your instance information (host, credentials, and db name).

#### Pulling and syncing course data

To pull and sync from the command-line, you may run
```shell
flask sync
```
Alternatively, you can run the [data sync service](https://github.com/sqrl-planner/sqrl-server/tree/main/services) to periodically aggregate and sync course data. The Docker image already sets up a cron job for syncing data according to a schedule (see the ``DATA_SYNC_SCHEDULE`` environment variable). 

Currently, the dataset sources are hardcoded parameters in the [``config/settings.py``](https://github.com/sqrl-planner/sqrl-server/blob/main/config/settings.py) file. You must modify this file directly to custsomize the data sources

## Tools

#### Linting the codebase
```
flake8
```

#### Formatting the codebase
```
autopep8
```

#### Running tests
````
pytest tests/
````
