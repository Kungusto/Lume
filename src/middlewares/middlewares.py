import re
from datetime import datetime, timedelta, timezone
from typing import Tuple
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.api.dependencies import get_db_as_context_manager
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError
from src.services.auth import AuthService
from fastapi import status
from src.constants.permissions import Permissions


class BanCheckMiddleware(BaseHTTPMiddleware):
    def ban_response(self, time_left: timedelta) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Вы были забанены",
                "remainded": time_left.total_seconds(),
            },
        )

    def expired_token_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Срок действия токена истек"},
        )

    
    def unauthenticated_user_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Вы не аутентифицированы!"},
        )

    def permission_denied_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "У вас недостаточно прав для совершения данной операции"
            },
        )

    def _get_user_id_and_role(self, token: str) -> Tuple[int | None, str | None]:
        try:
            decoded_token = AuthService().decode_token(token)
            user_role = decoded_token.get("role")
            user_id = decoded_token.get("user_id")
            return user_id, user_role
        except ExpiredSignatureError:
            return None, None  # 2 None чтобы не вызвать ошибку при распаковке

    def _should_check(self, request: Request) -> bool:
        """Нужно ли проверять, что пользователь забанен"""
        if request.url.path == "/auth/logout":
            return False
        for (pattern, method) in Permissions.PUBLIC_ENDPOINTS:
            if re.match(pattern, request.url.path) and request.method == method:
                return False
        return True

    async def _update_user_activity(self, db, user_id: int) -> None:
        await db.users.update_user_activity(user_id=user_id)
        await db.commit()

    async def check_ban_user(self, db, user_id: int) -> JSONResponse | None:
        user_ban = await db.bans.get_ban_by_user_id(user_id=user_id)
        if user_ban:
            time_left = user_ban.ban_until - datetime.now((timezone.utc))
            return self.ban_response(time_left=time_left)
        return None

    def get_prefix(self, path: str) -> str:
        parts = path.lstrip("/").split("/")
        return parts[0] if parts else ""

    def check_permissions_user(self, user_role: str, path: str) -> bool:
        allowed_prefixes = Permissions.ROLES_PREFIXES.get(user_role.upper(), [])
        prefix = self.get_prefix(path=path)
        if prefix in allowed_prefixes:
            return True
        return False
    
    async def dispatch(self, request: Request, call_next):
        """
        Проверяет, забанен ли пользователь, на всех методах, кроме GET,
        и на всех url, кроме разлогина

        Если пользователь не аутентифицирован - пропускаем, т.к. без токена
        он все равно ничего не сможет опубликовать
        """
        access_token = request.cookies.get("access_token", None)
        if not self._should_check(request=request):
            return await call_next(request)
        elif not access_token:
            return self.unauthenticated_user_response()

        # Получаем данные о пользователе из токена
        user_id, user_role = self._get_user_id_and_role(token=access_token)

        # Проверяем что срок токена не истек
        if user_id is None or user_role is None:
            return self.expired_token_json()

        check_permissions = self.check_permissions_user(
            user_role=user_role, path=request.url.path
        )
        if not check_permissions:
            return self.permission_denied_response()

        async with get_db_as_context_manager() as db:
            await self._update_user_activity(db=db, user_id=user_id)
            if request.method != "GET":
                ban_response = await self.check_ban_user(db=db, user_id=user_id)
                if ban_response:
                    return ban_response

        return await call_next(request)

