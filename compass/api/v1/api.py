# Copyright 2014 Huawei Technologies Co. Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Define all the RestfulAPI entry points."""
import logging
import simplejson as json

from flask import Blueprint
from flask import request

from flask.ext.restful import Api
from flask.ext.restful import Resource

from compass.api import exception
from compass.api import utils
from compass.db import db_api
from compass.db.exception import RecordNotExists

v1_app = Blueprint('v1_app', __name__)
api = Api(v1_app)
PREFIX = '/v1.0'


@v1_app.route('/users', methods=['GET'])
def list_users():
    
    emails = request.args.getlist('email')
    is_admin = request.args.get('admin')

    filters = {}

    if emails:
        filters['email'] = emails
    
    if is_admin is not None:
        if is_admin == 'true':
            filters['is_admin'] = True
        elif is_admin == 'false':
            filters['is_admin'] = False
            
    users_list = db_api.list_users(filters)

    return utils.make_json_response(200, users_list)


class User(Resource):
    ENDPOINT = PREFIX + '/users'

    def get(self, user_id):
        """Get user's information for specified ID."""
        try:
            user_data = db_api.get_user(user_id)
            logging.debug("user_data is===>%s", user_data)

        except RecordNotExists as ex:
            error_msg = ex.message
            return exception.handle_not_exist(
                exception.ItemNotFound(error_msg)
            )

        return utils.make_json_response(200, user_data)

    def post(self):
        """Create a new user"""
        pass

    def put(self, user_id):
        """Update user information(firstname, lastname)"""
        pass

    def delete(self, user_id):
        """Delete a user"""
        pass

@v1_app.route('/adapters', methods=['GET'])
def list_adapters():
    names = request.args.getlist('name')
    filters = {}
    if names:
        filters['name'] = names

    adapters_list = db_api.list_adapters(filters)
    return utils.make_json_response(200, adapters_list)


@v1_app.route('/adapters/<int:adapter_id>/config-schema', methods=['GET'])
def get_adapter_config_schema(adapter_id):
    os_id = request.args.get('os-id')
    schema=None
    try:
        schema = db_api.get_adapter(adapter_id)
    except Exception as e:
        print e

    return utils.make_json_response(200, schema)


class Adapter(Resource):
    ENDPOINT = PREFIX + "/adapters"

    def get(self, adapter_id):
        try:
            adapter_info = db_api.get_adapter(adapter_id)
        except RecordNotExists as ex:
            error_msg = ex.message
            return exception.handle_not_exist(
                exception.ItemNotFound(error_msg)
            )
        return utils.make_json_response(200, adapter_info)

api.add_resource(User,
                 '/users',
                 '/users/<int:user_id>')
api.add_resource(Adapter,
                 '/adapters',
                 '/adapters/<int:adapter_id>')

if __name__ == '__main__':
    v1_app.run(debug=True)
