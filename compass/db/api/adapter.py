from sqlalchemy import or_

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
    'findNoAdapter': 'Cannot find the Adapter, ID is %d'
}


@wrap_to_dict()
def get_adapter(adapter_id):
    return_config_schema = True
    os_id = 2
    with database.session() as session:
       adapter = _get_adapter(session, adapter_id)
       if not adapter:
           err_msg = ERROR_MSG['findNoAdapter'] % adapter_id
           raise RecordNotExists(err_msg)

       adapter_info = adapter.to_dict()
       """
       if return_role:
           roles = {
               "roles": adapter.roles
           }
           adapter_info.update(roles)
       """
       if return_config_schema and os_id:
           schema = {}
           schema.update(_get_adapter_os_config_schema(session, os_id))
           #schema.update(_get_adapter_package_config_schema(session, adapter_id))

           adapter_info.update({"config_schema": schema})

    return adapter_info


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

    filters = filters if filters else {}

    with session.begin(subtransactions=True):
        query = session.query(Adapter)
        if filters:
            for key in filters:
                if isinstance(filters[key], list):
                    query = query.filter(getattr(Adapter, key).in_(filters[key]))
                else:
                    query = query.filter(getattr(Adapter, key) == filters[key])

        adapters = query.all()

    return adapters


def _get_adapter_package_config_schema(session):
    pass

#TODO:grace
def _get_adapter_os_config_schema(session, os_id):
    with session.begin(subtransactions=True):
        root = session.query(OSConfigMetadata).filter_by(name="os_config").first()
        stack = [root]
        
        schema = {}
        prev = None
        while len(stack) > 0:
            curr = stack[-1]
            if prev and prev.parent == curr:

                if curr.name in schema:
                    if curr != root and curr.parent.name in schema:
                        tmp = schema[curr.name]
                        del schema[curr.name]
                        schema[curr.parent.name].update({curr.name: tmp})
                
                stack.pop()
            else:
                children = curr.children
                if children:
                    stack.extend(children)
                else:
                    fields = curr.fields
                    fields_name = [field.field for field in fields]
                    if curr.parent.name in schema:
                        schema[curr.parent.name].update({curr.name: fields_name})
                    else:    
                        schema[curr.parent.name] = {curr.name: fields_name}
                    stack.pop()
            prev = curr
        
        return schema
