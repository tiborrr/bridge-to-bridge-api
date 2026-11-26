import uuid

from fastapi import APIRouter, Depends, HTTPException
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError
from sqlalchemy.orm import Session

from bridge_to_bridge_api.auth.keycloak import get_current_user, get_keycloak_admin
from bridge_to_bridge_api.core.database import get_db
from bridge_to_bridge_api.models.team import Team, TeamMember
from bridge_to_bridge_api.models.user import User
from bridge_to_bridge_api.schemas.team import InviteRequest, TeamCreate
from bridge_to_bridge_api.schemas.team import Team as TeamSchema

router = APIRouter()


@router.get("/", response_model=list[TeamSchema])
def get_my_teams(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    keycloak_id = current_user.get("sub")
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        return []

    team_members = db.query(TeamMember).filter(TeamMember.user_id == user.id).all()
    team_ids = [tm.team_id for tm in team_members]
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    return teams


@router.post("/", response_model=TeamSchema)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    keycloak_id = current_user.get("sub")
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="User profile not found. Please load profile first."
        )

    new_team = Team(name=team_data.name, boat_type=team_data.boat_type)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    member = TeamMember(team_id=new_team.id, user_id=user.id, role="leader")
    db.add(member)
    db.commit()

    return new_team


@router.post("/{team_id}/invite")
def invite_user(
    team_id: uuid.UUID,
    invite: InviteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    keycloak_admin: KeycloakAdmin = Depends(get_keycloak_admin),
):
    # Verify the current user is a leader
    keycloak_id = current_user.get("sub")
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    team_member = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
        .first()
    )
    if not team_member or team_member.role != "leader":
        raise HTTPException(status_code=403, detail="Not authorized to invite")

    # Invite user via Keycloak
    try:
        new_user_id = keycloak_admin.create_user(
            {
                "email": invite.email,
                "username": invite.email,
                "enabled": True,
                "emailVerified": False,
            },
            exist_ok=True,
        )

        if new_user_id:
            keycloak_admin.send_update_account_email(
                user_id=new_user_id, payload=["UPDATE_PASSWORD"]
            )
            return {"status": "success", "message": f"Invite sent to {invite.email}"}
        else:
            return {"status": "exists", "message": "User already exists in Keycloak"}

    except KeycloakError as e:
        raise HTTPException(status_code=400, detail=f"Keycloak error: {e!s}") from e
