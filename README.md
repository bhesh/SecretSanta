# Secret Santa Web Service

Simple website that offers the ability to create and manage secret santa groups. 
This was originally built for my family to partake in Secret Santa easily from 
different locations with no single person aware of any other person's target.

## Dependencies

apache2 (httpd)
python3
python3-cgi
libapache2-wsgi-py3

Modssl and rewrite must be enabled in apache2.

## Installation

`# bash install.sh`

This installs the files to /var/www

## Further Development

Currently, it uses SQL-lite because it was simple. I plan to move this to 
a PostgreSQL service.

The page building is very inelegant--the process should be reworked.

The authorization process is basic and essentially hard-coded. It would be 
fun to implement an IDP of sorts to allow flexible RBAC policy decision making.

## License

(c) 2019 - Brian Hession

