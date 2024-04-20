#!/bin/sh -xe

. /shell-scripts/config-hbase.sh

apt-get update -y

apt-get install $minimal_apt_get_args $HBASE_BUILD_PACKAGES

curl --insecure $HBASE_DIST/$HBASE_VERSION/hbase-$HBASE_VERSION-bin.tar.gz | tar -x -z && mv hbase-${HBASE_VERSION} hbase

cd /hbase

here=$(pwd)

# delete files that are not needed to run hbase
rm -rf docs *.txt LEGAL
rm -f */*.cmd

# Set Java home for hbase servers
sed -i "s,^. export JAVA_HOME.*,export JAVA_HOME=$JAVA_HOME," conf/hbase-env.sh

# Set interactive shell defaults
cat > /etc/profile.d/defaults.sh <<EOF
JAVA_HOME=$JAVA_HOME
export JAVA_HOME
EOF

cd /usr/bin
ln -sf $here/bin/* .

cd /

AUTO_ADDED_PACKAGES=`apt-mark showauto`

apt-get remove --purge -y $HBASE_BUILD_PACKAGES $AUTO_ADDED_PACKAGES

# Install the run-time dependencies
apt-get install $minimal_apt_get_args $HBASE_RUN_PACKAGES

# Setup ssh
service ssh start

# Generate SSH key if not already present
if [ ! -f $HOME/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -N "" -f $HOME/.ssh/id_rsa
fi

# Copy the public key to the authorized_keys file for passwordless SSH
cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

# Set correct permissions for SSH files
chmod 700 $HOME/.ssh
chmod 600 $HOME/.ssh/authorized_keys

rm -rf /tmp/* /var/tmp/*

apt-get clean
rm -rf /var/lib/apt/lists/*