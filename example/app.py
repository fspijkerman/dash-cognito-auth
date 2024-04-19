import os

from dash import Dash, html, callback, Input, Output
from dotenv import load_dotenv
from flask import session

from dash_cognito_auth import CognitoOAuth

# For localhost we usually don't have TLS certificates
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv()


def build_app() -> Dash:

    app = Dash(name="demo-app")
    app.layout = html.Div(
        [
            html.H1("Welcome...", id="welcome-text"),
            html.A(children="Logout", href="/logout"),
        ]
    )

    app.server.secret_key = "SECRET_VALUE"

    app.server.config["COGNITO_OAUTH_CLIENT_ID"] = os.environ["COGNITO_OAUTH_CLIENT_ID"]
    app.server.config["COGNITO_OAUTH_CLIENT_SECRET"] = os.environ[
        "COGNITO_OAUTH_CLIENT_SECRET"
    ]

    CognitoOAuth(
        app,
        domain=os.environ["COGNITO_DOMAIN"],
        region=os.environ["COGNITO_REGION"],
        logout_url="logout",
    )

    return app


@callback(Output("welcome-text", "children"), Input("welcome-text", "id"))
def _update_welcome_text(_):

    return "Welcome " + session["email"]


if __name__ == "__main__":
    build_app().run_server(host="localhost", debug=True)
