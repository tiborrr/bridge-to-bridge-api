from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from bridge_to_bridge_api.core.database import get_db
from bridge_to_bridge_api.auth.keycloak import get_current_user
from bridge_to_bridge_api.models.user import User
from bridge_to_bridge_api.schemas.user import UserProfile, UserProfileUpdate

router = APIRouter()

@router.get("/me/preferences", response_model=UserProfile)
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    keycloak_id = current_user.get("sub")
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        # Create user profile lazily
        user = User(
            keycloak_id=keycloak_id,
            email=current_user.get("email"),
            name=current_user.get("preferred_username"),
            preferred_positions=[]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.put("/me/preferences", response_model=UserProfile)
def update_user_preferences(
    preferences: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    keycloak_id = current_user.get("sub")
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        user = User(
            keycloak_id=keycloak_id,
            email=current_user.get("email"),
            name=current_user.get("preferred_username"),
            preferred_positions=preferences.preferred_positions
        )
        db.add(user)
    else:
        user.preferred_positions = preferences.preferred_positions
        if preferences.name is not None:
            user.name = preferences.name
    
    db.commit()
    db.refresh(user)
    return user
