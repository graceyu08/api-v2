import logging


SUPPORTED_FILTERS = {
    "user": ['email', 'is_admin'],
    "adapter": ['name']
}


def wrap_to_dict(support_keys=None):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            obj = func(*args, **kwargs)
            obj_info = None
            if isinstance(obj, list):
                obj_info = [_wrapper_dict(o, support_keys) for o in obj]
            else:
                obj_info = _wrapper_dict(obj, support_keys)

            return obj_info
        return wrapped_f
    return wrap


def _wrapper_dict(data, support_keys=None):
    """Helper for warpping db object into dictionary"""
    if support_keys is None:
        return data

    info = {}
    for key in support_keys:
        if key in data:
            info[key] = data[key]

    return info


def get_legal_filters(table_name, filters):
    """Get legal filters"""
    legal_filters = {}
    try:
        supported_filters = SUPPORTED_FILTERS[table_name]
    except KeyError:
        logging.debug("Cannot find supported filters for table %s", table_name)
        return None

    for name in filters:
        if name in supported_filters:
            legal_filters[name] = filters[name]

    return legal_filters
