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
import netaddr
import re
import simplejson as json
import sys

"""
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
#from flask import session as app_session
from flask import url_for
"""
from flask.ext.restful import Resource
#from sqlalchemy.sql import and_
#from sqlalchemy.sql import or_

#from compass.api.v1 import v1_app as app
#from compass.api import app
#from compass.api import auth
from compass.api import exception
#from compass.api import login_manager
from compass.api import utils
#from compass.db import database
#new
from compass.db import db_api
from compass.db.exception import RecordNotExists
#new-end

from flask import Blueprint
from flask.ext.restful import Api
v1_app = Blueprint('v1_app', __name__)
api = Api(v1_app)

"""
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user

from flask.ext.wtf import Form
from wtforms.fields import BooleanField
from wtforms.fields import PasswordField
from wtforms.fields import TextField
from wtforms.validators import Required
"""
'''
@login_manager.header_loader
def load_user_from_token(token):
    """Return a user object from token."""
    duration = app.config['REMEMBER_COOKIE_DURATION']
    max_age = 0
    if sys.version_info > (2, 6):
        max_age = duration.total_seconds()
    else:
        max_age = (duration.microseconds + (
            duration.seconds + duration.days * 24 * 3600) * 1e6) / 1e6

    user_id = auth.get_user_info_from_token(token, max_age)
    if not user_id:
        logging.info("No user can be found from the token!")
        return None

    user = db_api.get_user(user_id)
    return user


@login_manager.user_loader
def load_user(user_id):
    """Load user from user ID."""
    return db_api.get_user(user_id)


@app.route('/restricted')
def restricted():
    return render_template('restricted.jinja')


@app.errorhandler(403)
def forbidden_403(exception):
    """Unathenticated user page."""
    return render_template('forbidden.jinja'), 403


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have logged out!')
    return redirect(url_for('index'))


@app.route('/')
def index():
    """Index page."""
    return render_template('index.jinja')


@app.route('/token', methods=['POST'])
def get_token():
    """Get token from email and passowrd after user authentication."""
    data = json.loads(request.data)
    email = data['email']
    password = data['password']

    user = auth.authenticate_user(email, password)
    if not user:
        error_msg = "User cannot be found or email and password do not match!"
        return exception.handle_invalid_user(
            exception.Unauthorized(error_msg)
        )

    token = user.get_auth_token()
    login_user(user)

    return utils.make_json_response(
        200, {"status": "OK", "token": token}
    )


class LoginForm(Form):
    """Define login form."""
    email = TextField('Email', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember me', default=False)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            user = auth.authenticate_user(email, password)
            if not user:
                flash('Wrong username or password!', 'error')
                return render_template('login.jinja', form=form)

            if login_user(user, remember=form.remember.data):
                # Enable session expiration if user didnot choose to be
                # remembered.
                app_session.permanent = not form.remember.data
                flash('Logged in successfully!', 'success')
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash('This username is disabled!', 'error')

        return render_template('login.jinja', form=form)

'''

class User(Resource):
    ENDPOINT = '/users'

    def get(self, user_id):
        """Get user's information for specified ID."""
        #resp = {}
        try:
            user_data = db_api.get_user(user_id)
            logging.debug("user_data is===>%s", user_data)

        except RecordNotExists as ex:
            error_msg = ex.message
            return exception.handle_not_exist(
                exception.ItemNotFound(error_msg)
            )

        return utils.make_json_response(
            200, {"user": user_data}
        )

api.add_resource(User, '/users/<int:user_id>')

"""
utils.add_resource(User,
                   '/v1.0/users',
                   '/v1.0/users/<int:user_id>')

"""
#if __name__ == '__main__':
#    app.run(debug=True)
