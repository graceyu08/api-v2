from compass.db.exception import *

from compass.db.models import User
from compass.db.api import database
from compass.db.api import utils

SUPPORT_FILTERS = ['email', 'admin']
DEFAULT_RESP_FIELDS = ['id', 'email', 'is_admin', 'active', 'firstname',
                       'lastname', 'created_at', 'last_login_at']
USER = 'user'
USERS = 'users'


def get_user(user_id):
    with database.session() as session:
       user = _get_user(session, user_id)
       if not user:
           raise RecordNotExists(USER, user_id)

       user = utils.wrapper_dict(user.to_dict(), DEFAULT_RESP_FIELDS)
    return user


def _get_user(session, user_id):
    """Get the user by ID"""
    with session.begin(subtransactions=True):
        user = session.query(User).filter_by(id=user_id).first()

    return user


def _list_users(session, filters=None):
    """Get all users, optionally filtered by some fields"""
    pass


def _add_user(session, **kwargs):
    """Create a user"""
    pass


def _update_user(session, user_id, **kwargs):
    """Update user information"""
    pass


def _add_permission(session, user_id, permissions):
    """Add permissions for the user"""
    pass


def _remove_permission(session, user_id, permissions):
    """Remove permissions for the user"""
    pass


def _delete_user(session, user_id):
    """Delete a user"""
    pass


def _list_permissions(session, user_id):
    """Get all permissions for the user"""
    pass


def _get_token(session, user_id):
    """Generate a token for the user"""
    pass
