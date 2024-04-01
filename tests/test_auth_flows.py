"""
Test the various auth flows and ensure that authentication happens.
"""

from http import HTTPStatus
from urllib.parse import parse_qs, urlparse


from flask import Flask

from dash_cognito_auth.cognito_oauth import CognitoOAuth


def test_that_a_redirect_to_cognito_handler_happens_if_not_logged_in(
    app_with_auth: CognitoOAuth,
):
    """
    If we're not logged in, an unauthenticated request should result in a redirect
    to the local cognito endpoint.
    """

    # Arrange
    flask_server: Flask = app_with_auth.app.server
    client = flask_server.test_client()

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == "/login/cognito"


def test_that_a_redirect_to_cognito_handler_happens_if_not_logged_in_with_url_prefix(
    prefixed_app_with_auth: CognitoOAuth,
):
    """
    If we're not logged in, an unauthenticated request should result in a redirect
    to the local cognito endpoint. This should respect any url_base_pathname settings.
    """

    # Arrange
    flask_server: Flask = prefixed_app_with_auth.app.server
    client = flask_server.test_client()

    # Act
    response = client.get("/some/prefix/")

    # Assert
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == "/some/prefix/login/cognito"


def test_that_cognito_handler_redirects_to_user_pool_if_not_authenticated(
    app_with_auth: CognitoOAuth,
):
    """
    If we're not logged in, the Cognito handler should redirect the request to the
    Cognito User pool so the client can login an retrieve a JWT.

    We test that all the required scopes etc. are present in the redirect uri
    and it's formed according to the expected pattern.
    """

    # Arrange
    flask_server: Flask = app_with_auth.app.server
    client = flask_server.test_client()

    # Act
    response = client.get("/login/cognito")

    # Assert
    assert response.status_code == HTTPStatus.FOUND, "We expect a redirect"

    redirect_url = response.headers.get("Location")
    parsed = urlparse(redirect_url)

    assert parsed.scheme == "https"
    assert (
        parsed.hostname == "test.auth.eu-central-1.amazoncognito.com"
    )  # Domain name + region
    assert parsed.path == "/oauth2/authorize"

    parsed_qs = parse_qs(parsed.query, strict_parsing=True)
    assert "openid" in parsed_qs["scope"][0]
    assert "email" in parsed_qs["scope"][0]
    assert "profile" in parsed_qs["scope"][0]

    assert parsed_qs["response_type"][0] == "code"
    assert parsed_qs["redirect_uri"][0] == "http://localhost/login/cognito/authorized"
    assert parsed_qs["client_id"][0] == "testclient"
    assert "state" in parsed_qs


def test_that_cognito_authorized_response_is_accepted(authorized_app: CognitoOAuth):
    """
    After we authenticate, Cognito redirects us to the /login/cognito/authorized
    endpoint. Here we test that this redirects us to the login page after the
    codes are verified (this is bypassed and left to the end-to-end test).
    """

    # Arrange
    flask_server: Flask = authorized_app.app.server
    client = flask_server.test_client()

    cognito_redirect_target = (
        "/login/cognito/authorized?code=1e4aa08d-d969-4264-a835-c1b2757b9163"
        "&state=vSBCqedXdyXQAOcr"
    )

    # Act
    response = client.get(cognito_redirect_target, follow_redirects=False)

    # Assert
    assert response.status_code == HTTPStatus.FOUND
    assert (
        response.headers.get("Location") == "/"
    ), "Should redirect to root after authorization"


def test_that_cognito_handler_redirects_to_user_pool_with_custom_domain(
    app_with_auth_and_cognito_custom_domain: CognitoOAuth,
):
    """
    If we're not logged in, the Cognito handler should redirect the request to the
    Cognito User pool so the client can login an retrieve a JWT.

    We test that all the required scopes etc. are present in the redirect uri
    and it's formed according to the expected pattern.
    In this scenario, we additionally ensure that a custom domain works, in our case
    it should be authentication.example.com
    """

    # Arrange
    flask_server: Flask = app_with_auth_and_cognito_custom_domain.app.server
    client = flask_server.test_client()

    # Act
    response = client.get("/login/cognito")

    # Assert
    assert response.status_code == HTTPStatus.FOUND, "We expect a redirect"

    redirect_url = response.headers.get("Location")
    parsed = urlparse(redirect_url)

    assert parsed.scheme == "https"
    assert parsed.hostname == "authentication.example.com"  # Custom Domain Name
    assert parsed.path == "/oauth2/authorize"

    parsed_qs = parse_qs(parsed.query, strict_parsing=True)
    assert "openid" in parsed_qs["scope"][0]
    assert "email" in parsed_qs["scope"][0]
    assert "profile" in parsed_qs["scope"][0]

    assert parsed_qs["response_type"][0] == "code"
    assert parsed_qs["redirect_uri"][0] == "http://localhost/login/cognito/authorized"
    assert parsed_qs["client_id"][0] == "testclient"
    assert "state" in parsed_qs
