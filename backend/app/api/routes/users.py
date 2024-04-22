"""
  Users routes.
"""
from typing import Any
from fastapi import APIRouter, HTTPException
from app.crud import users as crud_users
from app.api.deps import (
    CurrentUser,
    HBase,
)
from app.models.users import (UserCreate, UserPublic)

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(*, db: HBase, user_in: UserCreate) -> Any:
  """
  Create a new user.
  """
  user = crud_users.get_user_by_username(db=db,
                                         username=user_in.username)
  if user:
    raise HTTPException(
        status_code=400,
        detail="The user with this username already exists in the system",
    )
  user_create = UserCreate.model_validate(user_in)
  user = crud_users.create_user(db=db, user_create=user_create)
  return user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
  """
  Get current user.
  """
  return current_user


@router.delete("/{user_id}")
def delete_user(db: HBase, current_user: CurrentUser,
                username: str) -> Any:
  """
  Delete the user with the provided ID.
  """
  user = crud_users.get_user_by_username(username)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  elif user != current_user:
    raise HTTPException(status_code=403,
                        detail="The user doesn't have enough privileges")

  crud_users.delete_user_by_username(username)
  return {"message": "User deleted successfully"}