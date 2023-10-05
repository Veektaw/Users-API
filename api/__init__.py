from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_admin import Admin
from functools import wraps
from flask_restx import Api
from .Users.views import user_namespace
from .auth.views import auth_namespace
from .config.config import config_dict
from .utils import db, jwt
from flask_caching.backends import RedisCache
from redis import Redis
from .models.Users import User
from .models.tokenblocklist import TokenBlocklist
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, create_access_token
from werkzeug.exceptions import NotFound, NotAcceptable, MethodNotAllowed
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_bcrypt import Bcrypt



def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    db.init_app(app)
    
    
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)
    
    
    authorizations = {
        'Bearer Auth':{
           "type": "apiKey",
           "in": "Header",
           "name": "Authorization",
           "description": "Add a JWT token to the header with ** Bearer <JWT Token>" 
        }
    }

    api = Api(app, title='User management',
              description='A user management API',
              version = 1.0,
              Host = 'https://e673-102-89-23-19.ngrok-free.app',
              authorizations=authorizations,
              security=['Bearer Auth'])

    
    api.add_namespace(user_namespace, path='/user')
    api.add_namespace(auth_namespace, path='/auth')

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method not allowed"}, 404

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'user': User,
            'tokenblocklist': TokenBlocklist
        }
    
    return app