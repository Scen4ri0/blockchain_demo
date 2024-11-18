from flask import Flask
from .routes import routes

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.register_blueprint(routes)
    return app
