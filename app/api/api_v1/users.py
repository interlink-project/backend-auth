from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import deps, crud

router = APIRouter()

@router.get("/me/")
def me(
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.get("/{id}")
async def retrieve(
    id: str,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    user = await crud.get(id)
    return user

@router.get("/")
async def list(
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    return await crud.get_all()