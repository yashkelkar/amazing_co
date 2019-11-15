import structlog
from flask_restplus import Api

log = structlog.getLogger(__name__)

api = Api(version='1.0', title='Amazing Co Employee Directory API',
          description="Amazing Co's Employee Directory API!")
