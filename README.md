# agento: the First Osmotic Agent

**Authors**: [Lorenzo Carnevale](mailto:lorenzocarnevale@gmail.com)

The agento project follows the idea extracted by [*Osmotic Computing: A New Paradigm for Edge/Cloud Integration, M. Villari, M. Fazio, S. Dustdar, O. Rana and R. Ranjan*](http://ieeexplore.ieee.org/document/7802525/). It proposed the Osmotic Computing, in 2016, as a new promising paradigm for the integration between a centralised Cloud layer and Edge/Internet of Things (IoT) layers; whereas its basic principles and enabling technologies were presented in [*Towards Osmotic Computing: Looking at Basic Principles and Technologies, M. Villari, A. Celesti, M. Fazio*](https://link.springer.com/chapter/10.1007/978-3-319-61566-0_86).

## Why agento?
agento is the first ever designed Osmotic Agent. Its task is to mark devices (i.e. microprocessors, virtual machines or physical machines) through the installation of a software that enables communication from/to the Osmotic architecture core.

agento is a lightweight virtual machine that interacts with the host operating system in order to monitor host itself and other virtual machines; and deploy MicroELements (MELs) on the same level.

<p align="center">
	<img src="https://github.com/lcarnevale/agento/blob/master/doc/figure/agento1.png?raw=true">
</p>

It is designed on three layers. The Interface layer includes the RESTful APIs for using the deploy and monitor funcionalities. It is an HTTP interface for enabling the Osmotic Agent services and receives instructions from the architecture core. On the other hand, the Event producer consumes the data received from the Storage Layer and sends these to the architecture core.
The Service layer includes two functionalities, such as Deploy and Monitor. The first one is a service application addressed for deploying the injected MELs. It is enabled by means of the RESTful APIs. The second one is a service application addressed for monitoring the active resources. It is also enabled by means of the RESTful APIs.
The Storage layer includes an In-Memory database that implements the Publish/Subscribe messaging paradigm. It works as message broker, in which the Deploy and Monitor Blocks are Publisher; whereas the Event Producer is a Subscriber.

<p align="center">
	<img src="https://github.com/lcarnevale/agento/blob/master/doc/figure/agento2.png?raw=true">
</p>


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
$ export FLASK_APP=main.py
$ flask run
```

Try the web server:
```bash
$ curl -i http://localhost:5000/api/v1
```

## RESTful APIs list
This project implements two services.

Application | HTTP Methods  | Url
----------- | ------------- | -----------
Monitor  	| PUT, DELETE 	| /api/v1/monitor/<string:resource>/<string-target>
execute  	| PUT, DELETE 	| /api/v1/deploy

### Monitor

- **/api/v1/monitor**

- **Method**

	PUT | DELETE

- **URL Params**

	/api/v1/monitor/\<string:option\>
	
	**Required**:
	
	option=[string]

- **Data Params**

	```bash
	{
		"time":[integer], 
		"source":[string]
	}
	```

	- *time* represents the sample time in second;
	- *source* represents the source from which is read the monitor. It is **host** or **guest**.

- **Success Response**

	- {'response': True, 'status': 200}

- **Error Response**

	- **Code**: 404 Not Found
	- **Code**: 400 Bad Request

- **Sample Call**

	```bash
	$ curl -i -X PUT \
	-H "Content-Type: application/json" \
	-d '{ \
		"time":2, \
		"source":"guest" \
	}' \
	http://localhost:5000/api/v1/monitor/mem
	```

	```bash
	$ curl -i -X DELETE \
	-H "Content-Type: application/json" \
	-d '{ \
		"source":"guest" \	
	}' \
	http://localhost:5000/api/v1/monitor/mem
	```

- **Note**

	The PUT API executes a child program in a new process for monitoring cpu, network or memory. It run separately process for each monitor. You are able to monitor host cpu with sample time 5 second and guest mem with sample time 10 second.
	The DELETE API executes a child program in a new process for killing the monitoring.

### Deploy

- **/api/v1/deploy**

- **Method**

	PUT | DELETE

- **Data Params**

	```bash
	{
		"image":[string],
		"name":[string],
		"command":[string or list]
		"ports":[dict],
		"volumes":[dict],
		"privileged":[bool],
	}
	```

	- *image* - The image to run;
	- *name* - The name for this container;
	- *command* - The command to run in the container;
	- *ports* - Ports to bind inside the container. The keys of the dictionary are the ports to bind inside the container, either as an integer or a string in the form port/protocol, where the protocol is either tcp or udp
	- *privileged* - Give extended privileges to this container;
	- *volumes* - A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys: bind The path to mount the volume inside the container; mode Either rw to mount the volume read/write, or ro to mount it read-only.

	For more details [here](https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run)


- **Success Response**

	- {'response': True, 'status': 200}

- **Error Response**

	- **Code**: 400 Bad Request
	- **Code**: 409 Client Error

- **Sample Call**

	```bash
	$ curl -i -X PUT \
	-H "Content-Type: application/json"  \
	-d '{ \
		"image":"redis:4.0.8-alpine", \
		"ports":"", \
		"name":"redis", \
		"host":"", \
		"volumes":"", \
		"privileged":"", \
		"command":"" \
	}' \
	http://localhost:5000/api/v1/deploy
	```

	```bash
	$ curl -i -X DELETE \
	-H "Content-Type: application/json"  \
	-d '{ \
		"name":"redis", \
		"image":"redis:4.0.8-alpine" \
	}' \
	http://localhost:5000/api/v1/deploy
	```

- **Note**

	The PUT API downloads (if not present the image) and runs a container in detach mode.
	The DELETE API stops and removes the container and deletes the images.

## Bibliography

```latex
@article{Villari2016,
	doi = {10.1109/mcc.2016.124},
	url = {https://doi.org/10.1109/mcc.2016.124},
	year  = {2016},
	month = {nov},
	publisher = {Institute of Electrical and Electronics Engineers ({IEEE})},
	volume = {3},
	number = {6},
	pages = {76--83},
	author = {Massimo Villari and Maria Fazio and Schahram Dustdar and Omer Rana and Rajiv Ranjan},
	title = {Osmotic Computing: A New Paradigm for Edge/Cloud Integration},
	journal = {{IEEE} Cloud Computing}
}

@InProceedings{10.1007/978-3-319-61566-0_86,
	author="Villari, Massimo and Celesti, Antonio and Fazio, Maria",
	editor="Barolli, Leonard and Terzo, Olivier",
	title="Towards Osmotic Computing: Looking at Basic Principles and Technologies",
	booktitle="Complex, Intelligent, and Software Intensive Systems",
	year="2018",
	publisher="Springer International Publishing",
	address="Cham",
	pages="906--915",
	abstract="Osmotic Computing is becoming the new paradigm in the area of Computing. This paper shows how it can represents the glue of recent topics including Cloud, Edge and Fog Computing, and Internet of Things (IoT). Osmotic Computing introduces elements allowing to treat computation, networking, storage, data transfer and management among Cloud and IoT devices in Edge computing layers in a more harmonized fashion. In particular, we discuss how it can enable an abstraction of services that could bring into a new Software Defined of Everything era.",
	isbn="978-3-319-61566-0"
}
```
## Credits
agento is part of the Osmotic Computing activities carried out at both University of Messina and TU Wien.