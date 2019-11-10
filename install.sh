#!/bin/bash

[ $(id -u) -ne 0 ] && echo 'Must run as root' && exit 1

DOC_BASE='/var/www/html'

systemctl stop apache2

# Backup database
[ -f $DOC_BASE/private/secretsanta.db ] && cp $DOC_BASE/private/secretsanta.db secretsanta.db.bak

# Remove the current installation
echo rm -rf $DOC_BASE/*

# Make directories
mkdir -p $DOC_BASE/private

# Set prod environment
mv html/env.py{,.test}
mv private/env.py{,.test}
mv html/env.py{.prod,}
mv private/env.py{.prod,}

# Install files
echo cp -vr html/* $DOC_BASE/
echo cp -vr private/* $DOC_BASE/private/

# Restore database
[ -f secretsanta.db.bak ] && cp secretsanta.db.bak $DOC_BASE/private/secretsanta.db

# Restore test environment
mv html/env.py{,.prod}
mv private/env.py{,.prod}
mv html/env.py{.test,}
mv private/env.py{.test,}

systemctl start apache2

