from app import bcrypt
from flask import Blueprint, request
from flask.views import MethodView
from app.models import User, BlackListToken
from app.auth.helper import response, response_auth
from sqlalchemy import exc
from app.auth.helper import token_required
import re
from pycountry import countries


auth = Blueprint('auth', __name__)


class RegisterUser(MethodView):
    """
    View function to register a user via the api
    """

    def post(self):
        """
        Register a user, generate their token and add them to the database
        :return: Json Response with the user`s token
        """
        if request.content_type == 'application/json':
            post_data = request.get_json()
            print(post_data)
            first_name = post_data.get('first_name')
            last_name = post_data.get('last_name')
            email = post_data.get('email', '')
            password = post_data.get('password')
            country = post_data.get('country')
            if not first_name:
                return response('failed', 'first_name is missing', 400)
            if not last_name:
                return response('failed', 'last_name is missing', 400)
            if not password:
                return response('failed', 'password is missing', 400)
            if country:
                country_code = countries.get(name=country)
                if not country_code:
                    return response('failed', 'Invalid country provided', 400)
            else:
                return response('failed', 'country is missing', 400)
            if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
                user = User.get_by_email(email)
                if not user:
                    token = User(first_name=first_name, last_name=last_name, email=email, password=password, country=country).save()
                    return response_auth('success', 'Successfully registered', token, 201)
                else:
                    return response('failed', 'Failed, User already exists, Please sign In', 400)
            return response('failed', 'Missing or wrong email format', 400)
        return response('failed', 'Content-type must be json', 400)


class LoginUser(MethodView):
    def post(self):
        """
        Login a user if the supplied credentials are correct.
        :return: Http Json response
        """
        if request.content_type == 'application/json':
            post_data = request.get_json()
            email = post_data.get('email', '')
            password = post_data.get('password', '')
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                user = User.query.filter_by(email=email).first()
                if user and bcrypt.check_password_hash(user.password, password):
                    return response_auth('success', 'Successfully logged In', user.encode_auth_token(user.id), 200)
                return response('failed', 'User does not exist or password is incorrect', 401)
            return response('failed', 'Missing or wrong email format', 401)
        return response('failed', 'Content-type must be json', 202)


class LogOutUser(MethodView):
    """
    Class to log out a user
    """

    def post(self):
        """
        Try to logout a user using a token
        :return:
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                return response('failed', 'Provide a valid auth token', 403)
            else:
                decoded_token_response = User.decode_auth_token(auth_token)
                if not isinstance(decoded_token_response, str):
                    token = BlackListToken(auth_token)
                    token.blacklist()
                    return response('success', 'Successfully logged out', 200)
                return response('failed', decoded_token_response, 401)
        return response('failed', 'Provide an authorization header', 403)


# Register classes as views
registration_view = RegisterUser.as_view('register')
login_view = LoginUser.as_view('login')
logout_view = LogOutUser.as_view('logout')

# Add rules for the api Endpoints
auth.add_url_rule('/auth/register', view_func=registration_view, methods=['POST'])
auth.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])
auth.add_url_rule('/auth/logout', view_func=logout_view, methods=['POST'])
