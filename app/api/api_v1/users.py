from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import deps

router = APIRouter()

@router.get("/me")
def me(
    *,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    return current_user