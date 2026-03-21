from django.contrib.auth import authenticate, login, logout
from ninja import Router
from ninja.security import django_auth
from ninja.errors import HttpError

from .schemas import LoginIn, UserOut

router = Router()


@router.post("/login/", response=UserOut, auth=None)
def login_view(request, payload: LoginIn):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        raise HttpError(401, "Invalid credentials")
    login(request, user)
    return UserOut(id=user.id, username=user.username)


@router.post("/logout/")
def logout_view(request):
    logout(request)
    return {"detail": "Logged out"}


@router.get("/me/", response=UserOut, auth=django_auth)
def me_view(request):
    return UserOut(id=request.user.id, username=request.user.username)
