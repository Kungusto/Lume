from datetime import datetime, timezone
import logging
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.api.dependencies import get_db
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError
from src.services.auth import AuthService
from fastapi import status


class BanCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Проверяет, забанен ли пользователь, на всех методах, кроме GET,
        и на всех url, кроме разлогина

        Если пользователь не аутентифицирован - пропускаем, т.к. без токена
        он все равно ничего не сможет опубликовать
        """
        token_is_expired = False

        logging.info("Обработка миддлваром")
        access_token = request.cookies.get("access_token", None)
        """
         если нету access_token, не проверяем,
        т.к. без него пользователь все равно не сможет ничего публиковать
        """
        if not access_token:
            logging.info("Вызов эндпоинта")
            return await call_next(request)


        async for db in get_db():
            try:
                user_id = AuthService().decode_token(access_token)["user_id"]
                await db.users.update_user_activity(user_id=user_id)
                await db.commit()
            except ExpiredSignatureError:
                token_is_expired = True


            if request.method != "GET" and request.url.path != "/auth/logout":
                if token_is_expired:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Срок действия токена истек"},
                    )
                banned_users = await db.bans.get_banned_users()
                for banned_user in banned_users:
                    if user_id == banned_user.user_id:
                        time_left = banned_user.ban_until - datetime.now((timezone.utc))
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={
                                "detail": f"Вы были забанены. осталось: {time_left}"
                            },
                        )


        logging.info("Вызов эндпоинта")
        return await call_next(request)
