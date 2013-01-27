#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import shlex
import glob
import os
import errno
import shutil
import getopt
import sys
from string import rsplit

def package_version(version):
    return version.replace("_", "-")

def rm(path):
    try:
        os.remove(path)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            pass
        else: raise

def rmdir(path):
    try:
        shutil.rmtree(path)
    except OSError as exc:
        if exc.errno == errno.ENOENT or exc.errno == errno.ENOTEMPTY :
            pass
        else: raise

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def exe(cmdline):
    process = subprocess.Popen(shlex.split(cmdline), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = process.communicate()
    return stdout, stderr

def cleanup():
    print "Cleaning "
    # subprocess doesn't eat wildcards, glob it up
    arg=shlex.split("rm -f "+origdir+'/kafka*.deb')
    exe(' '.join(arg[:-1] + glob.glob(arg[-1])))
    arg=shlex.split("rm -f kafka*.tgz")
    exe(' '.join(arg[:-1] + glob.glob(arg[-1])))
    rmdir(workdir)

def fetch_kafka():
    print "Downloading ", DOWNLOAD_URL
    exe('wget '+DOWNLOAD_URL)
    print DOWNLOAD_URL
    tgz=rsplit(DOWNLOAD_URL, "/", 1)[1]
    print "Unpacking ", tgz
    exe('tar -zxvf '+tgz)
    global KAFKA_SRC
    KAFKA_SRC = rsplit(tgz, ".tgz", 1)[0]

def prepare_work_area():
    print "Creating work dir ", workdir
    mkdir_p(workdir)

def prepare_deb_structure():
    print "Preparing .deb file structure under ",workdir
    mkdir_p('%s/build/etc/init.d'%(workdir,))
    mkdir_p('%s/build/etc/security/limits.d'%(workdir,))
    mkdir_p('%s/build/etc/sysconfig'%(workdir,))
    mkdir_p('%s/build/etc/kafka'%(workdir,))
    mkdir_p('%s/build/usr/lib'%(workdir,))
    mkdir_p('%s/build/var/log/kafka'%(workdir,))

def add_base_files():
    print "Copying files into .deb work area "
    exe('cp kafka-server %s/build/etc/init.d' %(workdir,))
    exe('cp kafka-nofiles.conf %s/build/etc/security/limits.d' %(workdir,))
    exe('cp kafka %s/build/etc/sysconfig' %(workdir,))
    exe('cp preinst %s' %(workdir,))
    exe('cp postinst %s' %(workdir,))
    exe('cp log4j.properties %s/build/etc/kafka' %(workdir,))
    exe('cp %s/%s/config/server.properties %s/build/etc/kafka' %(workdir, KAFKA_SRC, workdir))
    exe('cp %s/%s/config/consumer.properties %s/build/etc/kafka' %(workdir, KAFKA_SRC, workdir))
    exe('cp %s/%s/config/producer.properties %s/build/etc/kafka' %(workdir, KAFKA_SRC, workdir))
    exe('cp %s/%s/config/zookeeper.properties %s/build/etc/kafka' %(workdir, KAFKA_SRC, workdir))

def build_kafka():
    print "Updating Kafka "
    os.system('./sbt update')
    print "Building Kafka "
    os.system('./sbt package')

def add_kafka_build():
    print "Copying Kafka build to ", workdir
    # not very surgical
    shutil.copytree(os.getcwd(), '%s/%s/build/usr/lib/kafka/'% (origdir, workdir))

def set_the_server_data_path():
    with open(os.path.join('%s/%s/build/etc/kafka'%(origdir, workdir,), 'server.properties'), 'r') as f:
        properties = f.read()

    properties = properties.replace('/tmp/kafka-logs', '/var/lib/kafka/data/kafka-logs')

    with open(os.path.join('%s/%s/build/etc/kafka'%(origdir, workdir,), 'server.properties'), 'w') as f:
        f.write(properties)

def create_an_deb():
    print "Preparing .deb "
    deb_name="kafka"
    deb_package_version=REL_VERSION
    deb_description='Apache Kafka is a distributed publish-subscribe messaging system.'
    deb_url="https://kafka.apache.org/"
    deb_license='Apache Software License 2.0'
    deb_arch="all"
    deb_vendor=VENDOR
    deb_category="misc"
    deb_maker=MAINTAINER
    deb_build_folder='.'
    deb_src='dir'
    deb_user ='kafka'
    deb_group='kafka'
    deb_preinst='../preinst'
    deb_postinst='../postinst'
    deb_prefix='/'
    deb_version="%s-%s"%(PKG_VERSION,deb_package_version)
    cmd_raw="""fpm \
--verbose \
-t deb \
-n %s  \
-v %s  \
--description "%s" \
--url="%s" \
-a %s \
--category %s \
--vendor "%s" \
--license "%s" \
-m "%s"  \
--prefix=%s \
-s %s \
--rpm-user %s \
--rpm-group %s \
--before-install %s \
--after-install %s \
--config-files /etc/init.d/kafka-server \
--config-files /etc/kafka/server.properties  \
--config-files /etc/kafka/producer.properties \
--config-files /etc/kafka/zookeeper.properties \
--config-files /etc/kafka/consumer.properties \
--config-files /etc/kafka/log4j.properties \
--config-files /etc/security/limits.d/kafka-nofiles.conf \
--config-files /etc/sysconfig/kafka \
-- %s"""

    cmd = cmd_raw %(
        deb_name,
        deb_version,
        deb_description,
        deb_url,
        deb_arch,
        deb_category,
        deb_vendor,
        deb_license,
        deb_maker,
        deb_prefix,
        deb_src,
        deb_user,
        deb_group,
        deb_preinst,
        deb_postinst,
        deb_build_folder
        ,)
    os.system(cmd)
    shutil.move("%s_%s_%s.deb"%(deb_name, deb_version, deb_arch), origdir)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def usage():
    print "\nBuild an FPM .deb for Kafka\n"
    print 'Usage:\n\n '+sys.argv[0]+' [OPTIONS]'
    print '\nOptions:\n'
    print ' REQUIRED [-r, --release] <kafka version>  create a deb named as this version\n'
    print ' REQUIRED [-l, --link] <kafka url>  download and unpack source release (assumes a tgz that unpacks to "kafka")\n'
    print ' REQUIRED [-m, --maintainer] <package>  package maintainer\n'
    print ' REQUIRED [-v, --vendor] <vendor>  package vendor\n'
    print ' OPTIONAL [-p, --package-release] <relase version>  package release version (default is 1)\n'

def main(argv=None):
    global RELEASE_VERSION
    global PKG_VERSION
    global REL_VERSION
    global MAINTAINER
    global DOWNLOAD_URL
    global VENDOR
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "r:l:h:p:m:v", ["release", "link", "help", "package-release", "maintainer", "vendor"])
            for o, a in opts:
                if o in ("--help"):
                    usage()
                    sys.exit()
                elif o in ("-r", "--release"):
                    RELEASE_VERSION = a
                    PKG_VERSION=package_version(a)
                elif o in ("-l", "--link"):
                    DOWNLOAD_URL = a
                elif o in ("-p", "--package-release"):
                    REL_VERSION = a
                elif o in ("-m", "--maintainer"):
                    MAINTAINER = a
                elif o in ("-v", "--vendor"):
                    VENDOR = a
        except getopt.error, msg:
            raise Usage(msg)
        cleanup()
        prepare_work_area()
        prepare_deb_structure()
        os.chdir('%s/%s'%(origdir,workdir))
        fetch_kafka()
        os.chdir(origdir)
        add_base_files()
        os.chdir('%s/%s/%s'%(origdir,workdir,KAFKA_SRC))
        build_kafka()
        add_kafka_build()
        os.chdir(origdir)
        os.chdir('%s/%s/build'%(origdir,workdir))
        set_the_server_data_path()
        create_an_deb()
        os.chdir(origdir)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


RELEASE_VERSION=None
PKG_VERSION=None
DOWNLOAD_URL=None
REL_VERSION="1"
MAINTAINER = None
VENDOR=None
KAFKA_SRC=None

workdir='out'
origdir = os.getcwd()

if __name__ == "__main__":
    sys.exit(main())