"""Custom exception"""
class RecordNotExists(Exception):
    """Define the exception for referring non-existing object in DB"""
    def __init__(self, obj_name, obj_id=None):
        message = ''
        if obj_id:
            message = "Cannot find the %s which ID is %d" % (obj_name, obj_id)
        else:
            message = "Cannot find the %s" % obj_name

        super(RecordNotExists, self).__init__(message)
        self.message = message


class RecordExists(Exception):
    """Define the exception for trying to insert an existing object in DB"""
    def __init__(self, obj_name, obj_id):
        message = "%s, which id is %s, already exists!" % (obj_name, obj_id)
        super(RecordExists, self).__init__(message)
        self.message = message

