from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session, get_session

from app.admin.schemes import AdminSchema
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
    @docs(tags=["admin"], summary="User info", description="Current user infomation")
    @response_schema(AdminSchema, 200)
    async def get(self):
        admin = getattr(self.request, "admin", None)
        response = AdminSchema().dump(admin)
        return json_response(data=response)
