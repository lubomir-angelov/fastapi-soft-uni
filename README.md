# fastapi-soft-uni

# Setup

Create a new project and install FastAPI along with Uvicorn, an ASGI server used to serve up FastAPI:

```bash
$ mkdir project && cd project
$ mkdir app
$ python3.10 -m venv fast-api-soft-uni
$ source fast-api-soft-uni/bin/activate

(fast-api-soft-uni)$ pip install fastapi==0.85.1
(fast-api-soft-uni)$ pip install uvicorn==0.19.0
```

Add an __init__.py file to the "app" directory along with a main.py file. Within main.py, create a new instance of FastAPI and set up a synchronous sanity check route:

```python
# project/app/main.py


from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
def pong():
    return {"ping": "pong!"}
```

That's all you need to get a basic route up and running!

You should now have:

```bash
└── project
    └── app
        ├── __init__.py
        └── main.py
```

Run the server from the "project" directory:

```bash
(fast-api-soft-uni) project$ uvicorn app.main:app
INFO:     Started server process [10398]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:64316 - "GET /ping HTTP/1.1" 200 OK
```

app.main:app tells Uvicorn where it can find the FastAPI application -- e.g., "within the 'app' module, you'll find the app, app = FastAPI(), in the 'main.py' file.

Navigate to http://localhost:8000/ping in your browser. You should see:

```json
{
  "ping": "pong!"
}
```

Why did we use Uvicorn to serve up FastAPI rather than a development server?

Unlike Django or Flask, FastAPI does not have a built-in development server. This is both a positive and a negative in my opinion. On the one hand, it does take a bit more to serve up the app in development mode. On the other hand, this helps to conceptually separate the web framework from the web server, which is often a source of confusion for beginners when one moves from development to production with a web framework that does have a built-in development server.

New to ASGI? Read through the excellent Introduction to ASGI: Emergence of an Async Python Web Ecosystem blog post.

FastAPI automatically generates a schema based on the OpenAPI standard. You can view the raw JSON at http://localhost:8000/openapi.json. This can be used to automatically generate client-side code for a front-end or mobile application. FastAPI uses it along with Swagger UI to create interactive API documentation, which can be viewed at http://localhost:8000/docs

Shut down the server.

# Auto-reload
Let's run the app again. This time, we'll enable auto-reload mode so that the server will restart after changes are made to the code base:

```bash 
(fast-api-soft-uni) project$ uvicorn app.main:app --reload
```


```bash 
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [84187]
INFO:     Started server process [84189]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Now when you make changes to the code, the app will automatically reload. Try this out.

# Config
Add a new file called config.py to the "app" directory, where we'll define environment-specific configuration variables:

```python 
# project/app/config.py


import logging

from pydantic import BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0


def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
```

Here, we defined a Settings class with two attributes:

    1. environment - defines the environment (i.e., dev, stage, prod)
    2. testing - defines whether or not we're in test mode
BaseSettings, from pydantic, validates the data so that when we create an instance of Settings, environment and testing will have types of str and bool, respectively.

BaseSettings also automatically reads from environment variables for these config settings. In other words, environment: str = "dev" is equivalent to os.getenv("ENVIRONMENT", "dev").

Update main.py like so:

```python 
# project/app/main.py


from fastapi import FastAPI, Depends

from app.config import get_settings, Settings


app = FastAPI()


@app.get("/ping")
def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
```

Take note of settings: Settings = Depends(get_settings). 
Here, the Depends function is a dependency that declares another dependency, get_settings. 
Put another way, Depends depends on the result of get_settings. The value returned, Settings, is then assigned to the settings parameter.

If you're new to dependency injection, review the Dependencies guide from the official FastAPI docs.

Run the server again. Navigate to http://localhost:8000/ping again. 

This time you should see:

```json 
{
  "ping": "pong!",
  "environment": "dev",
  "testing": false
}
```

Shut down the server and set the following environment variables:

```bash 
(env)$ export ENVIRONMENT=prod
(env)$ export TESTING=1
```
Run the server. Now, at http://localhost:8000/ping, you should see:

```json 
{
  "ping": "pong!",
  "environment": "prod",
  "testing": true
}
```

What happens when you set the TESTING environment variable to foo? Try this out. Then update the variable to 0.

With the server running, navigate to http://localhost:8000/ping and then refresh a few times. Back in your terminal, you should see several log messages for:

Loading config settings from the environment...
Essentially, get_settings gets called for each request. If we refactored the config so that the settings were read from a file, instead of from environment variables, it would be much too slow.

Let's use lru_cache to cache the settings so get_settings is only called once.

Update config.py:

```python 
# project/app/config.py


import logging
from functools import lru_cache

from pydantic import BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
```

After the auto-reload, refresh the browser a few times. 
You should only see one 

```bash
Loading config settings from the environment...
```
log message.

# Async Handlers
Let's convert the synchronous handler over to an asynchronous one.

Rather than having to go through the trouble of spinning up a task queue (like Celery or RQ) or utilizing threads, FastAPI makes it easy to deliver routes asynchronously. As long as you don't have any blocking I/O calls in the handler, you can simply declare the handler as asynchronous by adding the async keyword like so:

```python 
@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
```
That's it. Update the handler in your code, and then make sure it still works as expected.

Shut down the server once done. Exit then remove the virtual environment as well. Then, add a requirements.txt file to the "project" directory:

```bash 
fastapi==0.85.1
uvicorn==0.19.0
```

Finally, add a .gitignore to the project root:

```bash 
__pycache__
env
You should now have:

├── .gitignore
└── project
    ├── app
    │   ├── __init__.py
    │   ├── config.py
    │   └── main.py
    └── requirements.txt
```

Commit your code and push the changes.

# Docker Config
Start by ensuring that you have Docker and Docker Compose:

```bash 
$ docker -v
Docker version 20.10.17, build 100c701

$ docker-compose -v
Docker Compose version v2.10.2
```

Make sure to install or upgrade them if necessary.

Add a Dockerfile to the "project" directory, making sure to review the code comments:

```yaml 
# pull official base image
FROM python:3.10.8-slim-buster

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .
```

Here, we started with a slim-buster-based Docker image for Python 3.10.8. We then set a working directory along with two environment variables:

```bash 
PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc (equivalent to python -B option)
PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr (equivalent to python -u option)
```
We then installed the dependencies and copied over the app.

Depending on your environment, you may need to add 
```yaml
RUN mkdir -p /usr/src/app 
```
just before you set the working directory:

```yaml
# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
```

Add a .dockerignore file to the "project" directory as well:

```bash x
env
.dockerignore
Dockerfile
Dockerfile.prod
```

Like the .gitignore file, the .dockerignore file lets you exclude specific files and folders from being copied over to the image.

Review Docker Best Practices for Python Developers for more on structuring Dockerfiles as well as some best practices for configuring Docker for Python-based development.

Then add a docker-compose.yml file to the project root:

```yaml 
version: '3.8'

services:
  web:
    build: ./project
    command: uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
    volumes:
      - ./project:/usr/src/app
    ports:
      - 8004:8000
    environment:
      - ENVIRONMENT=dev
      - TESTING=0
 ```

This config will create a service called web from the Dockerfile.

So, when the container spins up, Uvicorn will run with the following settings:

```bash
reload enables auto reload so the server will restart after changes are made to the code base.
workers 1 provides a single worker process.
host 0.0.0.0 defines the address to host the server on.
port 8000 defines the port to host the server on.
```

The volume is used to mount the code into the container. This is a must for a development environment in order to update the container whenever a change to the source code is made. Without this, you would have to re-build the image each time you make a change to the code.

Take note of the Docker compose file version used -- 3.8. Keep in mind that this version does not directly relate back to the version of Docker Compose installed; it simply specifies the file format that you want to use.

Build the image:

```bash
$ docker-compose build
```
This will take a few minutes the first time. Subsequent builds will be much faster since Docker caches the results. If you'd like to learn more about Docker caching, review the Order Dockerfile Commands Appropriately section.

Once the build is done, fire up the container in detached mode:

```bash
$ docker-compose up -d
```
Navigate to http://localhost:8004/ping. Make sure you see the same JSON response as before:

```json 
{
  "ping": "pong!",
  "environment": "dev",
  "testing": false
}
```
If you run into problems with the volume mounting correctly, you may want to remove it altogether by deleting the volume config from the Docker Compose file. You can still go through the course without it; you'll just have to re-build the image after you make changes to the source code.

```text
Windows Users: Having problems getting the volume to work properly? Review the following resources:

Docker on Windows — Mounting Host Directories
Configuring Docker for Windows Shared Drives
You also may need to add COMPOSE_CONVERT_WINDOWS_PATHS=1 to the environment portion of your Docker Compose file. Review Declare default environment variables in file for more info.
```

You should now have:

```bash 
├── .gitignore
├── docker-compose.yml
└── project
    ├── .dockerignore
    ├── Dockerfile
    ├── app
    │   ├── __init__.py
    │   ├── config.py
    │   └── main.py
    └── requirements.txt
```

# Postgres
To configure Postgres, we'll need to add a new service to the docker-compose.yml file, add the appropriate environment variables, and install asyncpg.

Add a "db" directory to "project", and add a create.sql file in that new directory:

```bash 
CREATE DATABASE web_dev;
CREATE DATABASE web_test;
```

Next, add a Dockerfile to the same directory:

```yaml 
# pull official base image
FROM postgres:14-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
```

Here, we extended the official Postgres image (an Alpine-based image) by adding create.sql to the "docker-entrypoint-initdb.d" directory in the container. This file will execute on init.

Next, add a new service called web-db to docker-compose.yml:

```yaml 
version: '3.8'

services:

  web:
    build: ./project
    command: uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
    volumes:
      - ./project:/usr/src/app
    ports:
      - 8004:8000
    environment:
      - ENVIRONMENT=dev
      - TESTING=0
      - DATABASE_URL=postgres://postgres:postgres@web-db:5432/web_dev        # new
      - DATABASE_TEST_URL=postgres://postgres:postgres@web-db:5432/web_test  # new
    depends_on:   # new
      - web-db

  # new
  web-db:
    build:
      context: ./project/db
      dockerfile: Dockerfile
    expose:
      - 5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
```
Once spun up, Postgres will be available on port 5432 for services running in other containers. Since the web service is dependent not only on the container being up and running but also the actual Postgres instance being up and healthy, let's add an entrypoint.sh file to the "project" directory:

```bash 
#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z web-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

exec "$@"
```
So, we referenced the Postgres container using the name of the service, web-db. The loop continues until something like Connection to web-db port 5432 [tcp/postgresql] succeeded! is returned.

Update Dockerfile to install the appropriate packages and supply an entrypoint:

```yaml 
# pull official base image
FROM python:3.10.8-slim-buster

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
```

Add asyncpg to project/requirements.txt:

```bash 
asyncpg==0.27.0
```

Next, update config.py to read the DATABASE_URL and assign the value to database_url:

```python 
# project/app/config.py


import logging
from functools import lru_cache

from pydantic import BaseSettings, AnyUrl


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
```

Take note of the AnyUrl validator.

Build the new image and spin up the two containers:

```bash 
$ chmod +x project/entrypoint.sh
$ docker-compose up -d --build
```

Once done, check the logs for the web service:

```bash 
$ docker-compose logs web
```

You should see:

```bash 
web_1  | Waiting for postgres...
web_1  | PostgreSQL started
web_1  | INFO:     Will watch for changes in these directories: ['/usr/src/app']
web_1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
web_1  | INFO:     Started reloader process [1] using statreload
web_1  | INFO:     Started server process [37]
web_1  | INFO:     Waiting for application startup.
web_1  | INFO:     Application startup complete.
```

Depending on your environment, you may need to chmod 755 or 777 instead of +x. If you still get a "permission denied", review the docker entrypoint running bash script gets "permission denied" Stack Overflow question.

Want to access the database via psql?

```bash 
$ docker-compose exec web-db psql -U postgres
```

Then, you can connect to the database:

```bash 
postgres=# \c web_dev
postgres=# \q
```

# Tortoise ORM
To simplify interactions with the database, we'll using an async ORM called Tortoise.

Add the dependency to the requirements.txt file:

```bash 
tortoise-orm==0.19.2
```

Next, create a new folder called "models" within "project/app". Add two files to "models": __init__.py and tortoise.py.

In tortoise.py, add:

```python 
# project/app/models/tortoise.py


from tortoise import fields, models


class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.url
```

Here, we defined a new database model called TextSummary.

Add the register_tortoise helper to main.py to set up Tortoise on startup and clean up on teardown:

```python 
# project/app/main.py

import os

from fastapi import FastAPI, Depends
from tortoise.contrib.fastapi import register_tortoise

from app.config import get_settings, Settings


app = FastAPI()


register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.models.tortoise"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
```

Sanity check:

```bash 
$ docker-compose up -d --build
```

Ensure the textsummary table was created:

```bash 
$ docker-compose exec web-db psql -U postgres

psql (14.5)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".

web_dev=# \dt
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | textsummary | table | postgres
(1 row)

web_dev=# \q
```

http://localhost:8004/ping should still work as well:

```json 
{
  "ping": "pong!",
  "environment": "dev",
  "testing": false
}
```

You should now have:

```bash 
├── .gitignore
├── docker-compose.yml
└── project
    ├── .dockerignore
    ├── Dockerfile
    ├── app
    │   ├── __init__.py
    │   ├── config.py
    │   ├── main.py
    │   └── models
    │       ├── __init__.py
    │       └── tortoise.py
    ├── db
    │   ├── Dockerfile
    │   └── create.sql
    ├── entrypoint.sh
    └── requirements.txt
```

# Migrations
Tortoise supports database migrations via Aerich. Let's take a few steps back and configure it.

First, bring down the containers and volumes to destroy the current database table since we want Aerich to manage the schema:

```bash 
$ docker-compose down -v
```

Next, update the register_tortoise helper in project/app/main.py so that the schemas are not automatically generated:

```python x
register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.models.tortoise"]},
    generate_schemas=False,  # updated
    add_exception_handlers=True,
)
```

Spin the containers and volumes back up:

```bash
$ docker-compose up -d --build
```


Ensure the textsummary table was NOT created:

```bash 
$ docker-compose exec web-db psql -U postgres

psql (14.5)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".

web_dev=# \dt
Did not find any relations.

web_dev=# \q
```

Add Aerich to the requirements file:

```bash 
aerich==0.7.1
```

Then, update the containers:

```bash
$ docker-compose up -d --build
```

Aerich requires the Tortoise config, so let's add that to a new file called project/app/db.py:

```python 
# project/app/db.py


import os


TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

Now we're ready to start using Aerich.

Init:

```bash 
$ docker-compose exec web aerich init -t app.db.TORTOISE_ORM
```

This will create a config file called project/pyproject.toml:

```python
[tool.aerich]
tortoise_orm = "app.db.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

Create the first migration:

```bash 
$ docker-compose exec web aerich init-db

Success create app migrate location migrations/models
Success generate schema for app "models"
```

You should see the following migration inside a new file within "migrations/models":

```python 
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "textsummary" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
```
        
        
That's it! You should now be able to see the two tables:

```bash x
$ docker-compose exec web-db psql -U postgres

psql (14.5)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".

web_dev=# \dt
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | aerich      | table | postgres
 public | textsummary | table | postgres
(2 rows)

web_dev=# \q
```

Be sure to review the documentation to learn more about the available commands. Take note of the downgrade, history, and upgrade commands.


# Let's get our tests up and running for this endpoint with pytest.

# Setup

Add a "tests" directory to the "project" directory, and then create the following files inside the newly created directory:

```bash 
__init__.py # this might need to be removed depending on the env
conftest.py
test_ping.py
```

By default, pytest will auto-discover test files that start or end with test -- e.g., test_*.py or *_test.py. Test functions must begin with test_, and if you want to use classes they must also begin with Test.

Example:

```python 
# if a class is used, it must begin with Test
class TestFoo:

    # test functions must begin with test_
    def test_bar(self):
        assert "foo" != "bar"
```
If this is your first time with pytest be sure to review the Installation and Getting Started guide as well as Pytest for Beginners.

# Fixtures
Define a test_app fixture in conftest.py:

```python 
# project/tests/conftest.py


import os

import pytest
from starlette.testclient import TestClient

from app import main
from app.config import get_settings, Settings


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="module")
def test_app():
    # set up
    main.app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(main.app) as test_client:

        # testing
        yield test_client

    # tear down
```

Here, we imported Starlette's TestClient, which uses the Requests library to make requests against the FastAPI app.

To override the dependencies, we used the dependency_overrides attribute:
```python
main.app.dependency_overrides[get_settings] = get_settings_override
```

dependency_overrides is a dict of key/value pairs where the key is the dependency name and the value is what we'd like to override it with:
```python 
key: get_settings
value: get_settings_override
```

Fixtures are reusable objects for tests. They have a scope associated with them, which indicates how often the fixture is invoked:

```pythonx
function - once per test function (default)
class - once per test class
module - once per test module
session - once per test session
```

Check out All You Need to Know to Start Using Fixtures in Your pytest Code for more on pytest fixtures along with the Fixtures section from Pytest for Beginners.

Take note of the test_app fixture. In essence, all code before the yield statement serves as setup code while everything after serves as the teardown.

For more on this review Fixture finalization / executing teardown code.

Then, add pytest and Requests to the requirements file:
```bash
pytest==7.2.0
requests==2.28.1
```

We need to re-build the Docker images since requirements are installed at build time rather than run time:

```bash x
$ docker-compose up -d --build
```

With the containers up and running, run the tests:

```bash x
$ docker-compose exec web python -m pytest
```

You should see:

```bash x
=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 0 items

============================== no tests ran in 0.07s ==============================
```

# Tests
Moving on, let's add a quick test to test_ping.py:

```python 
# project/tests/test_ping.py


from app import main


def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"environment": "dev", "ping": "pong!", "testing": True}
```

While unittest requires test classes, pytest just requires functions to get up and running. In other words, pytest tests are just functions that either start or end with test.

You can still use classes to organize tests in pytest if that's your preferred pattern.

To use the fixture, we passed it in as an argument.

Run the tests again:

```bash 
$ docker-compose exec web python -m pytest
```

You should see:

```bashx
=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 1 item

tests/test_ping.py .                                                        [100%]

================================ 1 passed in 0.13s ================================
```

# Given-When-Then

When writing tests, try to follow the Given-When-Then framework to help make the process of writing tests easier and faster. It also helps communicate the purpose of your tests better so it should be easier to read by your future self and others.

```bash
State	Explanation	Code
Given	the state of the application before the test runs setup code, fixtures, database state
When	the behavior/logic being tested	code under test
Then	the expected changes based on the behavior	asserts
```

Example:

```python
def test_ping(test_app):
    # Given
    # test_app

    # When
    response = test_app.get("/ping")

    # Then
    assert response.status_code == 200
    assert response.json() == {"environment": "dev", "ping": "pong!", "testing": True}
```


### With tests in place, let's refactor the app, adding in FastAPI's APIRouter, a new database init function, and a pydantic model.

# APIRouter

First, add a new folder called "api" to the "app" folder. Add an ```__init__.py``` file to the newly created folder.

Now we can move the ```/ping``` route to a new file called ```project/app/api/ping.py```:

```python 
# project/app/api/ping.py


from fastapi import APIRouter, Depends

from app.config import get_settings, Settings


router = APIRouter()


@router.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
```

Then, update main.py like so to remove the old route, wire the router up to our main app, and use a function to initialize a new app:

```python 
# project/app/main.py


import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.api import ping


def create_application() -> FastAPI:
    application = FastAPI()

    register_tortoise(
        application,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )

    application.include_router(ping.router)

    return application


app = create_application()
```

Make sure http://localhost:8004/ping and http://localhost:8004/docs still work.

Update the test_app fixture in project/tests/conftest.py to use the create_application function to create a new instance of FastAPI for testing purposes:

```python
# project/tests/conftest.py


import os

import pytest
from starlette.testclient import TestClient

from app.main import create_application  # updated
from app.config import get_settings, Settings


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()  # new
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:  # updated

        # testing
        yield test_client

    # tear down
```

Make sure the tests still pass:

```bash 
$ docker-compose exec web python -m pytest

=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 1 item

tests/test_ping.py .                                                        [100%]

================================ 1 passed in 0.16s ================================
```

You can break up and modularize larger projects as well as apply versioning to your API with the APIRouter. If you're familiar with Flask, it's equivalent to a Blueprint.

Your project structure should now look like:

```bash 
├── .gitignore
├── docker-compose.yml
└── project
    ├── .dockerignore
    ├── Dockerfile
    ├── app
    │   ├── __init__.py
    │   ├── api
    │   │   ├── __init__.py
    │   │   └── ping.py
    │   ├── config.py
    │   ├── db.py
    │   ├── main.py
    │   └── models
    │       ├── __init__.py
    │       └── tortoise.py
    ├── db
    │   ├── Dockerfile
    │   └── create.sql
    ├── entrypoint.sh
    ├── migrations
    │   └── models
    │       └── 0_20211227001140_init.sql
    ├── pyproject.toml
    ├── requirements.txt
    └── tests
        ├── __init__.py
        ├── conftest.py
        └── test_ping.py
```

# Database Init

Next, let's move the ```register_tortoise``` helper to ```project/app/db.py``` to clean up project/app/main.py:

```python 
# project/app/db.py


import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )
```

Import init_db into main.py:

```python 
# project/app/main.py


import logging

from fastapi import FastAPI

from app.api import ping
from app.db import init_db


log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
```   

Here, we added startup and shutdown event handlers, which get executed before the app starts up or when the app shuts down, respectively.

To test, first bring down the containers and volumes:

```bash x
$ docker-compose down -v
```

Then, bring the containers back up:

```bash 
$ docker-compose up -d --build
```

Since we haven't applied the migrations, you shouldn't see any tables in the database:

```bash 
$ docker-compose exec web-db psql -U postgres

psql (14.5)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".

web_dev=# \dt
Did not find any relations.

web_dev=# \q
```

Rather than applying the migrations via Aerich, which can be slow, 
there may be times where you just want to apply the schema to the 
database in its final state. 
So, let's add a ```generate_schema``` function to ``db.py`` for handling that:

```python 
# project/app/db.py


import logging  # new
import os

from fastapi import FastAPI
from tortoise import Tortoise, run_async  # new
from tortoise.contrib.fastapi import register_tortoise


log = logging.getLogger("uvicorn") # new


TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )


# new
async def generate_schema() -> None:
    log.info("Initializing Tortoise...")

    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["models.tortoise"]},
    )
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


# new
if __name__ == "__main__":
    run_async(generate_schema())
```

So, ```generate_schema``` calls ```Tortoise.init``` to set up ```Tortoise``` and then generates the schema.

Run:

```bash 
$ docker-compose exec web python app/db.py
```

You should now see the schema:

```bash 
$ docker-compose exec web-db psql -U postgres

psql (14.5)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".

web_dev=# \dt
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | textsummary | table | postgres
(1 row)

web_dev=# \q
```

Finally, since we do want to use Aerich in dev to manage the database schema, bring the containers and volumes down again:

```bash 
$ docker-compose down -v
```

bring the containers back up:
```bash 
$ docker-compose up -d --build
```

Confirm that the table doesn't exist in the database. Then, apply the migration:

```bash 
$ docker-compose exec web aerich upgrade
```

Confirm that the aerich and textsummary tables now exist.

# Pydantic Model

First time using pydantic? Review the Overview guide from the official docs.

Create a SummaryPayloadSchema pydantic model with one required field -- a url -- in a new file called pydantic.py in "project/app/models":

```python
# project/app/models/pydantic.py


from pydantic import BaseModel


class SummaryPayloadSchema(BaseModel):
    url: str
```

We'll use this model in the next section.


### Next, let's set up three new routes, following RESTful best practices, with TDD:

```bash 
Endpoint	HTTP Method	CRUD Method	Result
/summaries	GET	READ	get all summaries
/summaries/:id	GET	READ	get a single summary
/summaries	POST	CREATE	add a summary
```

For each, we'll:

```bash 
write a test
run the test, to ensure it fails (red)
write just enough code to get the test to pass (green)
refactor (if necessary)
```

Let's start with the POST route.

# POST Route

We'll break from the normal TDD flow for this first route in order to establish the pattern that we'll use for the remaining routes.

# Code

Create a new file called ```summaries.py``` in the ```"project/app/api"``` folder:

```python 
# project/app/api/summaries.py


from fastapi import APIRouter, HTTPException

from app.api import crud
from app.models.pydantic import SummaryPayloadSchema, SummaryResponseSchema


router = APIRouter()


@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema) -> SummaryResponseSchema:
    summary_id = await crud.post(payload)

    response_object = {
        "id": summary_id,
        "url": payload.url
    }
    return response_object
```

Here, we defined a handler that expects a payload, ```payload: SummaryPayloadSchema```, with a URL.

Essentially, when the route is hit with a POST request, FastAPI will read the body of the request and validate the data:

```
If valid, the data will be available in the payload parameter. FastAPI also generates JSON Schema definitions that are then used to automatically generate the OpenAPI schema and the API documentation.
If invalid, an error is immediately returned.
```

Review the Request Body docs for more info.

It's worth noting that we used the async declaration here since the database communication will be asynchronous. In other words, there are no blocking I/O operations in the handler.

Next, create a new file called ```crud.py``` in the ```"project/app/api"``` folder:

```python 
# project/app/api/crud.py


from app.models.pydantic import SummaryPayloadSchema
from app.models.tortoise import TextSummary


async def post(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(
        url=payload.url,
        summary="dummy summary",
    )
    await summary.save()
    return summary.id
```

We added a utility function called post for creating new summaries that takes a payload object and then:

```
Creates a new TextSummary instance
Returns the generated ID
```

Next, we need to define a new pydantic model for use as the response_model:

```python
@router.post("/", response_model=SummaryResponseSchema, status_code=201)
```

Update ```pydantic.py``` like so:

```python 
# project/app/models/pydantic.py


from pydantic import BaseModel


class SummaryPayloadSchema(BaseModel):
    url: str


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int
```

The ```SummaryResponseSchema``` model inherits from the ```SummaryPayloadSchema``` model, adding an id field.

Wire up the new router in ```main.py```:

```python 
# project/app/main.py


import logging

from fastapi import FastAPI

from app.api import ping, summaries  # updated
from app.db import init_db


log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)
    application.include_router(summaries.router, prefix="/summaries", tags=["summaries"])  # new

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
```

Take note of the prefix URL along with the ```"summaries"``` tag, which will be applied to the OpenAPI schema (for grouping operations).

Test it out with curl or HTTPie:

```bash x
$ http --json POST http://localhost:8004/summaries/ url=https://google.com
```

You should see:

```bash
HTTP/1.1 201 Created
content-length: 37
content-type: application/json
date: Sat, 29 Oct 2022 15:18:20 GMT
server: uvicorn

{
    "id": 1,
    "url": "http://testdriven.io"
}
```
You can also interact with the endpoint at http://localhost:8004/docs.

# Test

First, add a new file called test_summaries.py to "project/tests". Then, add the following test:

```python 
# project/tests/test_summaries.py


import json

import pytest


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://foo.bar"}))

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"
```

Add the new fixture to conftest.py:

```python 
import os

import pytest
from starlette.testclient import TestClient

from app.main import create_application
from app.config import get_settings, Settings


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:

        # testing
        yield test_client

    # tear down


# new
@pytest.fixture(scope="module")
def test_app_with_db():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:

        # testing
        yield test_client

    # tear down
```

Add the import as well:
```python x
from tortoise.contrib.fastapi import register_tortoise
```

Run the tests:
```bash 
$ docker-compose exec web python -m pytest

=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 2 items

tests/test_ping.py .                                                        [ 50%]
tests/test_summaries.py .                                                   [100%]

================================ 2 passed in 0.19s ================================
```

Did a warning get outputted? Pass -p no:warnings on the command-line in to disable them.

This test covers the happy path. What about the exception path?

Add a new test:

```python x
# project/tests/test_summaries.py


import json

import pytest


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://foo.bar"}))

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"


def test_create_summaries_invalid_json(test_app):
    response = test_app.post("/summaries/", data=json.dumps({}))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }
```

It should pass.

With that, we can configure the remaining CRUD routes using Test-Driven Development.

```bash 
├── .gitignore
├── docker-compose.yml
└── project
    ├── .dockerignore
    ├── Dockerfile
    ├── app
    │   ├── __init__.py
    │   ├── api
    │   │   ├── __init__.py
    │   │   ├── crud.py
    │   │   ├── ping.py
    │   │   └── summaries.py
    │   ├── config.py
    │   ├── db.py
    │   ├── main.py
    │   └── models
    │       ├── __init__.py
    │       ├── pydantic.py
    │       └── tortoise.py
    ├── db
    │   ├── Dockerfile
    │   └── create.sql
    ├── entrypoint.sh
    ├── migrations
    │   └── models
    │       └── 0_20211227001140_init.sql
    ├── pyproject.toml
    ├── requirements.txt
    └── tests
        ├── __init__.py
        ├── conftest.py
        ├── test_ping.py
        └── test_summaries.py
```

# GET single summary Route

Start with a test:

```python 
def test_read_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://foo.bar"}))
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"]
    assert response_dict["created_at"]
```

Ensure the test fails:
```bash
>       assert response.status_code == 200
E       assert 404 == 200
E        +  where 404 = <Response [404]>.status_code
```

Add the following handler:

```python
@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(id: int) -> SummarySchema:
    summary = await crud.get(id)

    return summary
```

Here, instead of taking a payload, the handler requires an id, an integer, which will come from the path -- i.e., /summaries/1/.

Add the get utility function to crud.py:

```python x
async def get(id: int) -> Union[dict, None]:
    summary = await TextSummary.filter(id=id).first().values()
    if summary:
        return summary
    return None
```

Add the import:

```from typing import Union```

Here, we used the values method to create a ValuesQuery object. Then, if the TextSummary exists, we returned it as a dict.

```Union[dict, None]``` is equivalent to ```Optional[dict]```, so feel free to update this if you prefer Optional over Union.

Next, update ```project/app/models/tortoise.py``` to generate a pydantic model from the Tortoise model:

```python x
# project/app/models/tortoise.py


from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator  # new


class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.url


SummarySchema = pydantic_model_creator(TextSummary)  # new
```
Import SummarySchema into ```project/app/api/summaries.py```:

```from app.models.tortoise import SummarySchema```

Ensure the tests pass:

```bash
$ docker-compose exec web python -m pytest

=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 4 items

tests/test_ping.py .                                                        [ 25%]
tests/test_summaries.py ...                                                 [100%]

================================ 4 passed in 0.20s ================================
```

What if the summary ID doesn't exist?

Add a new test:

```python 
def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
```

It should fail:

```bash 
>       assert response.status_code == 404
E       assert 200 == 404
E        +  where 200 = <Response [200]>.status_code
```

Update the code:

```python 
@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(id: int) -> SummarySchema:
    summary = await crud.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary
```

It should now pass:

```bash 
=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 5 items

tests/test_ping.py .                                                        [ 20%]
tests/test_summaries.py ....                                                [100%]

================================ 5 passed in 0.21s ================================
```

Before moving on, manually test the new endpoint in the browser, with curl or HTTPie, and/or via the API documentation.

# GET all summaries Route
Again, let's start with a test:
```python x
def test_read_all_summaries(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "https://foo.bar"}))
    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1
```

Make sure it fails. Then add the handler:

```python 
@router.get("/", response_model=List[SummarySchema])
async def read_all_summaries() -> List[SummarySchema]:
    return await crud.get_all()
```
Import List from Python's typing module:

``` from typing import List ```

The response_model is a List with a SummarySchema subtype.

Add the CRUD util:

```python 
async def get_all() -> List:
    summaries = await TextSummary.all().values()
    return summaries
```
Update the import:

```from typing import Union, List```

Does the test past?

```bash 
=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 6 items

tests/test_ping.py .                                                        [ 16%]
tests/test_summaries.py .....                                               [100%]

================================ 6 passed in 0.22s ================================
```

Manually test this endpoint as well.

# Selecting Tests
You can select specific tests to run using substring matching.

For example, to run all tests that have ping in their names:

```bash x
$ docker-compose exec web python -m pytest -k ping

=============================== test session starts ===============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0
rootdir: /usr/src/app
plugins: anyio-3.6.2
collected 6 items / 5 deselected / 1 selected

tests/test_ping.py .                                                        [100%]

========================= 1 passed, 5 deselected in 0.14s =========================
```
So, you can see that the single test in test_ping.py ran (and passed) while the five tests in test_summaries.py were skipped.

Which test(s) will run when you run this command:

```bash 
$ docker-compose exec web python -m pytest -k read
```

# Pytest Commands
Before moving on, let's review some useful pytest commands:

```bash 
# normal run
$ docker-compose exec web python -m pytest

# disable warnings
$ docker-compose exec web python -m pytest -p no:warnings

# run only the last failed tests
$ docker-compose exec web python -m pytest --lf

# run only the tests with names that match the string expression
$ docker-compose exec web python -m pytest -k "summary and not test_read_summary"

# stop the test session after the first failure
$ docker-compose exec web python -m pytest -x

# enter PDB after first failure then end the test session
$ docker-compose exec web python -m pytest -x --pdb

# stop the test run after two failures
$ docker-compose exec web python -m pytest --maxfail=2

# show local variables in tracebacks
$ docker-compose exec web python -m pytest -l

# list the 2 slowest tests
$ docker-compose exec web python -m pytest --durations=2
```

