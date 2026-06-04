from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Request
import jwt

from app.core.config import settings
from app.models.user_models import UserInDB, Role
from app.api.dependencies import UserRepositoryDep

# Using a simple function to extract token from HttpOnly cookie
def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

async def get_current_user(
    request: Request,
    user_repo: UserRepositoryDep
) -> UserInDB:
    token = get_token_from_cookie(request)
    if not token:
        # DEBUG: Log missing token
        import logging
        logging.getLogger("auth").debug(f"No token in cookies. Cookies: {list(request.cookies.keys())}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError as e:
        import logging
        logging.getLogger("auth").debug(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    user = await user_repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    if not user.is_active or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
        
    return user

async def get_current_user_or_guest(
    request: Request,
    user_repo: UserRepositoryDep
) -> Optional[UserInDB]:
    token = get_token_from_cookie(request)
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("user_id")
        if user_id:
            user = await user_repo.get_user_by_id(user_id)
            if user and user.is_active and not user.is_deleted:
                return user
    except Exception:
        pass
    return None

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: UserInDB = Depends(get_current_user)):
        current_role = current_user.role.value if isinstance(current_user.role, Role) else str(current_user.role)
        normalized_allowed = {
            role.value if isinstance(role, Role) else str(role)
            for role in allowed_roles
        }
        if current_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

CurrentUserDep = Annotated[UserInDB, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[UserInDB], Depends(get_current_user_or_guest)]
