how to build
--------------------

```
sudo docker build -t ambari/build .
```

how to run
--------------------

```
# bash
sudo docker run --privileged -t -i -p 5005:5005 -p 8080:8080 -h host1.mydomain.com --name ambari1 -v ${AMBARI_SRC}:/tmp/ambari ambari/build bash
# where 5005 is java debug port and 8080 is the default http port, if no --privileged ambari-server start fails due to access to /proc/??/exe

# build, install ambari and deploy hadoop in container
sudo docker run --privileged -t -i -p 5005:5005 -p 8080:8080 -h host1.mydomain.com --name ambari1 -v ${AMBARI_SRC}:/tmp/ambari ambari/build /tmp/ambari-build-docker/install.sh

```

how to build ambari
----------------------------

```
mvn -B clean install package rpm:rpm -Dmaven.clover.skip=true -Dfindbugs.skip=true -DskipTests -Dpython.ver="python >= 2.6" -Preplaceurl
```

how to install ambari
----------------------------

```
sudo yum install -y ambari-server/target/rpm/ambari-server/RPMS/noarch/ambari-server-*.noarch.rpm ambari-agent/target/rpm/ambari-agent/RPMS/x86_64/ambari-agent-*.x86_64.rpm

sudo service ntpd start
echo -e '\n\n\n\n' | sudo ambari-server setup
sudo ambari-server start # or --debug


sudo service sshd start
sudo sed -i "s/hostname=localhost/hostname=$(hostname -f)/g" /etc/ambari-agent/conf/ambari-agent.ini && service ambari-agent start
```

how to deploy Hadoop
---------------------

```
# find IP of container
AMBARI1_IP=`docker inspect --format='{{.NetworkSettings.IPAddress}}' ambari1`
curl -X POST -D - -d @single-node-blueprint1.json http://${AMBARI1_IP}:8080/api/v1/blueprints/myblueprint1 --header "Authorization:Basic YWRtaW46YWRtaW4=" --header "X-Requested-By: PIVOTAL"
curl -X POST -D - -d @single-node-hostmapping1.json http://${AMBARI1_IP}:8080/api/v1/clusters/mycluster1 --header "Authorization:Basic YWRtaW46YWRtaW4=" --header "X-Requested-By: PIVOTAL"
curl -X GET -D - http://${AMBARI1_IP}:8080/api/v1/clusters/mycluster1/requests/1 --header "Authorization:Basic YWRtaW46YWRtaW4=" --header "X-Requested-By: PIVOTAL"
```

