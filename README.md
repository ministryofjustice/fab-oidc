# Flask-AppBuilder SecurityManager for OpenIDConnect

Wrapper for [flask_oidc] that exposes a `SecurityManager` for use with any Flask-AppBuilder app.

It will allow your users to login with OpenIDConnect providers such as Auth0, Okta or Google Apps.

This is roughly inspired by the code in this [stackoverflow](https://stackoverflow.com/a/47787279/44252) answer. (MIT Licenced © [thijsfranck](https://stackoverflow.com/users/8905583/thijsfranck))

## Usage

### Generic

Just override the default security manager in your Flask Appbuilder app.

```python
from fab_oidc.security import OIDCSecurityManager

appbuilder = AppBuilder(app, db.session, security_manager_class=OIDCSecurityManager)
```

### [Airflow]
Airflow provides a hook in the `webserver_config.py` file where you can specify a security manager class.
In `webserver_config.py` import the OIDCSecurityManager and set
```python
from fab_oidc.security import AirflowOIDCSecurityManager
...
SECURITY_MANAGER_CLASS = AirflowOIDCSecurityManager
```

Airflow now requires that your `SECURITY_MANAGER_CLASS` is a subclass of `AirflowSecurityManager`.
Use the special `AirflowOIDCSecurityManager` that is only defined if you're using this library alongside Airflow.

### [Superset]
Superset works in a a similar way. Just as in Airflow,
`SECURITY_MANAGER_CLASS` needs to be a subclass of `SupersetSecurityManager`
the config is in a file called `superset_config.py` and the hook is called
`CUSTOM_SECURITY_MANAGER`. There now exists a special
`SupersetOIDCSecurityManager` that is only defined if you are using this
library alongside Superset.

```python
from fab_oidc.security import SupersetOIDCSecurityManager
...
CUSTOM_SECURITY_MANAGER = SupersetOIDCSecurityManager
```


## Settings
The settings are the same as the [flask_oidc settings][flask_oidc_settings], so look there for a reference.

if you're happy with [flask_oidc]'s defaults the only thing you'll really need is something like:

```python
OIDC_CLIENT_SECRETS = '/path/to/client_secret.json'
```

see the [flask_oidc manual client registration][flask_oidc_manual_config] docs for how to generate or write one.

Copyright © 2018 HM Government (Ministry of Justice Digital Services). See LICENSE.txt for further details.


[flask_oidc]: http://flask-oidc.readthedocs.io/en/latest/
[flask_oidc_settings]: http://flask-oidc.readthedocs.io/en/latest/#settings-reference
[flask_oidc_manual_config]: http://flask-oidc.readthedocs.io/en/latest/#manual-client-registration
[Airflow]: https://airflow.apache.org/
[Superset]: https://superset.incubator.apache.org/
