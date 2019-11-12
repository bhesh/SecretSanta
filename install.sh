#!/bin/bash

[ $(id -u) -ne 0 ] && echo 'Must run as root' && exit 1

DOC_BASE='/var/www/html'

systemctl stop apache2

# Backup database
[ -f $DOC_BASE/private/secretsanta.db ] && mv -i $DOC_BASE/private/secretsanta.db secretsanta.db.bak

# Remove the current installation
find $DOC_BASE -depth -type f -exec rm {} \;
find $DOC_BASE -depth -type d -exec rmdir {} \;

# Make directories
mkdir -p $DOC_BASE/private

# Set prod environment
mv -v html/env.py{,.test}
mv -v private/env.py{,.test}
mv -v html/env.py{.prod,}
mv -v private/env.py{.prod,}

# Install files
cp -vr html/* $DOC_BASE/
cp -vr private/* $DOC_BASE/private/

# Restore database
[ -f secretsanta.db.bak ] && mv -i secretsanta.db.bak $DOC_BASE/private/secretsanta.db

# Restore test environment
mv -v html/env.py{,.prod}
mv -v private/env.py{,.prod}
mv -v html/env.py{.test,}
mv -v private/env.py{.test,}

# Fix permissions
chown -R www-data:www-data $DOC_BASE/*
find $DOC_BASE -type f -exec chmod 640 {} \;
find $DOC_BASE -name '*.py' -exec chmod 750 {} \;
find $DOC_BASE -type d -exec chmod 750 {} \;
chmod 755 $DOC_BASE

systemctl start apache2

