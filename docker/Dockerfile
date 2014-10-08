FROM centos:centos6

RUN echo root:changeme | chpasswd

## Install some basic utilities that aren't in the default image
RUN yum -y install vim wget rpm-build sudo which telnet tar openssh-server openssh-clients ntp git python-setuptools
RUN rpm -e --nodeps --justdb glibc-common
RUN yum -y install glibc-common

ENV HOME /root

#Install JAVA
RUN wget --no-check-certificate --no-cookies --header "Cookie:oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/7u55-b13/jdk-7u55-linux-x64.rpm -O jdk-7u55-linux-x64.rpm
RUN yum -y install jdk-7u55-linux-x64.rpm
ENV JAVA_HOME /usr/java/default/

#Install Maven
RUN mkdir -p /opt/maven
WORKDIR /opt/maven
RUN wget http://apache.cs.utah.edu/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
RUN tar -xvzf /opt/maven/apache-maven-3.0.5-bin.tar.gz
RUN rm -rf /opt/maven/apache-maven-3.0.5-bin.tar.gz

ENV M2_HOME /opt/maven/apache-maven-3.0.5
ENV MAVEN_OPTS -Xmx2048m -XX:MaxPermSize=256m
ENV PATH $PATH:$JAVA_HOME/bin:$M2_HOME/bin


# SSH key
RUN ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ''
RUN cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys
RUN sed -ri 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config

# Install python, nodejs and npm
RUN yum -y install http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
RUN yum -y install nodejs npm --enablerepo=epel
RUN npm install -g brunch@1.7.13

# Once run some mvn commands to cache .m2/repository
WORKDIR /tmp
RUN git clone https://github.com/apache/ambari.git
WORKDIR /tmp/ambari
RUN mvn versions:set -DnewVersion=1.6.1.0
RUN mvn -B clean install package rpm:rpm -DskipTests -DnewVersion=1.6.1.0 -Dpython.ver="python >= 2.6" -Preplaceurl

# also build ambari-log4j and install
WORKDIR /tmp/ambari/contrib/ambari-log4j
RUN mvn package rpm:rpm
RUN yum install -y  target/rpm/ambari-log4j/RPMS/noarch/ambari-log4j-1.2.1-*.noarch.rpm

# clean git code because I want to use the one on local filesystem.
WORKDIR /tmp
RUN rm -rf /tmp/ambari

RUN mkdir -p /tmp/ambari-build-docker
ADD . /tmp/ambari-build-docker

# RUN mkdir -p /tmp/ambari-build-docker/blueprints
# ADD ./blueprints/single-node-HDP-2.1-blueprint1.json /tmp/ambari-build-docker/blueprints
# ADD ./blueprints/single-node-hostmapping1.json /tmp/ambari-build-docker/blueprints

WORKDIR /tmp

