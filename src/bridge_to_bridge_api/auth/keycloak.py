from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID, KeycloakAdmin
from bridge_to_bridge_api.core.config import get_settings
import jwt
import logging

logger = logging.getLogger(__name__)

def get_keycloak_admin() -> KeycloakAdmin:
    settings = get_settings()
    admin = KeycloakAdmin(
        server_url=settings.KEYCLOAK_SERVER_URL,
        client_id="admin-cli",
        realm_name="master",
        username=settings.KEYCLOAK_ADMIN_USERNAME,
        password=settings.KEYCLOAK_ADMIN_PASSWORD,
        verify=True
    )
    admin.realm_name = settings.KEYCLOAK_REALM
    return admin

def get_keycloak_openid() -> KeycloakOpenID:
    settings = get_settings()
    return KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER_URL,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        realm_name=settings.KEYCLOAK_REALM,
        client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        verify=True
    )

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_settings().KEYCLOAK_SERVER_URL}/realms/{get_settings().KEYCLOAK_REALM}/protocol/openid-connect/token",
)

async def get_current_user(token: str = Depends(oauth2_scheme), keycloak_openid: KeycloakOpenID = Depends(get_keycloak_openid)):
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
        )
