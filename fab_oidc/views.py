from flask import redirect, request
from flask_appbuilder.security.views import AuthOIDView
from flask_login import login_user
from flask_admin import expose
from urllib.parse import quote


class AuthOIDCView(AuthOIDView):

    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):

        sm = self.appbuilder.sm
        oidc = sm.oid

        @self.appbuilder.sm.oid.require_login
        def handle_login():
            user = sm.auth_user_oid(oidc.user_getfield('email'))

            if user is None:
                info = oidc.user_getinfo(
                    ['sub', 'name', 'email', 'nickname']
                )

                user = sm.add_user(
                    username=info.get('sub'),
                    first_name=info.get('nickname'),
                    last_name=info.get('name'),
                    email=info.get('email'),
                    role=sm.find_role(sm.auth_user_registration_role)
                )

            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)

        return handle_login()

    @expose('/logout/', methods=['GET', 'POST'])
    def logout(self):

        oidc = self.appbuilder.sm.oid

        oidc.logout()
        super(AuthOIDCView, self).logout()
        redirect_url = request.url_root.strip(
            '/') + self.appbuilder.get_url_for_login

        logout_uri = oidc.client_secrets.get(
            'issuer') + '/protocol/openid-connect/logout?redirect_uri='
        if 'OIDC_LOGOUT_URI' in self.appbuilder.app.config:
            logout_uri = self.appbuilder.app.config['OIDC_LOGOUT_URI']

        return redirect(logout_uri + quote(redirect_url))

class SupersetAuthOIDCView(AuthOIDView):

    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):

        sm = self.appbuilder.sm
        oidc = sm.oid

        @self.appbuilder.sm.oid.require_login
        def handle_login():
            user = sm.auth_user_oid(oidc.user_getfield('email'))

            if user is None:
                info = oidc.user_getinfo(
                    ['sub', 'given_name', 'family_name', 'email']
                )

                # Superset requires `first_name` not to be NULL, so we use the
                # `given_name` rather than `nickname`, which has higher
                # probability for being NULL
                user = sm.add_user(
                    username=info.get('sub'),
                    first_name=info.get('given_name'),
                    last_name=info.get('family_name'),
                    email=info.get('email'),
                    role=sm.find_role(sm.auth_user_registration_role)
                )

            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)

        return handle_login()

    @expose('/logout/', methods=['GET', 'POST'])
    def logout(self):

        oidc = self.appbuilder.sm.oid
        id_token = oidc.get_access_token()

        oidc.logout()
        super(SupersetAuthOIDCView, self).logout()
        redirect_url = request.url_root.strip(
            '/') + self.appbuilder.get_url_for_login

        issuer_uri = oidc.client_secrets.get('issuer')
        logout_uri = f'{issuer_uri}/logout?id_token_hint={id_token}&redirect_uri='

        if 'OIDC_LOGOUT_URI' in self.appbuilder.app.config:
            logout_uri = self.appbuilder.app.config['OIDC_LOGOUT_URI']

        return redirect(logout_uri + quote(redirect_url))
