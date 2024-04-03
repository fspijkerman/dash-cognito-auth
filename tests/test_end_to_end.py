"""
Integration test that authenticates against a real user pool.

Naturally these are a bit sensitive to the way the Cognito UI is implemented.
"""

# pylint: disable=W0621

import os

from http import HTTPStatus

import requests
import pytest

from bs4 import BeautifulSoup
from dash import Dash, html
from flask import Flask, session

from dash_cognito_auth import CognitoOAuth

# For our end to end test we don't have HTTPS
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@pytest.fixture
def end_to_end_app() -> CognitoOAuth:
    """
    Small dash app that's wrapped with the CognitoOAuth and offers a /session-info
    endpoint which returns the currently logged in user.
    """

    name = "end-to-end"

    dash_app = Dash(name, server=Flask(name), url_base_pathname="/")
    dash_app.layout = html.H1("Hello World")
    dash_app.server.config.update(
        {
            "TESTING": True,
        }
    )
    dash_app.server.secret_key = "just_a_test"

    auth = CognitoOAuth(
        dash_app,
        domain=os.environ["COGNITO_DOMAIN"],
        region=os.environ["COGNITO_REGION"],
        logout_url="logout",
    )
    auth.app.server.config["COGNITO_OAUTH_CLIENT_ID"] = os.environ[
        "COGNITO_OAUTH_CLIENT_ID"
    ]
    auth.app.server.config["COGNITO_OAUTH_CLIENT_SECRET"] = os.environ[
        "COGNITO_OAUTH_CLIENT_SECRET"
    ]

    @dash_app.server.route("/session-info")
    def session_info():
        return {"email": session["email"]}

    return auth


def test_end_to_end(end_to_end_app: CognitoOAuth):
    """
    - Request the local webapp
    - Follow the redirect to the local authorization endpoint
    - Follow the redirect to the Cognito UI
    - Parse the Cognito UI
    - Log in to Cognito
    - Follow the redirect to the authorization endpoint
    - Follow the redirect to the app home page (logged in)
    - Check the /session-info endpoint to verify the correct user is logged in
    - Call the /logout endpoint to end the current session
    - Check a call to the homepage redirects us to the local cognito endpoint
    """

    # Arrange
    server: Flask = end_to_end_app.app.server
    client = server.test_client()
    s = requests.session()

    # Act + Assert

    # We're not authenticated, we should be redirected to the local cognito endpoint.
    redirect_to_local_cognito = client.get("/")

    # Redirect to the Cognito Login UI
    redirect_to_cognito_ui = client.get(redirect_to_local_cognito.location)

    # Get Cognito Login page, extract tokens
    cognito_login_ui = s.get(redirect_to_cognito_ui.location, timeout=5)
    ui_soup = BeautifulSoup(cognito_login_ui.text, features="html.parser")

    ui_soup.select_one('input[name="_csrf"]')
    csrf_token = ui_soup.select_one('input[name="_csrf"]')["value"]
    cognito_asf_data = ui_soup.select_one('input[name="cognitoAsfData"]')
    login_url = (
        redirect_to_cognito_ui.location.split(".com/")[0]
        + ".com"
        + ui_soup.select_one('form[name="cognitoSignInForm"]')["action"]
    )

    # Login and catch redirect response
    login_response = s.post(
        url=login_url,
        data={
            "_csrf": csrf_token,
            "username": os.environ["COGNITO_USER_NAME"],
            "password": os.environ["COGNITO_PASSWORD"],
            "cognitoAsfData": cognito_asf_data,
        },
        timeout=5,
        allow_redirects=False,
    )

    # Use Cognito tokens to log in
    post_cognito_auth_redirect = client.get(login_response.headers["location"])

    # We should now be redirected to the home page which will be displayed
    home_page_with_auth = client.get(post_cognito_auth_redirect.location)
    assert home_page_with_auth.status_code == HTTPStatus.OK

    # Verify that the logged in users' email matches the one from the env
    session_info_response = client.get("/session-info")
    assert session_info_response.json["email"] == os.environ["COGNITO_EMAIL"]

    # Log out
    logout_response = client.get("/logout")
    assert logout_response.status_code == HTTPStatus.FOUND
    assert "/logout" in logout_response.location

    # Since we're not longer logged in, we should be redirected to the local
    # Cognito endpoint.
    homepage_response = client.get("/")
    assert homepage_response.status_code == HTTPStatus.FOUND
    assert homepage_response.location == "/login/cognito"
