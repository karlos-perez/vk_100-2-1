import json
import typing

from aiohttp.web_exceptions import HTTPException, HTTPUnprocessableEntity
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from app.admin.models import AdminModel
from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request


@middleware
async def auth_middleware(request: "Request", handler: callable):
    session = await get_session(request)
    if session:
        request.admin = AdminModel.from_session(session)
    return await handler(request)


HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        if e.status in HTTP_ERROR_CODES.keys():
            status_code = e.status
            status_str = HTTP_ERROR_CODES[e.status]
        else:
            status_code = e.status
            status_str = e.reason
        return error_json_response(
            http_status=status_code, status=status_str, message=str(e.text)
        )
    except Exception as e:
        return error_json_response(
            http_status=500, status=HTTP_ERROR_CODES[500], message=str(e)
        )


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
