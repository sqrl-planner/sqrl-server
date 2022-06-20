# sqrl-server
 Backend API server for sqrl - a timetable planner for the University of Toronto, Faculty of Arts & Science.

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
 ```
 The defaults are for running in *development* mode. Go through each variable in the file and make sure it is properly set. You will likely need to update the
 credentials.

 #### Build the Docker image

 *The first time you run this, it's going to take 5-10 minutes depending on your internet connection and hardware.*
 ```shell
 docker-compose up --build
 ```
 Once the image is built, Docker will automatically spin up a container with the image. The server is now running!

 #### Starting and stopping the Docker container

 You can stop running the container by running ``docker-compose down`` and similarly, you can start it back up with ``docker-compose up``. This should only take a few seconds since we've already built the image!

#### Setting up the database

sqrl-server uses MongoDB, a NoSQL database program. An instance of MongoDB is already setup for you (with a ``sqrl`` database) by the Docker container.

Alterntively, you can run an instance locally or use a number of database providers. If you do so, create an empty database on your MongoDB instance and update the ``.env`` file with your instance information (host, credentials, and db name).

#### Pulling and syncing course data

If your database is empty, you'll need course information to use sqrl. To pull the latest data from all dataset sources, run

```shell
flask sync
```
The Docker container will automaticlly sync the data on the first-run. You might find it useful to setup a cron job to periodically run this job in production.

Currently, the dataset sources are hardcoded parameters in the [``config/settings.py``](https://github.com/sqrl-planner/sqrl-server/blob/main/config/settings.py) file. You must modify this file directly to customize the data sources.

## Tools

#### Linting the codebase
For detecting code quality and style issues, run
```
flake8
```
For checking compliance with Python docstring conventions, run
```
pydocstyle
```

**NOTE**: these tools will not fix any issues, but they can help you identify potential problems.

#### Formatting the codebase
For automatically formatting the codebase, run
```
autopep8 --in-place --recursive .
```
For more information on this command, see the [autopep8](https://pypi.python.org/pypi/autopep8) documentation.

For automatically sorting imports, run
```
isort .
```

#### Running tests
````
pytest
````
