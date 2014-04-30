#from sqlalchemy import or_

from compass.db.api import database
from compass.db.api import utils
from compass.db.api.utils import wrap_to_dict
from compass.db.exception import *
from compass.db.models import Adapter
from compass.db.models import OSConfigMetadata
#from compass.db.models import AdapterConfigMetadata


SUPPORTED_FILTERS = ['name']
ADAPTER = 'adapter'

ERROR_MSG = {
    'findNoAdapter': 'Cannot find the Adapter, ID is %d',
    'findNoOs': 'Cannot find OS, ID is %d'
}


@wrap_to_dict()
def get_adapter(adapter_id, return_roles=False):

    with database.session() as session:
       adapter = _get_adapter(session, adapter_id)
       if not adapter:
           err_msg = ERROR_MSG['findNoAdapter'] % adapter_id
           raise RecordNotExists(err_msg)
       info = None

       if return_roles:
           roles = adapter.roles
           info = [role.name for role in roles]

    return info


@wrap_to_dict()
def get_adapter_config_schema(adapter_id,
                              os_id,
                              os_config_only=False,
                              package_config_only=False):
    schema = {}
    with database.session() as session:
        adapter = _get_adapter(session, adapter_id)
        if not adapter:
            err_msg = ERROR_MSG['findNoAdapter'] % adapter_id
            raise RecordNotExists(err_msg)

        # TODO(Grace): This function signature has a flaw (in theory).
        # os_config_only and package_config_only is not of equal importance.
        # For example, it is not easy to define a behavior if
        # os_config_only=True, and package_config_only=True
        # With your current implementation, this case is allowed and
        # only os_config_only takes effect.

        # An alternative implementation with simplier logic, but different
        # behavior if both args are set to true.
        """
           if not os_config_only:
             schema.update(_get_adapter_package_config_schema(session, adapter_id))

           if not package_config_only:
             schema.update(_get_adapter_os_config_schema(session, os_id))
        """
        if os_config_only:
            schema.update(_get_adapter_os_config_schema(session, os_id))
        elif package_config_only:
            pass
            schema.update(_get_adapter_package_config_schema(session, adapter_id))
        else:
            schema.update(_get_adapter_os_config_schema(session, os_id))
            schema.update(_get_adapter_package_config_schema(session, adapter_id))

    return schema


@wrap_to_dict()
def list_adapters(filters=None):
    """List all users, optionally filtered by some fields"""
    if filters:
        filters = utils.get_legal_filters(ADAPTER, filters)

    with database.session() as session:
        adapters = _list_adapters(session, filters)
        adapters_list = [adapter.to_dict() for adapter in adapters]

    return adapters_list


def _get_adapter(session, adapter_id):
    """Get the adapter by ID"""
    with session.begin(subtransactions=True):
        adapter = session.query(Adapter).filter_by(id=adapter_id).first()

    return adapter


def _list_adapters(session, filters=None):
    """Get all adapters, optionally filtered by some fields"""

    # TODO(Grace): Simplier if using this:
    # filters = filters or {}
    filters = filters if filters else {}

    with session.begin(subtransactions=True):
        query = session.query(Adapter)
        # TODO(Grace): There is no need to have if- here.
        # simply do for-loop. It is no-op if filters is empty
        if filters:
            for key in filters:
                if isinstance(filters[key], list):
                    query = query.filter(getattr(Adapter, key).in_(filters[key]))
                else:
                    query = query.filter(getattr(Adapter, key) == filters[key])

        adapters = query.all()

    return adapters


def _get_adapter_package_config_schema(session):
    return {}


# TODO(Grace): TMP method
def _get_adapter_os_config_schema(session, os_id):
    output_dict = {}

    with session.begin(subtransactions=True):
        root = session.query(OSConfigMetadata).filter_by(name="os_config").first()


        os_config_dict = {"_name" : "os_config" }
        output_dict["os_config"] = os_config_dict
        _get_adapter_os_config_internal(root, os_config_dict, output_dict, os_id)

    return output_dict

### A recursive function
# This assumes that only leaf nodes have field entry and that
# an intermediate node in config_metadata table does not have field entries
def _get_adapter_os_config_internal(node, current_dict, parent_dict, os_id):
    children = node.children

    if children:
        for c in children:
            if c.os_id is None or c.os_id == os_id:
                child_dict = {"_name" : c.name}
                current_dict[c.name] = child_dict
                _get_adapter_os_config_internal(c, child_dict, current_dict, os_id)
        del current_dict["_name"]
    else:
        fields = node.fields
        fields_dict = {}

        for field in fields:
            info = field.to_dict()
            name = info['field']
            del info['field']
            fields_dict[name] = info

        parent_dict[current_dict["_name"]] = fields_dict
