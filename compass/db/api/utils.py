def wrapper_dict(data, support_keys):
    """Helper for warpping db object into dictionary"""
    info = {}

    for key in support_keys:
        if key in data:
            info[key] = data[key]

    return info
