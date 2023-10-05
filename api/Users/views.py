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

## When accessing the api from the browser, copy and paste the access token in the Authorization header.




@user_namespace.route('/users')
class GetUsers(Resource):
   
    @user_namespace.doc(
    description="Get all users",
    params={"get method": "Get all users",})
       
    @user_namespace.marshal_with(user_marshall_serializer)
    @jwt_required()
    
    
    def get(self):
        
        """
        This gets all the users in the database.
        """

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

        user = User.get_by_id(id)

        if user is None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        return user, HTTPStatus.OK
    

    @user_namespace.doc(description="Delete a User by ID", params={"id": "ID of the user"})
    @jwt_required()
    
    def delete(self, id):
        """
        This deletes a user by ID.
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
        
        """
        This updates a user by ID.
        """
        authenticated_user_email = get_jwt_identity()
        authenticated_user = User.query.filter_by(email=authenticated_user_email).first()

        if authenticated_user.email != "veektaw@gmail.com":  # Change this email to give access to update users.
            return {'Message': 'You do not have access'}, HTTPStatus.NOT_ACCEPTABLE

        user = User.get_by_id(id)

        if user is None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        data = request.json

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)

        user.save()

        return {"message": "User updated successfully"}, HTTPStatus.OK
