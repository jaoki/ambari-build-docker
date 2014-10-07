how to build
--------------------

```
sudo docker build -t ambari/build .
```

how to run
--------------------

```
sudo docker run --privileged -t -i -p 5005:5005 -p 8080:8080 -h host1.mydomain.com -v ${AMBARI_SRC:-$(pwd)}:/root/ambari ambari/build bash
# where 5005 is java debug port and 8080 is the default http port, if no --privileged ambari-server start fails due to access to /proc/??/exe
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

echo -e '\n\n\n\n' | sudo ambari-server setup
sudo ambari-server start # or --debug


sudo service sshd start
sudo sed -i "s/hostname=localhost/hostname=$(hostname -f)/g" /etc/ambari-agent/conf/ambari-agent.ini && service ambari-agent start
```

