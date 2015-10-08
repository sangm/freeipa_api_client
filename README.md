# Library for interacting with FreeIPA JSON api

## List of available classes (explain purpose/why)
+ ipaAuth
+ ipaPassword
+ ipaClient

## List of environment variables
+ FREEIPA_API_LOG_PATH. Path to any error for the api. Defaults to /tmp/freeipa_api_logs

## To run tests
+ run `export PYTHONPATH='.'` to include current project into pythonpath 
+ Get all the dependencies in the following section

## Installing dependencies
+ [Install virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
+ `virtualenv env`
+ `. ./env/bin/activate` to be sandboxed into a virtual environment
+ `pip install -r requirements.txt`

## Things left to do
+ TODO Logging unexpected error to a log file in ipaAuth
+ TODO Compare time stamps in ipaClient
+ TODO Optional read values from environment variables
+ TODO Support configuration files
+ TODO make this available in pip

## Resources
+ https://vda.li/en/posts/2015/05/28/talking-to-freeipa-api-with-sessions/