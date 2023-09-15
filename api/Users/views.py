from http import HTTPStatus
from flask import request
from flask_restx import Resource
from flask import request
from flask_jwt_extended import jwt_required , get_jwt_identity, create_access_token, create_refresh_token
from .serializer import user_namespace, user_expect_serializer, user_marshall_serializer, user_login_serializer, update_user_model
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils import db
from api.models.Users import User


## When testing on postman or insomnia, copy and paste the access token in the bearer path.


@user_namespace.route('/users')
class GetUsers(Resource):
   
    @user_namespace.doc(
    description="Get all users",
    params={"get method": "Get all users",})
       
    @user_namespace.marshal_with(user_marshall_serializer)
    @jwt_required()
    
    
    def get(self):

        try:
            users = User.query.all()
            
        except:
            return {'Message':"Could not get all students"}, HTTPStatus.NOT_FOUND
        
        return users, HTTPStatus.OK
    

@user_namespace.route('/<id>')
class ViewDeleteUpdateUSERSbyID(Resource):
    
    @user_namespace.doc(description = "Get a User by id",
                       params = {"id":"ID of the User"})
    @user_namespace.marshal_with(user_marshall_serializer)  
    @jwt_required()
    
       
    def get(self, id):
        
        """
        
            This gives access to view a particular user
        
        """
        
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            return {"message": "Access denied"}

        url = User.get_by_id(id)

        if url is None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        return url, HTTPStatus.OK
    

    @user_namespace.doc(description="Delete a User by ID", params={"id": "ID of the user"})
    @jwt_required()
    
    def delete(self, id):
        """
        This deletes a user.
        """
        authenticated_user_email = get_jwt_identity()
        authenticated_user = User.query.filter_by(email=authenticated_user_email).first()

        if authenticated_user.email != "veektaw@gmail.com": ## IMPORTANT: Change this email to give access to delete users.
            return {'Message': 'You do not have access'}, HTTPStatus.NOT_ACCEPTABLE

        user = User.get_by_id(id)

        if user is None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        user.delete()

        return {"message": "User deleted successfully"}, HTTPStatus.OK
    
    @user_namespace.doc(description="Update a User by ID", params={"id": "ID of the user"})
    @user_namespace.expect(update_user_model)
    @jwt_required()
 
    def put(self, id):
        authenticated_user_email = get_jwt_identity()
        authenticated_user = User.query.filter_by(email=authenticated_user_email).first()

        if authenticated_user.email != "veektaw@gmail.com":  # Change this email to give access to update users.
            return {'Message': 'You do not have access'}, HTTPStatus.NOT_ACCEPTABLE

        user = User.get_by_id(id)

        if user is None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        # Parse the request data
        data = request.json

        # Update user information
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)

        user.save()

        return {"message": "User updated successfully"}, HTTPStatus.OK
    
    
    
    
    
    
    
    
@user_namespace.route('/signup')
class SignUp(Resource):
   @user_namespace.expect(user_expect_serializer)
   @user_namespace.marshal_list_with(user_marshall_serializer)
   @user_namespace.doc(description="Signup user")
   
   def post(self):
      
      data = request.get_json()
         
      new_user  = User (
         first_name = data.get('first_name'),
         last_name = data.get('last_name'),
         email = data.get('email'), 
         password = generate_password_hash(data.get('password'))
      )
      
      signup_attempt = User.query.filter_by(email=new_user.email).first()
      
      if signup_attempt:
         response = {"message" : "Email exists"}
         return response, HTTPStatus.NOT_ACCEPTABLE
         
         
      try:
         new_user.save()
            
      except:
         db.session.rollback()
         response = {"message" : "An error occurred"}
         
             
         return response, HTTPStatus.INTERNAL_SERVER_ERROR
         
      access_token = create_access_token(identity=new_user.email)
      refresh_token = create_refresh_token(identity=new_user.email)
      
      tokens = {
         'access_token' : access_token,
         'refresh_token' : refresh_token
         }
         
      response = {
         'id': new_user.id,
         'first_name': new_user.first_name,
         'last_name': new_user.last_name,
         'email': new_user.email,
         'password': new_user.password,
         'tokens': tokens
      }
      
      return response , HTTPStatus.CREATED 
  
  
@user_namespace.route('/login')
class Login(Resource):
   @user_namespace.expect(user_login_serializer)
   @user_namespace.doc(description = "Login user",
                       params = {"user input": "Email and password"})
   def post(self):
      
      
      data = request.get_json()

      email = data.get("email")
      password = data.get("password")

      user = User.query.filter_by(email=email).first()

      if (user is not None) and check_password_hash(user.password, password):
         access_token = create_access_token(identity=user.email)
         refresh_token = create_refresh_token(identity=user.email)

         response = {
            'access_token': access_token,
            'refresh_token': refresh_token
         }

         return response, HTTPStatus.CREATED
      
      else:
         response = {"message": "Invalid credentials"} 
         return response , HTTPStatus.NOT_FOUND
     
@user_namespace.route('/refresh')
class Refresh(Resource):

   @user_namespace.doc(description = "Refresh access token of user login")
   @jwt_required(refresh=True)
   def post(self):
      email = get_jwt_identity()

      access_token = create_access_token(identity=email)

      return {"access_token": access_token}, HTTPStatus.OK