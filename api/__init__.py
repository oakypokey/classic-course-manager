import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from api.index_route import index_route
from api.api_routes import api_routes
SECRET_KEY = os.getenv("SECRET_KEY", default="super secret")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.register_blueprint(index_route)
    app.register_blueprint(api_routes)
    return app

if __name__ == "__main__":
    my_app = create_app()
    my_app.run(debug=True)