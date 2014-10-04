how to build
--------------------

```
sudo docker build -t ambari/build build_env/
```

how to run
--------------------

```
sudo docker run -t -i -h host1.mydomain.com -v /home/jaoki/coding/ambari:/root/ambari ambari/build bash
```

how to build ambari
----------------------------

```
mvn -B clean install package rpm:rpm -Dmaven.clover.skip=true -Dfindbugs.skip=true -DskipTests -DnewVersion=1.6.1.0 -Dpython.ver="python >= 2.6" -Preplaceurl

sudo yum install -y ambari-server/target/rpm/ambari-server/RPMS/noarch/ambari-server-*.noarch.rpm
sudo yum install -y ambari-agent/target/rpm/ambari-agent/RPMS/x86_64/ambari-agent-*.x86_64.rpm

echo -e '\n\n\n\n' | sudo ambari-server setup
sudo ambari-server start


sudo service sshd start
sudo sed -i "s/hostname=localhost/hostname=$(hostname -f)/g" /etc/ambari-agent/conf/ambari-agent.ini
sudo service ambari-agent start
```

