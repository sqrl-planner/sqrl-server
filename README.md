# sqrl-server
 Backend API server for sqrl - a timetable planner for the University of Toronto, Faculty of Arts & Science.

## Package manager
Sqrl uses the [poetry](https://python-poetry.org/) package manager to manage its dependencies. To install the dependencies, run the following command:
```
poetry install
```
See the [poetry](https://python-poetry.org/) documentation for more information and
installation instructions.

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

 #### Build the Docker image and start the Docker container

You start the Docker container by running
```shell
docker-compose up
```
*NOTE: The first time you run this, it's going to take 5-10 minutes depending on your internet connection and hardware.*

This will build the image, if needed, and once built, automatically spin up a container with the image. If you'd like to force a rebuild of the image, you may additionally pass an optional ``--build`` flag to the above command.

#### Stopping the Docker container

You can stop running the container by running ``docker-compose down``.

#### Setting up the database

Sqrl uses MongoDB, a NoSQL database program. An instance of MongoDB is already setup for you (with a ``sqrl`` database) by the Docker container.

Alterntively, you can run an instance locally or use a number of database providers. If you do so, create an empty database on your MongoDB instance and update the ``.env`` file with your instance information (host, credentials, and db name).

#### Gator
Gator is a service that is responsible for aggregating all needed datasets for the server which is required for sqrl to function. You'll need to install the Gator service and configure it to run on your local machine. See the [Gator documentation](https://github.com/sqrl-planner/gator/blob/main/README.md) for more information

## Tools

There are a number of tools available to help you with the development of sqrl. These tools ensure that your code is well-formed, follows the best practices, and
is consistent with the rest of the project.

#### Linting the codebase
- For detecting code quality and style issues, run ``flake8``
- For checking compliance with Python docstring conventions, run ``pydocstyle``

**NOTE**: these tools will not fix any issues, but they can help you identify potential problems.

#### Formatting the codebase
- For automatically formatting the codebase, run ``autopep8 --in-place --recursive .``. For more information on this command, see the [autopep8](https://pypi.python.org/pypi/autopep8) documentation.
- For automatically sorting imports, run ``isort .``

#### Running tests
For running tests, run ``pytest``.
