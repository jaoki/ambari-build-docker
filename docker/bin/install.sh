#!/bin/bash


cd /tmp/ambari

mvn -B clean install package rpm:rpm -Dmaven.clover.skip=true -Dfindbugs.skip=true -DskipTests -Dpython.ver="python >= 2.6" -Preplaceurl

sudo yum install -y ambari-server/target/rpm/ambari-server/RPMS/noarch/ambari-server-*.noarch.rpm ambari-agent/target/rpm/ambari-agent/RPMS/x86_64/ambari-agent-*.x86_64.rpm

cd /tmp

sudo service ntpd start
echo -e '\n\n\n\n' | sudo ambari-server setup
sudo ambari-server start # or --debug

sudo service sshd start
sudo sed -i "s/hostname=localhost/hostname=$(hostname -f)/g" /etc/ambari-agent/conf/ambari-agent.ini && service ambari-agent start

# keep container running
tail -f /tmp/ambari-build-docker/bin/install.sh

