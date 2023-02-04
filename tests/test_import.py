"""
Test Dash Cognito Auth.
"""

import pytest

from dash_cognito_auth import CognitoOAuth

from dash import Dash
from flask import Flask


@pytest.fixture
def app(name='dask'):
    """Dash App."""

    return Dash(name, server=Flask(name),
                url_base_pathname='/')


def test_init(app):
    """Test initialisation."""

    auth = CognitoOAuth(app, domain='test', region='eu-west-1')

    assert auth.app is app
