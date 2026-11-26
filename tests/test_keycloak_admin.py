from bridge_to_bridge_api.auth import keycloak as kc
from bridge_to_bridge_api.core.config import Settings


def _capture(monkeypatch, **settings):
    calls = []
    monkeypatch.setattr(
        kc, "get_settings", lambda: Settings(_env_file=None, **settings)
    )
    monkeypatch.setattr(
        kc, "KeycloakAdmin", lambda **kwargs: calls.append(kwargs) or kwargs
    )
    kc.get_keycloak_admin()
    return calls[0]


def test_uses_app_realm_service_account_when_secret_is_set(monkeypatch):
    kwargs = _capture(
        monkeypatch,
        KEYCLOAK_REALM="bridge-realm",
        KEYCLOAK_ADMIN_CLIENT_SECRET="s3cret",
    )
    assert kwargs["realm_name"] == "bridge-realm"
    assert kwargs["client_id"] == "bridge-api-admin"
    assert kwargs["client_secret_key"] == "s3cret"
    assert "username" not in kwargs and "user_realm_name" not in kwargs


def test_dev_fallback_logs_in_to_master_but_manages_app_realm(monkeypatch):
    kwargs = _capture(
        monkeypatch, KEYCLOAK_REALM="bridge-realm", KEYCLOAK_ADMIN_CLIENT_SECRET=""
    )
    assert kwargs["realm_name"] == "bridge-realm"
    assert kwargs["user_realm_name"] == "master"
    assert kwargs["client_id"] == "admin-cli"
