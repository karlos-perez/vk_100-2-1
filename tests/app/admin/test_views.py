from tests.utils import ok_response, error_response


class TestAdminLoginView:
    async def test_create_on_startup(self, store, config):
        admin = await store.admins.get_by_email(config.admin.email)
        assert admin is not None
        assert admin.email == config.admin.email

    async def test_success(self, cli, config):
        response = await cli.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password,
            },
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "id": 1,
                "email": config.admin.email,
            }
        )

    async def test_missed_email(self, cli):
        response = await cli.post(
            "/admin.login",
            json={
                "password": "qwerty",
            },
        )
        assert response.status == 400
        data = await response.json()
        assert data == error_response(status="bad_request",
                                      message="Unprocessable Entity",
                                      data={'email': ['Missing data for required field.']})

    async def test_not_valid_credentials(self, cli):
        response = await cli.post(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert response.status == 403
        data = await response.json()
        assert data == error_response(status="forbidden",
                                      message="403: Forbidden")

    async def test_different_method(self, cli):
        response = await cli.get(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert response.status == 405
        data = await response.json()
        assert data == error_response(status="not_implemented",
                                      message="405: Method Not Allowed")


class TestAdminCurrentView:
    async def test_success(self, authed_cli, config):
        response = await authed_cli.get("/admin.current")
        assert response.status == 200
        data = await response.json()
        assert data == ok_response({"id": 1,
                                    "email": config.admin.email})

    async def test_unauthorized(self, cli, config):
        response = await cli.get("/admin.current")
        assert response.status == 401
        data = await response.json()
        assert data == error_response(status="unauthorized",
                                      message="401: Unauthorized")
