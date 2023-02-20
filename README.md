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
