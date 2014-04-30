"""
Default config validation function
"""

from sqlalchemy import or_
from compass.db import validator

from compass.db.models import OSConfigMetadata
from compass.db.models import OSConfigField

# TODO(Grace): Personally, I prefer not to define common functions in __init__.py
#
def validate_config(session, adapter_id, os_id, config, patch=True):

    root_elems = ["os_config", "package_config"]


    elem = config.keys()[0]
    # TODO(Grace): Need to re-work here. len()!=1 chcking is too late because
    # be above line assumes config.keys() is a least of length 1
    if len(config.keys()) != 1 or elem not in root_elems:
        return (False, "Only one root element can be accepted, given two.")

    if elem == 'os_config':
        return _validate_config_helper(session, "os_id", os_id, config, patch)
    else:
        return _validate_config_helper(session, "adapter_id", adapter_id, config, patch)

def _validate_config_helper(session, id_name, id_value, config, patch=True):

    # TODO(Grace): This could be move to module level constant dict.
    # MAPPER =  ...
    mapper = {
        "os_id": {
            "metaTable": OSConfigMetadata,
            "metaFieldTable": OSConfigField
        }

        #"adapter_id": {
        #    "metaTable": AdapterConfigMetadata,
        #    "metaFieldTable": AdapterConfigField
        #}
    }
    # TODO(Grace): check key id_name exists.
    meta_table = mapper[id_name]['metaTable']
    meta_field_table = mapper[id_name]['metaFieldTable']
    with session.begin(subtransactions=True):
        for elem in config:
            obj = session.query(meta_table).filter(getattr(meta_table, 'name')==elem)\
                         .filter(or_(getattr(meta_table, id_name)==None,
                                     getattr(meta_table, id_name)==id_value)).first()
            if not obj:
                if "_type" in config[elem]:
                    obj = session.query(meta_table).filter_by(name=config[elem]['_type']).first()
                    print "obj ===> %s" % obj.name
                    if not obj:
                        err_msg = ("Invalid metatdata '%s' or missing '_type'"
                                   "to indicate this is a variable metatdata." % elem)
                        return (False, err_msg)
                    del config[elem]['_type']
                else:
                    return (False, "Invalid metadata '%s'!" % elem)

            fields = obj.fields
            print "fields ===> %s" % [field.field for field in fields]
            if fields:
                field_config = config[elem]

                for key in field_config:
                    field = session.query(meta_field_table).filter_by(field=key).first()
                    if not field:
                        # The field is not in schema
                        return (False, "Invalid field '%s'!" % key)

                    value = field_config[key]
                    if field.is_required and value is None:
                        # The value of this field in schema is required, but
                        # now it is None
                        return (False, "The value of field '%s' cannot be null" % key)

                    # TODO(Grace): I believe we can get rid of checking on None.
                    if field.validator and value is not None:
                        func = getattr(validator, field.validator)
                        if not func or not func(value):
                            return (False, "The value of the field '%s' is invalid format!" % key)

                if not patch:
                    for field in fields:
                        name = field.field
                        if field.is_required and name not in field_config:
                            return (False, "Missing required field '%s'" % name)

            else:
                # TODO(Grace): I have a preference to put this block upfront.
                # This is so that we can get ride of if-else

                # if not fields:
                #    ....
                #    return
                #
                # the rest of code here.

                is_valid, message = _validate_config_helper(session, id_name,
                                                            id_value, config[elem], patch)
                if not is_valid:
                    return (False, message)

        return (True, None)
