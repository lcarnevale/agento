# agento

The agento project follows the idea extracted by [*Osmotic Computing: A New Paradigm for Edge/Cloud Integration, M. Villari, M. Fazio, S. Dustdar, O. Rana and R. Ranjan*](http://ieeexplore.ieee.org/document/7802525/). It represents a new computation paradigm that aims to put togheter different Cloud layer, such as Cloud, Fog ad Edge.

## Why agento?

## Getting Started

The instructions below will get you a copy of the project on your local machine for developing and testing.

### Installing

The *requirements.txt* file includes all the project python dependencies.
```bash
$ pip install -r requirements.txt
```

### Running the web server

The following commands will help you to start the web service.

```bash
$ export FLASK_APP=restful.py
$ flask run
```

### How to use it
```bash
$ curl -i -X PUT \
-H "Content-Type: application/json" \
-d '{"time":2, "source":"guest"}' \
http://localhost:5000/api/v1/monitor/mem
```

```bash
$ curl -i -H "Content-Type: application/json" -X DELETE -d '{"source":"guest"}' http://localhost:5000/api/v1/monitor/mem
```

```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"image":"redis","port":"","name":"some-redis","host":"","volume":"","privileges":"","command":""}' http://localhost:5000/api/v1/deploy
```

```bash
$ curl -i -H "Content-Type: application/json" -X DELETE -d '{"name":"some-redis", "image":"redis"}' http://localhost:5000/api/v1/deploy
```

## RESTful APIs list