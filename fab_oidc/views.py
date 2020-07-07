import os
from flask import redirect, request
from flask_appbuilder.security.views import AuthOIDView
from flask_login import login_user
from flask_admin import expose
from urllib.parse import quote


# Set the OIDC field that should be used as a username
USERNAME_OIDC_FIELD = os.getenv('USERNAME_OIDC_FIELD', default='sub')
FIRST_NAME_OIDC_FIELD = os.getenv('FIRST_NAME_OIDC_FIELD',
                                  default='nickname')
LAST_NAME_OIDC_FIELD = os.getenv('LAST_NAME_OIDC_FIELD',
                                 default='name')
GROUPS_OIDC_FIELD = os.getenv('GROUPS_OIDC_FIELD', default='groups')


class AuthOIDCView(AuthOIDView):

    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):

        sm = self.appbuilder.sm
        oidc = sm.oid

        @self.appbuilder.sm.oid.require_login
        def handle_login():
            user = sm.auth_user_oid(oidc.user_getfield('email'))
            groups = oidc.user_getfield(GROUPS_OIDC_FIELD)

            if user is None:
                info = oidc.user_getinfo([
                    USERNAME_OIDC_FIELD,
                    FIRST_NAME_OIDC_FIELD,
                    LAST_NAME_OIDC_FIELD,
                    'email',
                ])

                user = sm.add_user(
                    username=info.get(USERNAME_OIDC_FIELD),
                    first_name=info.get(FIRST_NAME_OIDC_FIELD),
                    last_name=info.get(LAST_NAME_OIDC_FIELD),
                    email=info.get('email'),
                    role=sm.find_role(sm.auth_user_registration_role)
                )

            if groups is not None:
                AuthOIDCView.sync_roles(groups, user, sm)

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

    def sync_roles(groups, user, sm):
        # sync OIDC groups to roles
        updated = False
        for role in user.roles:
            if role.name not in groups and role.name not in [
                sm.auth_role_admin,
                sm.auth_user_registration_role]:
                user.roles.remove(role)
                updated = True

        for group in groups:
            role = sm.find_role(group)
            if role is not None:
                user.roles.append(role)
                updated = True

        if updated:
            sm.update_user(user)
