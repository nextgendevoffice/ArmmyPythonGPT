from flask import Flask

def create_app():
    app = Flask(__name__)

    from .line_bot import line_bp
    app.register_blueprint(line_bp)

    return app
