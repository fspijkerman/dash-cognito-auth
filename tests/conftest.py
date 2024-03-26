from unittest.mock import patch

import pytest

from dash import Dash, html
from dotenv import load_dotenv
from flask import Flask, redirect

from dash_cognito_auth import CognitoOAuth

load_dotenv()


@pytest.fixture
def app(name="dash") -> Dash:
    """
    Dash App that has only one H1 Tag with the value "Hello World".
    It uses a Flask server with the secret key just_a_test.
    """

    dash_app = Dash(name, server=Flask(name), url_base_pathname="/")
    dash_app.layout = html.H1("Hello World")
    dash_app.server.config.update(
        {
            "TESTING": True,
        }
    )
    dash_app.server.secret_key = "just_a_test"
    return dash_app


@pytest.fixture
def app_with_auth(app) -> CognitoOAuth:
    """
    Dash App wrapped with Cognito Authentication:
    - Domain name: test
    - Region: eu-central-1
    - App Client Id: testclient
    - App Client Secret: testsecret
    """

    auth = CognitoOAuth(app, domain="test", region="eu-central-1")
    auth.app.server.config["COGNITO_OAUTH_CLIENT_ID"] = "testclient"
    auth.app.server.config["COGNITO_OAUTH_CLIENT_SCRET"] = "testsecret"

    return auth


@pytest.fixture
def authorized_app(app) -> CognitoOAuth:
    """
    App with Cognito Based authentication that bypasses the authentication/authorization
    part, i.e. replaced is_authorized and the authorized endpoint.

    Intended for tests that
    """

    def is_authorized_call(_):

        return True

    def authorized_call(_):

        return redirect("/")

    with patch(
        "dash_cognito_auth.cognito_oauth.CognitoOAuth.is_authorized", is_authorized_call
    ), patch(
        "flask_dance.consumer.oauth2.OAuth2ConsumerBlueprint.authorized",
        authorized_call,
    ):

        auth = CognitoOAuth(app, domain="test", region="eu-central-1")
        auth.app.server.config["COGNITO_OAUTH_CLIENT_ID"] = "testclient"
        auth.app.server.config["COGNITO_OAUTH_CLIENT_SCRET"] = "testsecret"

        yield auth
