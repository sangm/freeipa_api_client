# Library for interacting with FreeIPA

## To run tests
+ run `export PYTHONPATH='.'` to include current project into pythonpath 
+ activate virtualenv and install packages by running `pip install -r requirements.txt`

## Installing dependencies
+ [Install virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
+ `virtualenv env`
+ `. ./env/bin/activate` to be sandboxed into a virtual environment
+ `pip install -r requirements.txt`

## Things left to do
+ TODO Logging unexpected error to a log file in ipaAuth
+ TODO Compare time stamps in ipaClient
+ TODO Store passwords in a secure manner

