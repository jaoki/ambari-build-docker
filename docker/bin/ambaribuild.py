#!/usr/bin/python
# coding: utf-8

import subprocess, time, sys
import json
from optparse import OptionParser

SKIP_TEST="-DskipTests"
AMBARI_AUTH_HEADERS = "--header 'Authorization:Basic YWRtaW46YWRtaW4=' --header 'X-Requested-By: PIVOTAL'"
AMBARI_BUILD_DOCKER_ROOT = "/tmp/ambari-build-docker"

def gitDeepCleaning():
	proc = subprocess.Popen("git clean -xdf",
			shell=True,
			cwd="/tmp/ambari")
	proc.wait()

def ambariUnitTest():
	gitDeepCleaning()
	proc = subprocess.Popen("mvn -fae clean install",
			shell=True,
			cwd="/tmp/ambari")
	return proc.wait()

def buildAmbari(stackDistribution):
	gitDeepCleaning()
	stackDistributionParam = ""
	if stackDistribution is not None:
		stackDistributionParam = "-Dstack.distribution=" + stackDistribution
	proc = subprocess.Popen("mvn -B clean install package rpm:rpm -Dmaven.clover.skip=true -Dfindbugs.skip=true "
						+ SKIP_TEST + " "
						+ stackDistributionParam + " -Dpython.ver=\"python >= 2.6\" -Preplaceurl",
			shell=True,
			cwd="/tmp/ambari")
	return proc.wait()

def installAmbariServer():
	proc = subprocess.Popen("sudo yum install -y ambari-server-*.noarch.rpm",
			shell=True,
			cwd="/tmp/ambari/ambari-server/target/rpm/ambari-server/RPMS/noarch")
	proc.wait()

def installAmbariAgent():
	proc = subprocess.Popen("sudo yum install -y ambari-agent-*.x86_64.rpm",
			shell=True,
			cwd="/tmp/ambari/ambari-agent/target/rpm/ambari-agent/RPMS/x86_64")
	proc.wait()

def startNtpdService():
	proc = subprocess.Popen("sudo service ntpd start",
			shell=True)
	proc.wait()

def setupAmbariServer():
	proc = subprocess.Popen("echo -e '\n\n\n\n' | sudo ambari-server setup",
			shell=True)
	proc.wait()

def startAmbariServer(debug=False):
	proc = subprocess.Popen("sudo ambari-server start" + (" --debug" if debug else ""),
			shell=True)
	proc.wait()

def startSshdService():
	proc = subprocess.Popen("sudo service sshd start",
			shell=True)
	proc.wait()

def configureAmbariAgent():
	proc = subprocess.Popen("hostname -f", stdout=subprocess.PIPE, shell=True)
	hostname = proc.stdout.read().rstrip()
	proc = subprocess.Popen("sudo sed -i 's/hostname=localhost/hostname=" + hostname + "/g' /etc/ambari-agent/conf/ambari-agent.ini",
			shell=True)
	proc.wait()

def startAmbariAgent(waitUntilRegistered = True):
	proc = subprocess.Popen("service ambari-agent start",
			shell=True)
	proc.wait()
	if waitUntilRegistered:
		waitUntilAmbariAgentRegistered()
	
def waitUntilAmbariAgentRegistered():
	count = 0
	while count < 20:
		count += 1
		proc = subprocess.Popen("curl " +
				"http://localhost:8080/api/v1/hosts " +
				AMBARI_AUTH_HEADERS,
				stdout=subprocess.PIPE,
				shell=True)
		hostsResultString = proc.stdout.read()
		hostsResultJson = json.loads(hostsResultString)
		if len(hostsResultJson["items"]) != 0:
			break
		time.sleep(5)

def postBlueprint():
	proc = subprocess.Popen("curl -X POST -D - " +
			"-d @single-node-HDP-2.1-blueprint1.json http://localhost:8080/api/v1/blueprints/myblueprint1 " +
			AMBARI_AUTH_HEADERS ,
			cwd=AMBARI_BUILD_DOCKER_ROOT + "/blueprints",
			shell=True)
	proc.wait()

def createCluster():
	proc = subprocess.Popen("curl -X POST -D - " +
			"-d @single-node-hostmapping1.json http://localhost:8080/api/v1/clusters/mycluster1 " +
			AMBARI_AUTH_HEADERS ,
			cwd=AMBARI_BUILD_DOCKER_ROOT + "/blueprints",
			shell=True)
	proc.wait()

# Loop to not to exit Docker container
def noExit():
	print "loop to not to exit docker container..."
	while True:
		time.sleep(60)

class ParseResult:
	isRebuild = False
	stackDistribution = None
	isTest = False
	isInstallServer = False
	isInstallAgent = False
	isDeploy = False

def parse(argv):
	result = ParseResult()
	if len(argv) >=2:
		parser = OptionParser()
		parser.add_option("-b", "--rebuild", dest="isRebuild", action="store_true", default=False)
		parser.add_option("-s", "--stackDistribution", dest="stackDistribution")
		(options, args) = parser.parse_args(argv[1:])
		if options.isRebuild:
			result.isRebuild = True
		if options.stackDistribution:
			result.stackDistribution = options.stackDistribution

	if argv[0] == "test":
		result.isTest = True

	if argv[0] == "server":
		result.isInstallServer = True

	if argv[0] == "agent":
		result.isInstallServer = True
		result.isInstallAgent = True

	if argv[0] == "deploy":
		result.isInstallServer = True
		result.isInstallAgent = True
		result.isDeploy = True

	return result


# TODO move this to a proper location
def unittest():
	# parse
	result = parse(["test"])
	assert result.isTest == True
	assert result.isRebuild == False
	assert result.stackDistribution == None
	assert result.isInstallServer == False
	assert result.isInstallAgent == False
	assert result.isDeploy == False

	result = parse(["server"])
	assert result.isTest == False
	assert result.isRebuild == False
	assert result.stackDistribution == None
	assert result.isInstallServer == True
	assert result.isInstallAgent == False
	assert result.isDeploy == False

	result = parse(["agent"])
	assert result.isTest == False
	assert result.isRebuild == False
	assert result.stackDistribution == None
	assert result.isInstallServer == True
	assert result.isInstallAgent == True
	assert result.isDeploy == False

	result = parse(["agent", "-b"])
	assert result.isTest == False
	assert result.isRebuild == True
	assert result.stackDistribution == None
	assert result.isInstallServer == True
	assert result.isInstallAgent == True
	assert result.isDeploy == False

	result = parse(["deploy"])
	assert result.isTest == False
	assert result.isRebuild == False
	assert result.stackDistribution == None
	assert result.isInstallServer == True
	assert result.isInstallAgent == True
	assert result.isDeploy == True

	result = parse(["deploy", "-b", "--s=BIGTOP"])
	assert result.isTest == False
	assert result.isRebuild == True
	assert result.stackDistribution == "BIGTOP"
	assert result.isInstallServer == True
	assert result.isInstallAgent == True
	assert result.isDeploy == True

if len(sys.argv) == 1:
	print "specify one of unittest, test, server, agent, deploy"
	sys.exit(1)

if sys.argv[1] == "unittest":
	unittest()
	sys.exit(0)

# test: execute unit test
# server: install ambari-server
#    with or without rebuild
# agent: install ambari-server and ambari-agent
#    with or without rebuild
# deploy: install ambari-server, ambari-agent and deploy Hadoop
#    with or without rebuild

parsedArgv = parse(sys.argv[1:])

if parsedArgv.isTest:
	retcode = ambariUnitTest()
	sys.exit(retcode)

if parsedArgv.isRebuild:
	retcode = buildAmbari(parsedArgv.stackDistribution)
	if retcode != 0:
		sys.exit(retcode)

if parsedArgv.isInstallServer:
	installAmbariServer()
	setupAmbariServer()
	startAmbariServer()
	startSshdService()
	startNtpdService()

if parsedArgv.isInstallAgent:
	installAmbariAgent()
	configureAmbariAgent()
	startAmbariAgent()

if parsedArgv.isDeploy:
	postBlueprint()
	createCluster()

noExit()

