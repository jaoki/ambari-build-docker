how to build
--------------------

```
docker build -t ambari/build ./docker
```

how to run
--------------------

```
# bash
docker run --privileged -t -i -p 80:80 -p 5005:5005 -p 8080:8080 -h node1.mydomain.com --name ambari1 -v ${AMBARI_SRC:-$(pwd)}:/tmp/ambari ambari/build bash
# where 5005 is java debug port and 8080 is the default http port, if no --privileged ambari-server start fails due to access to /proc/??/exe
# -t is required otherwise, sudo commands do not run

# build, install ambari and deploy hadoop in container
cd {ambari src}
docker rm ambari1
docker run --privileged -t -p 80:80 -p 5005:5005 -p 8080:8080 -h node1.mydomain.com --name ambari1 -v ${AMBARI_SRC:-$(pwd)}:/tmp/ambari ambari/build /tmp/ambari-build-docker/bin/ambaribuild.py [test|server|agent|deploy] [-b] [-s [HDP|BIGTOP|PHD]]
where
test: mvn test
server: install and run ambari-server
agent: install and run ambari-server and ambari-agent
deploy: install and run ambari-server and ambari-agent, and deploy a hadoop
-b option to rebuild ambari
```

