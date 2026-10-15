from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from business_object.user import User
from service.user_service import UserService

"""Shared FastAPI dependencies.

Any route reserved to logged-in users adds:
    current_user: User = Depends(get_current_user)
"""

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security),) -> User:
    """ Check the token of a user """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserService().find_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
