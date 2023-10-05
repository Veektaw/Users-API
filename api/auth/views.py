from flask import request, jsonify
import json
import logging
from ..utils import db, jwt, blocklist
from datetime import datetime 
from flask_restx import Namespace, Resource, fields
from ..models.Users import User
from functools import wraps
from ..models.tokenblocklist import TokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                get_jwt_identity,
                                 get_jti,
                                 get_jwt_identity,
                                 verify_jwt_in_request,
                                 unset_jwt_cookies,
                                 get_jwt)
from .serializers import signup_expect_model, signup_model, auth_namespace, login_expect_model

admin_dashboard_namespace = Namespace('admin_dashboard', description='Namespace for admin dashboard') 



## This is to sign up a user. User with the email "Veektaw@gmail.com, is the admin. change it above to give others access as admin"
@auth_namespace.route('/signup')
class SignUp(Resource):
   
   @auth_namespace.expect(signup_expect_model)
   @auth_namespace.doc(description="Signup user")
   
   def post(self):
      """
         This is to signup a user
      """
         
      data = request.get_json()
         
      new_user  = User (
         first_name = data.get('first_name'),
         last_name = data.get('last_name'),
         email = data.get('email'), 
         password = generate_password_hash(data.get('password'))
      )
      
      if data.get('email') == 'veektaw@gmail.com':
          new_user.is_admin = True
      
      signup_attempt = User.query.filter_by(email=new_user.email).first()
      
      if signup_attempt:
         response = {"message" : "Email exists"}
         return response, HTTPStatus.NOT_ACCEPTABLE
         
         
      try:
         new_user.save()
            
      except:
         db.session.rollback()
         response = {"message" : "An error occured"}
             
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
         'tokens': tokens
      }
      
      return response , HTTPStatus.CREATED 
  



@auth_namespace.route('/login')
class Login(Resource):
   
   @auth_namespace.expect(login_expect_model)
   @auth_namespace.doc(description = "Login user",
                       params = {"user input": "Email and password"})
   def post(self):
      
      """
        This is to login a user
      """
      
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

         return response, HTTPStatus.OK
      
      else:
         response = {"message": "Invalid credentials"} 
         return response , HTTPStatus.NOT_FOUND
     
@auth_namespace.route('/refresh')
class Refresh(Resource):

   @auth_namespace.doc(description = "Refresh access token of user login")
   @jwt_required(refresh=True)
   def post(self):
      
      
      email = get_jwt_identity()

      access_token = create_access_token(identity=email)

      return {"access_token": access_token}, HTTPStatus.OK
   
   


@auth_namespace.route('/logout')
class UserLogout(Resource):
   
   @auth_namespace.doc(description = "Logout user by revoking access token of user login")
   @jwt_required()
   def post(self):
      
      """
         This is to log out a user
      """
      
      
      jti = get_jwt()["jti"]
      blocklist.add(jti)
      return {"message": "Successfully logged out"}, HTTPStatus.OK

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        
        user_email = get_jwt_identity()
        
        user = User.query.filter_by(email=user_email).first()

        if user is None or not user.is_admin:
            return jsonify(message="Admin access required"), 403

        return fn(*args, **kwargs)

    return wrapper

@auth_namespace.route('/admin')
class AdminDashboard(Resource):

    @jwt_required
    @admin_required
    def get(self):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()

        return {
            "message": f"Welcome to the admin dashboard, {user.first_name} {user.last_name}!",
            "email": user.email,
        }, 200