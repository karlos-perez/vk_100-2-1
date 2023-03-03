from aiohttp.web_app import Application


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.questions.routes import setup_routes as questions_setup_routes

    admin_setup_routes(app)
    questions_setup_routes(app)
