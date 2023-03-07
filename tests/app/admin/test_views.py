from tests.utils import ok_response, error_response


class TestAdminLoginView:
    url = "/admin.login"

    async def test_create_on_startup(self, store, config):
        admin = await store.admins.get_by_email(config.admin.email)
        assert admin is not None
        assert admin.email == config.admin.email

    async def test_success(self, cli, config):
        response = await cli.post(
            self.url,
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
            self.url,
            json={
                "password": "qwerty",
            },
        )
        assert response.status == 400
        data = await response.json()
        assert data == error_response(
            status="bad_request",
            message="Unprocessable Entity",
            data={"email": ["Missing data for required field."]},
        )

    async def test_not_valid_credentials(self, cli):
        response = await cli.post(
            self.url,
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert response.status == 403
        data = await response.json()
        assert data == error_response(status="forbidden", message="403: Forbidden")

    async def test_different_method(self, cli):
        response = await cli.get(
            self.url,
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert response.status == 405
        data = await response.json()
        assert data == error_response(
            status="not_implemented", message="405: Method Not Allowed"
        )


class TestAdminCurrentView:
    url = "/admin.current"

    async def test_success(self, authed_cli, config):
        response = await authed_cli.get(self.url)
        assert response.status == 200
        data = await response.json()
        assert data == ok_response({"id": 1, "email": config.admin.email})

    async def test_unauthorized(self, cli, config):
        response = await cli.get(self.url)
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized", message="401: Unauthorized"
        )


class TestAdminStatistic:
    url = "/admin.statistic"

    async def test_success(self, authed_cli, question_1, game_1, user_1):
        response = await authed_cli.get(self.url)
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {"games_count": 1, "users_count": 1, "questions_count": 1}
        )

    async def test_unauthorized(self, cli, config):
        response = await cli.get(self.url)
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized", message="401: Unauthorized"
        )


class TestAdminUserStatistic:
    url = "/admin.statistic.users"

    async def test_success(self, authed_cli, question_1, user_1, game_1, participant_1):
        response = await authed_cli.get(self.url)
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "users_count": 1,
                "users": [{"fullname": "Noname Nobody", "games": 1, "scores": 13}],
            }
        )

    async def test_unauthorized(self, cli, config):
        response = await cli.get(self.url)
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized", message="401: Unauthorized"
        )


class TestAdminGameStatistic:
    url = "/admin.statistic.games"

    async def test_success(self, authed_cli, question_1, user_1, game_1, game_2):
        response = await authed_cli.get(self.url)
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {"games_count": 2, "games": [{"status": "Игра запущенна", "count": 2}]}
        )

    async def test_unauthorized(self, cli, config):
        response = await cli.get(self.url)
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized", message="401: Unauthorized"
        )
