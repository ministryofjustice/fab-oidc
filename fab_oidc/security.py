import os

from logging import getLogger

from flask_appbuilder.security.manager import AUTH_OID
from flask_appbuilder.security.sqla.manager import SecurityManager
from authlib.integrations.flask_client import OAuth

from .views import AuthOIDCView

log = getLogger(__name__)

issuer = os.getenv('ISSUER', 'https://keycloak.k8s.eltoro.com/auth/realms/keycloak')
clientId = os.getenv('CLIENT_ID', 'flask-webapp')
clientSecret = os.getenv('CLIENT_SECRET', 'lkkoQDUdJUqYDHXZBVDodw2ocvqJEflP')
oidcDiscoveryUrl = f'{issuer}/.well-known/openid-configuration'

class OIDCSecurityManagerMixin:
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        if self.auth_type == AUTH_OID:
            self.oid = OAuth(self.appbuilder.get_app)
            self.oid.register(
                name='keycloak',
                client_id=clientId,
                client_secret=clientSecret,
                server_metadata_url=oidcDiscoveryUrl,
                client_kwargs={
                    'scope': 'openid email profile',
                    'code_challenge_method': 'S256'  # enable PKCE
                },
            )
            self.authoidview = AuthOIDCView


class OIDCSecurityManager(OIDCSecurityManagerMixin, SecurityManager):
    pass


try:
    from airflow.www.security import AirflowSecurityManager


    class AirflowOIDCSecurityManager(OIDCSecurityManagerMixin, AirflowSecurityManager):
        pass


except ImportError:
    log.debug("Airflow 2 not installed")

    try:
        from airflow.www_rbac.security import AirflowSecurityManager


        class AirflowOIDCSecurityManager(
            OIDCSecurityManagerMixin, AirflowSecurityManager
        ):
            pass

    except ImportError:
        log.debug("Airflow 1 not installed")

try:
    from superset.security import SupersetSecurityManager


    class SupersetOIDCSecurityManager(
        OIDCSecurityManagerMixin, SupersetSecurityManager
    ):
        pass


except ImportError:
    log.debug("Superset not installed")
