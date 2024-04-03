from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError
from dash import Dash
from flask import (
    redirect,
    url_for,
    Response,
    session,
)
from .cognito import make_cognito_blueprint, cognito

from .auth import Auth


class CognitoOAuth(Auth):
    """
    Wraps a Dash App and adds Cognito based OAuth2 authentication.
    """

    def __init__(self, app: Dash, domain: str, region=None, additional_scopes=None):
        """
        Wrap a Dash App with Cognito authentication.

        The app needs two configuration options to work:

        COGNITO_OAUTH_CLIENT_ID -> Client-ID of the Cognito App Client
        COGNITO_OAUTH_CLIENT_SECRET -> Secret of the Cognito App Client

        Can be set like this:

        app.server.config["COGNITO_OAUTH_CLIENT_ID"] = "something"
        app.server.config["COGNITO_OAUTH_CLIENT_SECRET"] = "something"

        ---

        Parameters
        ----------
        app : Dash
            The app to add authentication to.
        domain : str
            Either the domain prefix of the User Pool domain if hosted by Cognito
            or the FQDN of your custom domain, e.g. authentication.example.com
        region : str, optional
            AWS region of the User Pool. Mandatory if domain is NOT a custom domain, by default None
        additional_scopes : Additional OAuth Scopes to request, optional
            By default openid, email, and profile are requested - default value: None
        """
        super().__init__(app)

        dash_base_path = app.get_relative_path("")

        cognito_bp = make_cognito_blueprint(
            domain=domain,
            region=region,
            redirect_url=dash_base_path,
            scope=[
                "openid",
                "email",
                "profile",
            ]
            + (additional_scopes if additional_scopes else []),
        )

        app.server.register_blueprint(cognito_bp, url_prefix=f"{dash_base_path}/login")

    def is_authorized(self):
        if not cognito.authorized:
            # send to cognito login
            return False

        try:
            resp = cognito.get("/oauth2/userInfo")
            assert resp.ok, resp.text

            session["email"] = resp.json().get("email")
            return True
        except (InvalidGrantError, TokenExpiredError):
            return self.login_request()

    def login_request(self):
        # send to cognito auth page
        return redirect(url_for("cognito.login"))

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                return Response(status=403)

            response = f(*args, **kwargs)
            return response

        return wrap

    def index_auth_wrapper(self, original_index):
        def wrap(*args, **kwargs):
            if self.is_authorized():
                return original_index(*args, **kwargs)
            else:
                return self.login_request()

        return wrap
