# agento: the First Osmotic Agent

**Authors**: [Lorenzo Carnevale](mailto:lorenzocarnevale@gmail.com)

The agento project follows the idea extracted by [*Osmotic Computing: A New Paradigm for Edge/Cloud Integration, M. Villari, M. Fazio, S. Dustdar, O. Rana and R. Ranjan*](http://ieeexplore.ieee.org/document/7802525/). It presented the Osmotic Computing in 2016 as a new promising paradigm for the integration between a centralised Cloud layer and Edge/Internet of Things (IoT) layers; whereas its basic principles and enabling technologies were presented in [*Towards Osmotic Computing: Looking at Basic Principles and Technologies, M. Villari, A. Celesti, M. Fazio*](https://link.springer.com/chapter/10.1007/978-3-319-61566-0_86).

## Why agento?
agento is the first ever designed and developed Osmotic Agent. Its task is to mark the devices (i.e. microprocessors, virtual machines or physical machines) through the installation of a software that enables communication from/to the Osmotic architecture core.

agento is a lightweight virtual machine that interacts with the host operating system in order to monitor host itself and other virtual machines; and deploy MicroELements (MELs) on the same level.

![agento-environment](https://github.com/lcarnevale/agento/blob/master/doc/figure/agento1.png?raw=true)

It is designed on three layers. The Interface layer includes the RESTful APIs for using the deploy and monitor funcionalities. It is an HTTP interface for enabling the Osmotic Agent services and receives instructions from the architecture core. On the other hand, the Event producer consumes the data received from the Storage Layer and sends these to the architecture core.
The Service layer includes two functionalities, such as Deploy and Monitor. The first one is a service application addressed for deploying the injected MELs. It is enabled by means of the RESTful APIs. The second one is a service application addressed for monitoring the active resources. It is also enabled by means of the RESTful APIs.
The Storage layer includes an In-Memory database that implements the Publish/Subscribe messaging paradigm. It works as message broker, in which the Deploy and Monitor Blocks are Publisher; whereas the Event Producer is a Subscriber.

![agento-architecture](https://github.com/lcarnevale/agento/blob/master/doc/figure/agento2.png?raw=true)


## Getting Started
The instructions below will get you a copy of the project on your local machine for developing and testing.

### Prerequisities
agento makes use of Docker.
```bash
$ lcarnevale@lcarnevale-pc:~/mypath$ docker version
Client:
 Version:	17.12.0-ce
 API version:	1.35
 Go version:	go1.9.2
 Git commit:	c97c6d6
 Built:	Wed Dec 27 20:11:19 2017
 OS/Arch:	linux/amd64

Server:
 Engine:
  Version:	17.12.0-ce
  API version:	1.35 (minimum version 1.12)
  Go version:	go1.9.2
  Git commit:	c97c6d6
  Built:	Wed Dec 27 20:09:53 2017
  OS/Arch:	linux/amd64
  Experimental:	false
```

### Installing
This project is compatible with **python2.7**. The *requirements.txt* file includes all the dependencies.
```bash
$ pip install -r requirements.txt
```

### Running the web server
The following commands will help you to start the web service.

```bash
$ export FLASK_APP=restful.py
$ flask run
```

Try the web server:
```bash
$ curl -i http://localhost:5000/api/v1
```

### How to use it
```bash
$ curl -i -X PUT \
-H "Content-Type: application/json" \
-d '{"time":2, "source":"guest"}' \
http://localhost:5000/api/v1/monitor/mem
```

```bash
$ curl -i -X DELETE \
-H "Content-Type: application/json" \
-X DELETE -d '{"source":"guest"}' \
http://localhost:5000/api/v1/monitor/mem
```

```bash
$ curl -i -X PUT \
-H "Content-Type: application/json"  \
-d '{"image":"redis:4.0.8-alpine","ports":"","name":"redis","host":"","volumes":"","privileged":"","command":""}' \
http://localhost:5000/api/v1/deploy
```

```bash
$ curl -i -X DELETE \
-H "Content-Type: application/json"  \
-d '{"name":"redis", "image":"redis:4.0.8-alpine"}' \
http://localhost:5000/api/v1/deploy
```

## RESTful APIs list
This project implements two services.

### Monitor

- /api/v1/monitor/\<string:option\>
	Execute a child program in a new process.


## Credits
agento is the result of research conducted at the University of Messina. 