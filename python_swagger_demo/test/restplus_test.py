#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/14 下午2:38
# @Author  : （Vian）716517@qq.com
# @Site    : 
# @File    : restplus_test.py
# @Software: PyCharm

"""
Standalone test class that sets up a basic API that supports both JSON and XML. It is a single class setup so
that it is easy to follow.

Some quick pointers:
- If a multi line docstring is present in any function, it will be displayed in the Swagger UI as
  "Implementation Notes". Use the Markdown syntax to format these notes, see
  https://daringfireball.net/projects/markdown/syntax.
- Namespaces allow the API operations to be split into separate files, each defining a part of the API with a
  different URL prefix.
- For url_for to work with namespaces and blueprints the param "endpoint" must be set on ns.route.
  Example: @ns.route('/', endpoint='users')
"""
from flask import Flask, Blueprint, url_for, make_response, jsonify
from flask_restplus import Api, Resource, fields

# needs: pip install python-simplexml
from simplexml import dumps

# Setup application

url_prefix = '/api/v2_0'
version = '2.0'
doc = '/apidoc/'
bp_name = 'api'
app = Flask(__name__)
blueprint = Blueprint(bp_name, __name__, url_prefix=url_prefix)


# Convenience functions

def print_url_for(method, ep_name, **kwargs):
    if len(kwargs) == 0:
        result = url_for(bp_name + '.' + ep_name)
    else:
        result = url_for(bp_name + '.' + ep_name, **kwargs)
    print(' ---- {method} - url_for={url_for}'.format(method=method, url_for=result))


# Setup DAO

class UserDAO(object):
    def __init__(self):
        self.counter = 0
        self.users = []

    def get(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user
        api.abort(404, "User {} doesn't exist".format(user_id))

    def create(self, data):
        user = data
        user['id'] = self.counter = self.counter + 1
        self.users.append(user)
        return user

    def update(self, user_id, data):
        user = self.get(user_id)
        user.update(data)
        return user

    def delete(self, user_id):
        user = self.get(user_id)
        self.users.remove(user)


DAO = UserDAO()
DAO.create({'first_name': 'John', 'last_name': 'Doe'})
DAO.create({'first_name': 'Jane', 'last_name': 'Doe'})
DAO.create({'first_name': 'Scooby', 'last_name': 'Doo'})


# Helper functions

def output_xml(data, code, headers=None):
    """ Makes a Flask response with a XML encoded body. """
    resp = make_response(dumps({'response': data}), code)
    resp.headers.extend(headers or {})
    return resp


# Setup API operations

api = Api(blueprint, doc=doc, version=version)
# Enable XML as response content time
api.representations['application/xml'] = output_xml

# Expand the Swagger UI when it is loaded: list or full
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
# Globally enable validating
app.config['RESTPLUS_VALIDATE'] = True
# Enable or disable the mask field, by default X-Fields
app.config['RESTPLUS_MASK_SWAGGER'] = False

# Used to document the user model
# CHeck: http://flask-restplus.readthedocs.io/en/0.8.2/documenting.html?highlight=RESTPLUS_VALIDATE
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The users unique identifier'),
    'first_name': fields.String(required=True, description='The users first name'),
    'last_name': fields.String(required=True, description='The users last name')
})

ns = api.namespace('users', description='desc')
ep_1 = 'users'
ep_2 = 'user'


# Collection endpoint
@ns.route('/', endpoint=ep_1)
class UserCollection(Resource):
    """
    Retrieves a list of all users and creates a new user.
    """

    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    @ns.response(200, 'User found')
    @api.marshal_with(user_model)
    def get(self):
        """
        Retrieves a list of all users.
        """
        print_url_for('GET', ep_1)
        return DAO.users, 200

    @ns.doc('create_users')
    @ns.expect(user_model)
    @ns.marshal_with(user_model, code=201)
    @ns.response(201, 'User created')
    def post(self):
        """
        Creates a new user.
        """
        print_url_for('POST', ep_1)
        return DAO.create(api.payload), 201


# Resource endpoint
@ns.route('/<int:user_id>', endpoint=ep_2)
@ns.response(404, 'User not found')
@ns.param('user_id', 'The user identifier')
class UserResource(Resource):
    """
    Retrieves a single user, update a user and delete a user.
    """

    @ns.doc('get_user')
    @ns.marshal_with(user_model)
    @ns.response(200, 'User found')
    def get(self, user_id):
        """
        Retrieve a single user.
        """
        print_url_for('GET', ep_1)
        print_url_for('GET', ep_2, user_id=user_id)
        return DAO.get(user_id), 200

    @ns.doc('update_user')
    @ns.expect(user_model)
    @ns.response(201, 'User updated')
    def put(self, user_id):
        """
        Update a user.

        Use this method to change the name of an user.
        * Specify the unique identifier of the user to modify as user_id parameter in the query string of the URI.
        ```
        http://<domain>/<uri>?user_id=<id>
        ```
        * Send a JSON object with the new first name and last name in the request body.
        ```
        {
          "first_name": "New first name",
          "last_name": "New last name"
        }
        ```
        """
        print_url_for('PUT', ep_1)
        print_url_for('PUT', ep_2, user_id=user_id)
        return DAO.update(user_id, api.payload)

    @ns.doc('delete_user')
    @ns.marshal_with(user_model)
    @ns.response(204, 'User deleted')
    def delete(self, user_id):
        """
        Delete a user.
        """
        print_url_for('DELETE', ep_1)
        print_url_for('DELETE', ep_2, user_id=user_id)
        DAO.delete(user_id)
        return None, 204


app.register_blueprint(blueprint)

if __name__ == '__main__':
    print('>>>>> Starting server at http://localhost:8080{url_prefix}{doc}'.format(url_prefix=url_prefix, doc=doc))
    app.run(port=8080, debug=True)
