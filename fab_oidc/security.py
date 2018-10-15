from flask_appbuilder.security.manager import AUTH_OID
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_oidc import OpenIDConnect
from .views import AuthOIDCView, SupersetAuthOIDCView
from logging import getLogger
log = getLogger(__name__)

class OIDCSecurityManagerMixin:

    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        if self.auth_type == AUTH_OID:
            self.oid = OpenIDConnect(self.appbuilder.get_app)
            self.authoidview = AuthOIDCView

class OIDCSecurityManager(OIDCSecurityManagerMixin, SecurityManager):
    pass

try:
    from airflow.www_rbac.security import AirflowSecurityManager
    class AirflowOIDCSecurityManager(OIDCSecurityManagerMixin, AirflowSecurityManager):
        pass
except ImportError:
    log.debug('Airflow not installed')

try:
    from superset.security import SupersetSecurityManager
    class SupersetOIDCSecurityManager(SupersetSecurityManager):
        def __init__(self, appbuilder):
            super().__init__(appbuilder)
            if self.auth_type == AUTH_OID:
                self.oid = OpenIDConnect(self.appbuilder.get_app)
                self.authoidview = SupersetAuthOIDCView
except ImportError:
    log.debug('Superset not installed')
