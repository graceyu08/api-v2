from compass.db.exception import *

from compass.db.models import User
from compass.db.api import database
from compass.db.api import utils

SUPPORT_FILTERS = ['email', 'admin']
DEFAULT_RESP_FIELDS = ['id', 'email', 'is_admin', 'active']
USER = 'user'
USERS = 'users'


def get_user(user_id):
    with database.session() as session:
       user = _get_user(session, user_id)
       if not user:
           raise RecordNotExists(USER, user_id)

       data = user.to_dict()
     
       user_dict = utils.wrap_to_dict(USER, data, DEFAULT_RESP_FIELDS)
    return user_dict


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


def _auth_user(session, user_id, password):
    """Authenticate this user"""
    pass
