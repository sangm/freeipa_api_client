# Library for interacting with FreeIPA JSON api

## List of available classes (explain purpose/why)

#### IPAResponse
small wrapper around the requests that is returned by json api.

+ headers: entire HTTP header returned by json api
+ status_code: HTTP Status Code
+ session: session cookie
+ failure: reason for failure extracted from HTTP headers
+ expiration: expiration date extracted from HTTP headers
+ raw_result: actual result from HTTP request
+ parsed_json: 

#### IPAAuth

```python
from freeipa_api_client import IPAAuth
import requests

a = IPAAuth(requests=requests, baseUrl='https://ipa.example.test')
ipaResponse = a.authenticate('admin', 'Secret123')

ipaResponse.status_code # 200
ipaResponse.session  # session cookie from json api

```

#### IPAPassword
This is needed because FreeIPA was never intended to be used this way.
Any user that is registered will have to reset their password based on their first login attempt.
FreeIPA provides another end point so that the user will not be prompted for another login

[Link to Patch](https://www.redhat.com/archives/freeipa-devel/2012-June/msg00073.html)

#### IPAClient
Used to actually interact with the api. Uses IPAAuth internally.

## Show examples of ipa help commands

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
+ TODO Optional read values from environment variables
+ TODO Support configuration files
+ TODO make this available in pip
+ TODO make sure IPAClient documentation notes json_result is the PARSED result ['result']['result']

## Resources
+ https://vda.li/en/posts/2015/05/28/talking-to-freeipa-api-with-sessions/
