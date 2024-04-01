"""
Test Dash Cognito Auth.
"""

import pytest
from dash_cognito_auth import CognitoOAuth


def test_init(app):
    """Test initialisation."""

    auth = CognitoOAuth(app, domain="test", region="eu-west-1")

    assert auth.app is app


def test_that_init_raises_an_exception_if_cognito_domain_and_region_is_missing(app):
    """
    Initializing the app with a Cognito Domain (non-FQDN) and no Region should
    raise a ValueError.
    """

    # Arrange

    # Act + Assert
    with pytest.raises(ValueError):
        CognitoOAuth(app, "non-fqdn")
