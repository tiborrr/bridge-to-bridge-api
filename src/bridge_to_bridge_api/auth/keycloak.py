import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakAdmin, KeycloakOpenID

from bridge_to_bridge_api.core.config import get_settings

logger = logging.getLogger(__name__)


def get_keycloak_admin() -> KeycloakAdmin:
    """Admin client for the app realm.

    In production the API authenticates as the service account of the
    KEYCLOAK_ADMIN_CLIENT_ID client in the app realm, which only holds the
    realm-management roles it needs (manage-users, view-users). The master
    admin login is only a fallback for local development, when no client
    secret is configured.
    """
    settings = get_settings()
    if settings.KEYCLOAK_ADMIN_CLIENT_SECRET:
        return KeycloakAdmin(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
            verify=True,
        )
    # Log in to master, but manage the app realm. (Assigning admin.realm_name
    # afterwards has no effect in python-keycloak 7, so users were created in master.)
    return KeycloakAdmin(
        server_url=settings.KEYCLOAK_SERVER_URL,
        realm_name=settings.KEYCLOAK_REALM,
        user_realm_name="master",
        client_id="admin-cli",
        username=settings.KEYCLOAK_ADMIN_USERNAME,
        password=settings.KEYCLOAK_ADMIN_PASSWORD,
        verify=True,
    )


def get_keycloak_openid() -> KeycloakOpenID:
    settings = get_settings()
    return KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER_URL,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        realm_name=settings.KEYCLOAK_REALM,
        verify=True,
    )


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_settings().KEYCLOAK_SERVER_URL}/realms/{get_settings().KEYCLOAK_REALM}/protocol/openid-connect/token",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    keycloak_openid: KeycloakOpenID = Depends(get_keycloak_openid),
):
    try:
        # Decode and verify token
        payload = keycloak_openid.decode_token(token)
        return payload
    except Exception as e:
        logger.error(f"Token validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
