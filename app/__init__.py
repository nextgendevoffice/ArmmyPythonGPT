from flask import Flask

app = Flask(__name__)

from .line_bot import line_bp
app.register_blueprint(line_bp)

def create_app(environ, start_response):
    return app(environ, start_response)
