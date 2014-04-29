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

from compass.api.exception import *
from compass.api import utils

from compass.db import db_api
from compass.db.exception import RecordNotExists
from compass.db.exception import InvalidParameter


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
            return handle_not_exist(
                ItemNotFound(error_msg)
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


@v1_app.route('/adapters/<int:adapter_id>/os/<int:os_id>/config-schema',
              methods=['GET'])
def get_adapter_config_schema(adapter_id, os_id):

    try:
        schema = db_api.get_adapter_config_schema(adapter_id, os_id)
    except RecordNotExists as ex:
        return handle_not_exist(
            ItemNotFound(ex.message)
        )

    return utils.make_json_response(200, schema)


@v1_app.route('/adapters/<int:adapter_id>/roles', methods=['GET'])
def get_adapter_roles(adapter_id):
    try:
        roles = db_api.get_adapter(adapter_id, True)
    except RecordNotExists as ex:
        return handle_not_exist(
            ItemNotFound(ex.message)
        )

    return utils.make_json_response(200, roles)


class Adapter(Resource):
    ENDPOINT = PREFIX + "/adapters"

    def get(self, adapter_id):
        try:
            adapter_info = db_api.get_adapter(adapter_id)
            print adapter_info
        except RecordNotExists as ex:
            error_msg = ex.message
            return handle_not_exist(
                ItemNotFound(error_msg)
            )
        return utils.make_json_response(200, adapter_info)


class Cluster(Resource):
    def get(self, cluster_id):
        try:
            cluster_info = db_api.get_cluster(cluster_id)

        except RecordNotExists as ex:
            error_msg = ex.message
            return handle_not_exist(
                ItemNotFound(error_msg)
            )
        return utils.make_json_response(200, cluster_info)


@v1_app.route('/clusters/<int:cluster_id>/config', methods=['PUT', 'PATCH'])
def add_cluster_config(cluster_id):
        config = json.loads(request.data)
        if not config:
            return handle_bad_request(
                BadRequest("Config cannot be None!")
            )

        result = None
        try:
            if "os_config" in config:
                result = db_api.update_cluster_config(cluster_id, config,
                                                      patch=request.method=='PATCH')
            elif "package_config" in config:
                result = db_api.update_cluster_config(cluster_id, config,
                                                      is_os_config=False,
                                                      patch=request.method=='PATCH')
        except InvalidParameter as ex:
            return handle_bad_request(
                BadRequest(ex.message)
            )
        return utils.make_json_response(200, result)


api.add_resource(User,
                 '/users',
                 '/users/<int:user_id>')
api.add_resource(Adapter,
                 '/adapters',
                 '/adapters/<int:adapter_id>')
api.add_resource(Cluster,
                 '/clusters',
                 '/clusters/<int:cluster_id>')


@v1_app.errorhandler(ItemNotFound)
def handle_not_exist(error, failed_objs=None):
    """Handler of ItemNotFound Exception."""

    message = {'type': 'itemNotFound',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(404, message)


@v1_app.errorhandler(Unauthorized)
def handle_invalid_user(error, failed_objs=None):
    """Handler of Unauthorized Exception."""

    message = {'type': 'unathorized',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(401, message)

@v1_app.errorhandler(Forbidden)
def handle_no_permission(error, failed_objs=None):
    """Handler of Forbidden Exception."""

    message = {'type': 'Forbidden',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(403, message)


@v1_app.errorhandler(BadRequest)
def handle_bad_request(error, failed_objs=None):
    """Handler of badRequest Exception."""

    message = {'type': 'badRequest',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(400, message)


if __name__ == '__main__':
    v1_app.run(debug=True)
