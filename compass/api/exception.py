#from compass.api import app
#from compass.api import utils


class ItemNotFound(Exception):
    """Define the exception for referring non-existing object."""
    def __init__(self, message):
        super(ItemNotFound, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class BadRequest(Exception):
    """Define the exception for invalid/missing parameters or a user makes
       a request in invalid state and cannot be processed at this moment.
    """
    def __init__(self, message):
        super(BadRequest, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class Unauthorized(Exception):
    """"""
    def __init__(self, message):
        super(Unauthorized, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class UserDisabled(Exception):
    """"""
    def __init__(self, message):
        super(UserDisabled, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class Forbidden(Exception):
    """"""
    def __init__(self, message):
        super(Forbidden, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class BadMethod(Exception):
    """"""
    def __init__(self, message):
        super(BadMethod, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class ConflictObject(Exception):
    """"""
    def __init__(self, message):
        super(ConflictObject, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)

'''
@app.errorhandler(ItemNotFound)
def handle_not_exist(error, failed_objs=None):
    """Handler of ItemNotFound Exception."""

    message = {'type': 'itemNotFound',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(404, message)


@app.errorhandler(Unauthorized)
def handle_invalid_user(error, failed_objs=None):
    """Handler of Unauthorized Exception."""

    message = {'type': 'unathorized',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(401, message)


@app.errorhandler(Forbidden)
def handle_no_permission(error, failed_objs=None):
    """Handler of Forbidden Exception."""

    message = {'type': 'Forbidden',
               'message': error.message}

    if failed_objs and isinstance(failed_objs, dict):
        message.update(failed_objs)

    return utils.make_json_response(403, message)
'''
