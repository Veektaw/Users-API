from flask_restx import Namespace, fields


user_namespace = Namespace('user', description='Namespace for user')

user_expect_serializer = user_namespace.model ( 
    'User', {
      'first_name' : fields.String(required=True , description="User's first name"),
      'last_name' : fields.String(required=True , description="User's provided long url"),
      'email' : fields.String(required=True , description="User's email"),
      'password' : fields.String(required=True , description="User's password"),
    }
)

user_login_serializer = user_namespace.model ( 
    'User', {
      'email' : fields.String(required=True , description="User's email"),
      'password' : fields.String(required=True , description="User's password"),
    }
)


user_marshall_serializer = user_namespace.model (
    'User', {
      'first_name' : fields.String(required=True , description="User's first name"),
      'last_name' : fields.String(required=True , description="User's last name"),
      'email' : fields.String(required=True , description="User's email"),
    }
)

update_user_model = user_namespace.model('UpdateUser', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user'),
})