from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError
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

    def __init__(self, app, domain, region, additional_scopes=None):
        super(CognitoOAuth, self).__init__(app)
        cognito_bp = make_cognito_blueprint(
            domain=domain,
            region=region,
            scope=[
                "openid",
                "email",
                "profile",
            ]
            + (additional_scopes if additional_scopes else []),
        )
        app.server.register_blueprint(cognito_bp, url_prefix="/login")

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
