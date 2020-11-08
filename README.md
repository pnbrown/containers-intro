# A Developer's Introduction to Containers

Welcome to a Developer's Introduction to Containers. 

By the end of the workshop you will have acheived three outcomes: 
1. You'll understand what containers are and how they came onto the scene 
2. You'll be able to containerize an application and run it locally  
3. You'll be able to deploy your container image to a remote registry.

To complete this workshop, you will need to have Docker installed on your machine as well as an account on Docker Hub.

## Part 1: What are containers and how did they get here?

#### The what:

If there are two words that come to mind when you think containers, they should be **process isolation**.

> “Put most simply, a process is an instance of an executing program...processes are the entities among which the kernel must share the various resources of the computer.” Michael Kerrisk, _The Linux Programming Interface_

A **container** is a process, or group of processes running in isolation. This isolation is achieved by leveraging several features of the Linux kernel. Two of the main features are **namespaces** and **cgroups**. 

> "A namespace wraps global system resources in an abstraction that makes it appear to the process within the namespace that they have their own instance of the resource." _namespaces man page_

A metaphor I like for this concept are apartments in an apartment building. Utilities come in to the apartment building, but it appears to each apartment that they have their own instance. In our usecase, the utilities represent resources like the network, the process id counter, and more.

> "Control groups, usually referred to as cgroups, are a Linux feature which allow processes to be organized into hierarchical groups whose usage of various types of resources can then be limited and monitored." _cgroups man page_

One use of cgroups is assigning a maximum amount of resources each group can allocate to ensure that your critical system processes always have the resources they need.

#### The how:

Containers are not a particularly new technology. They falls under a class of virtualization called Operating System Level Virtualization. It's possible that you became familiar with some other iteration of this technology. We'll touch on some of the more notable points:

Unix in 1982 had a feature called chroot which allows the "root" directory to be changed. This had an effect of isolation, but for security, it is rarely the best choice. The first major point we have for commercial adoption of what came to be known as containerization was from Virtuozzo's release in 2000. The next point of note is the concept of Zones which came from the Solaris operating system in 2005. It's notable that the term "container" most likely came from Solaris. The widespread adoption, and, anecdotally, the first interaction with containers came with Linux Containers or lxc in 2008. When Docker came on the scene in 2013, they weren't creating new technology per se, but making it easier and more secure to leverage containers for today's workloads. In fact, Docker's initial releases used lxc before they wrote their own implementation.

The software Docker created to interact with the Linux kernel was packaged into a library called libcontainer. For standardization and to further encourage the development of containerization technology, Docker donated libcontainer to the Cloud Native Computing Foundation (CNCF) to start the Open Container Initiative (OCI).

## Part 2: Containerize an application and run it locally

In this section, we'll use a minimal Python application to demonstrate how to containerize an application. This one is written by my friend Mofi Rahman and it greets a website visitor by name and then provides them a quote of the day. After containerizing, you are strongly encouraged to customize the application.

Make sure you get a copy of the repository locally by cloning it with Git.

`git clone https://github.com/pnbrown/containers-intro`

### The application

We chose Python as an accessible language for participants. There are four files that comprise the application: `hello.py`, `quotes.txt`,`requirements.txt`, and `templates/view.html` which contain our web server, list of quotes, dependencies, and the web page respectively.

When a user visits our site at the root url, they'll see text defined in our `hello.py` server. If they then append `/hello/$your_name` they will get to the page defined in `templates/view.html` which will show them a random quote from `quotes.txt`.

If you have a local Python 3 installation and want to run the application before containerizing, you may by following these steps after navigating to the project directory:

1. First install the dependencies, which, in this case, is Flask 1.1.1

    `pip install --trusted-host pypi.python.org -r requirements.txt`

2. Start the application:

    `python hello.py`

### Writing a Dockerfile

In the world of containers, it's helpful to know the difference between a _container_, an _image_, and a _registry_. We mentioned earlier that a container is a process or group of processes _running_ in isolation. But what about when the process(es) are not running?

Containers are built from a set of instructions. Commonly, the instructions are contained in a text file called a Dockerfile. From these instructions are built an _image_. Images are stored in _registries_ until they're ready to be run. You can think of an image as a recipe and the required ingredients and the container as our cooked meal while registries would be the cookbooks in which we keep our recipes.

So now let's gather our ingredients and write our recipe.

You're going to need to edit the empty Dockerfile in the root directory.

Container images are created in modular layers. Generally, each line in a Dockerfile creates a new layer that builds upon the one immediately preceding it. The unique hash for each layer is then calculated and cataloged. In practice, this speeds up subsequent container builds because the modular layers contained in our images are reused whenever possible. This means that the first builds will generally take some time, but each subsequent build completes much faster. Further, you should ensure that the lines of the Dockerfile most likely to change are toward the bottom to ensure speedy builds. Docker will only rebuild the image from the line that changed to the end of the file.



1. The first line of our Dockerfile defines a base image. We're using one created by the Python organization that uses the Alpine operating system:

    `FROM python:alpine3.7`

2. The second line creates and sets our working directory for the image for any of the subsequent adding, copying, or running of files:

    `WORKDIR /app`

3. The third line copies our requirements into our working directory:

    `COPY requirements.txt /app`

4. The fourth line installs our dependencies that Python will need. By using the image that the Python organization created, we can ensure that everything Python needs to run is already a part of our image:

    `RUN pip install --trusted-host pypi.python.org -r requirements.txt`

5. The fifth line copies the rest of our current directory into the working directory so we can access all of our files once the container is running:

    `COPY . /app`

6. The sixth line indicates on which ports Docker should listen when our application is running. This Flask app runs on port 80 so we'll expose that:

    `EXPOSE 80`

7. The seventh line determines the entry point for the running container. After the container is built, it runs the entrypoint command. Ours will be python:

    `ENTRYPOINT [ "python" ]`

8. The eigth line sets the command that is provided to the entrypoint. For our purposes, we want to run the hello.py file we copied over:

    `CMD ["./hello.py"]`

All together, your Dockerfile should be comprised of what follows:

```
FROM python:alpine3.7

WORKDIR /app

COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt 

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python" ]

CMD [ "./hello.py" ]
```

In case something has gone wrong, there is a completed Dockerfile in the safety directory that you can use.

### Building our Docker image

We wrote the recipe for our container and now we need to assemble the ingredients through the building of the container image. The Docker engine will go line by line of our Dockerfile and assemble it. If you have an account on Docker Hub, please use that when you name your image. You should use the tag for version control. Use whatever versioning or tag makes sense for you.

```
docker build -t <username>/<imagename>:<tag> .
```

### Running our image locally

Now that we've built our image, we can run it locally and see our process(es) running in isolation. We need to map that port we exposed in our Dockerfile to one that's not currently in use by our system. I often use port 4567. That is reflected in the command below. The `-p` flag handles the port mapping in the form host_port:container_port. Additionally, you can use the `-d` flag to run the container in the background or detached mode.

`docker run -p 4567:80 <username>/<imagename>:<tag>`


## Part 3: Deploy your image to a remote registry

When we've built our container, it get stored in the local container registry on our machine. You can see all the images currently in our local registry (cookbook) with the `docker images` command. Some recipes are too good to keep to ourselves. We can share it by publishing it to a remote registry. For our case, we'll share it to Docker Hub.

### Push it to Docker Hub

We refer to putting images in repositories as "pushing" them. Once you log into your Docker account, you can then push your image to your repository. Once it's there, anyone can "pull" your image to their local registry and run it.

```
docker login
docker push <username>/<imagename>:<tag>
```
