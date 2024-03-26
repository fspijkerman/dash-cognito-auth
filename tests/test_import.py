"""
Test Dash Cognito Auth.
"""

from dash_cognito_auth import CognitoOAuth


def test_init(app):
    """Test initialisation."""

    auth = CognitoOAuth(app, domain="test", region="eu-west-1")

    assert auth.app is app
