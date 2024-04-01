from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask.globals import LocalProxy
from flask import g


__maintainer__ = "Frank Spijkerman <frank@jeito.nl>"


def make_cognito_blueprint(
    client_id=None,
    client_secret=None,
    scope=None,
    redirect_url=None,
    redirect_to=None,
    login_url=None,
    authorized_url=None,
    session_class=None,
    storage=None,
    domain=None,
    region=None,
):
    """
    Make a blueprint for authenticating with Cognito using OAuth 2. This requires
    a client ID and client secret from Cognito. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables :envvar:`COGNITO_OAUTH_CLIENT_ID` and
    :envvar:`COGNITO_OAUTH_CLIENT_SECRET`.

    Args:
        client_id (str): The client ID for your application on Cognito.
        client_secret (str): The client secret for your application on Cognito
        scope (str, optional): comma-separated list of scopes for the OAuth token
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/cognito``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/cognito/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth2Session`.
        storage: A token storage class, or an instance of a token storage
                class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.storage.session.SessionStorage`.
        domain (str): The domain configured in Cognito
        region (str): The region of AWS

    :rtype: :class:`~flask_dance.consumer.OAuth2ConsumerBlueprint`
    :returns: A :ref:`blueprint <flask:blueprints>` to attach to your Flask app.
    """

    # There are more sophisticated checks, but for our purposes it should
    # strike a balance between accuracy and readability. The value of domain
    # is either just a prefix in Cognito or a FQDN.
    custom_domain = "." in domain

    if not custom_domain and region is None:
        raise ValueError("The region parameter must be set if 'domain' is not a FQDN.")

    hostname = (
        f"{domain}.auth.{region}.amazoncognito.com" if region is not None else domain
    )

    scope = scope or ["openid", "email", "phone", "profile"]
    cognito_bp = OAuth2ConsumerBlueprint(
        "cognito",
        __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        base_url=f"https://{hostname}",
        authorization_url=f"https://{hostname}/oauth2/authorize",
        token_url=f"https://{hostname}/oauth2/token",
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        storage=storage,
    )
    cognito_bp.from_config["client_id"] = "COGNITO_OAUTH_CLIENT_ID"
    cognito_bp.from_config["client_secret"] = "COGNITO_OAUTH_CLIENT_SECRET"

    @cognito_bp.before_app_request
    def set_applocal_session():
        g.cognito_oauth = cognito_bp.session

    return cognito_bp


cognito = LocalProxy(lambda: g.cognito_oauth)
