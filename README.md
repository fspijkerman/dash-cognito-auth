# Dash Cognito Auth

![Build + Test](https://github.com/fspijkerman/dash-cognito-auth/actions/workflows/build.yml/badge.svg) [![PyPI version](https://badge.fury.io/py/dash-cognito-auth.svg)](https://pypi.org/project/dash-cognito-auth/)

Dash Cognito Auth is a simple library using Cognito OAuth to authenticate and
view a [Dash](https://dash.plot.ly/) app.

This Library uses [Flask Dance](https://github.com/singingwolfboy/flask-dance)
and a modified version of Plotly's own [dash auth](https://github.com/plotly/dash-auth)
for authentication.

This Library is heavily inspired by [dash-google-oauth](https://github.com/lchapo/dash-google-auth) created by Lucas Chapin

## Basic Use

Authentication can be added to your Dash application using the `CognitoOAuth`
class, i.e.

```python
from dash import Dash
from flask import Flask
from dash_cognito_auth import CognitoOAuth

server = Flask(__name__)
server.config.update({
  'COGNITO_OAUTH_CLIENT_ID': ...,
  'COGNITO_OAUTH_CLIENT_SECRET': ...,
})

app = Dash(__name__, server=server, url_base_pathname="/")

additional_scopes = [...]
auth = CognitoOAuth(
   app,
   domain='mydomain',
   region='eu-west-1',
   additional_scopes,
   logout_url="/logout"
)

# your Dash app here :)
...
```

## Example

This repository contains a simple [Example App](example/) that demonstrates how to add Cognito authentication to your Dash app as well as the Login and Logout Flows.

## Development

- Check out the repository
- Run `pip install -r requirements.txt` to install the package
- Run `pip install -r requirements-dev.txt` to install additional dependencies for running the tests
- If you want to run the [Sample App](example/) or the end to end tests, it makes sense to deploy the [Cloudformation Template](example/aws_resources.yaml) in order to get a functioning User Pool + App Client
- Run the tests locally
   - Use `python -m pytest tests --ignore-glob "*end_to_end*"` to exclude the integration / end to end tests that require a [Cognito Setup](#integration-tests)
   - Use `python -m pytest tests` to run all tests


## Integration Tests

There are integration tests against a Cognito User Pool + App Client, if you want to run those - either create a `.env` file with this content or set the environment variables with the same name.

```shell
# Credentials for the user in the user pool
COGNITO_USER_NAME=<username>
COGNITO_EMAIL=<email-that-must-match>
COGNITO_PASSWORD=<password>

# Connection between the app and the user pool
COGNITO_DOMAIN=<just-the-prefix>
COGNITO_REGION=<aws-region-of-the-cognito-userpool>
COGNITO_OAUTH_CLIENT_ID=<app-client-id>
COGNITO_OAUTH_CLIENT_SECRET=<app-client-secret>
```