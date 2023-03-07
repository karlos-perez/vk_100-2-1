from aiohttp.web import HTTPForbidden
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import (
    AdminSchema,
    StatisticSchema,
    StatisticGameSchema,
    StatisticUserSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Admin login", description="Login admin user")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data.get("email", "")
        password = self.data.get("password", "")
        if email and password:
            admin = await self.store.admins.get_by_email(email)
            if admin is None:
                raise HTTPForbidden
            if admin.is_password_valid(password):
                session = await new_session(request=self.request)
                session["sessionid"] = self.request.app.config.session.key
                response = AdminSchema().dump(admin)
                session["admin"] = response
                return json_response(data=response)
        else:
            raise HTTPBadRequest


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="User info", description="Current user information")
    @response_schema(AdminSchema, 200)
    async def get(self):
        admin = getattr(self.request, "admin", None)
        response = AdminSchema().dump(admin)
        return json_response(data=response)


class AdminStatisticView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Total statistic",
        description="Total statistic information",
    )
    @response_schema(StatisticSchema, 200)
    async def get(self):
        statistic = await self.store.admins.get_full_statistic()
        response = StatisticSchema().dump(statistic)
        return json_response(data=response)


class AdminStatisticGameView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Game statistic",
        description="Game statistic information",
    )
    @response_schema(StatisticGameSchema, 200)
    async def get(self):
        statistic = await self.store.admins.get_game_statistic()
        response = StatisticGameSchema().dump(statistic)
        return json_response(data=response)


class AdminStatisticUserView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="User statistic",
        description="User statistic information",
    )
    @response_schema(StatisticUserSchema, 200)
    async def get(self):
        statistic = await self.store.admins.get_user_statistic()
        response = StatisticUserSchema().dump(statistic)
        return json_response(data=response)
