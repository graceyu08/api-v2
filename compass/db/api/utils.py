def wrap_to_dict(name, data, keywords):
    """Helper for warpping db object into dictionary"""
    wrapper_dict = {}

    for key in keywords:
        if key in data:
            wrapper_dict[key] = data[key]

    return wrapper_dict
