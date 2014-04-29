from compass.db.api import database
from compass.db.api import utils
from compass.db.api.utils import wrap_to_dict
from compass.db.exception import *

from compass.db import utils
from compass.db.config_validation import validate_config
#from compass.db.config_validation import extension

from compass.db.models import Cluster

SUPPORTED_FILTERS = ['name', 'adapter', 'owner']

ERROR_MSG = {
    'findNoCluster': 'Cannot find the Cluster, ID is %d',
}


@wrap_to_dict()
def get_cluster(cluster_id):

    with database.session() as session:
       cluster = _get_cluster(session, cluster_id)
       if not cluster:
           err_msg = ERROR_MSG['findNoCluster'] % cluster_id
           raise RecordNotExists(err_msg)

       info = cluster.to_dict()

    return info


@wrap_to_dict()
def list_clusters(filters=None):
    """List all users, optionally filtered by some fields"""
    if filters:
        filters = utils.get_legal_filters("cluster", filters)

    with database.session() as session:
        clusters = _list_clusters(session, filters)
        clusters_info = [cluster.to_dict() for cluster in clusters]

    return clusters_info


@wrap_to_dict
def get_cluster_config(cluster_id):
    """Get configuration info for a specified cluster"""

    with database.session() as session:
        try:
            config = _get_cluster_config(session, cluster_id)
        except RecordNotExists as ex:
            raise RecordNotExists(ex.message)

    return config


def _get_cluster_config(session, cluster_id):
    config = {}
    with session.begin(subtransactions=True):
        cluster = session.query(Cluster).filter_by(id=cluster_id).first()
        if not cluster:
            err_msg = ERROR_MSG['findNoCluster'] % cluster_id
            raise RecordNotExists(err_msg)
        config = cluster.config

    return config


def _get_cluster(session, cluster_id):
    """Get the adapter by ID"""
    with session.begin(subtransactions=True):
        cluster = session.query(Cluster).filter_by(id=cluster_id).first()

    return cluster


def _list_clusters(session, filters=None):
    """Get all adapters, optionally filtered by some fields"""

    filters = filters if filters else {}

    with session.begin(subtransactions=True):
        query = session.query(Cluster)
        if filters:
            for key in filters:
                if isinstance(filters[key], list):
                    query = query.filter(getattr(Cluster, key).in_(filters[key]))
                else:
                    query = query.filter(getattr(Cluster, key) == filters[key])

        clusters = query.all()

    return clusters


def update_cluster_config(cluster_id, config, is_os_config=True, patch=True):
    with database.session() as session:
       cluster = _get_cluster(session, cluster_id)

       is_valid, message = validate_config(session, cluster.adapter_id,
                                           cluster.os_id, config, patch)
       if not is_valid:
          raise InvalidParameter(message)
       
       # For addtional validation, you can define functions in extension,
       # for example: 
       # os_name = get_os(cluster.os_id)['name']
       # if getattr(extension, os_name):
       #    func = getattr(getattr(extension, os_name), 'validate_config')
       #    if not func(session, os_id, config, patch):
       #        return False
       
       if is_os_config:
           os_config = cluster.os_global_config
           utils.merge_dict(os_config, config)
           cluster.os_global_config = config
           return os_config
       else:
           package_config = cluster.package_global_config
           utils.merge_dict(package_config, config)
           cluster.package_global_config = package_config
           return package_config
