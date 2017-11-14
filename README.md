Python Flask Swagger Api Demo
==============================

This repository contains boilerplate code for a RESTful API based on Flask and Flask-RESTPlus.

Setting up the demo application

To download and start the demo application issue the following commands. First clone the application code into any directory on your disk:

$ cd /path/to/my/workspace/
$ git clone https://github.com/vianppz/python_swagger_demo.git
$ cd python_swagger_demo
Create a virtualenv called venv in the application directory, activate the virtualenv and install required dependencies using pip:

$ pyvenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
Make sure the current working directory is on your PYTHONPATH and start the app:

$ export PYTHONPATH=.:$PYTHONPATH
$ python python_swagger_demo/app.py
Now everything should be ready. In your browser, open the URL http://localhost:8888/api/

Next Oauth2 Client...