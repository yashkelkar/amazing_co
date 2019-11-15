from flask import Flask, Blueprint, redirect
from employee_management.api.restplus import api
from employee_management.api.v1.endpoints.employee import ns as employee_namespace
from flask_cors import CORS
import structlog

app = Flask(__name__)
log = structlog.get_logger(__file__)

cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})


@app.route("/__health/", methods=["GET"])
@app.route("/__health", methods=["GET"])
def health():
    return "ok", 200


@app.route('/')
def api_page():
    return redirect("/api/v1", code=302)


def initialize_app(flask_app):
    blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
    api.init_app(blueprint)
    api.add_namespace(employee_namespace)
    flask_app.register_blueprint(blueprint)



initialize_app(app)

if __name__ == '__main__':
    app.run()
