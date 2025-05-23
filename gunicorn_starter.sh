#!/bin/sh

#This is NOT BEING USED in PRODUCTION. We are using systemd to start the app on every server restart.

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

# Here we will be spinning up multiple threads with multiple worker processess(-w) and perform a binding.
#run this from inside pdfparser.

gunicorn wsgi:app -w 2 --threads 4 -b 0.0.0.0:5000 --daemon --log-level info