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

        return utils.make_json_response(200, {user_data})

api.add_resource(User, '/users/<int:user_id>')


if __name__ == '__main__':
    v1_app.run(debug=True)
