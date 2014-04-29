from compass.db.api import database
from compass.db.api import utils
from compass.db.api.utils import wrap_to_dict
from compass.db.exception import *

from compass.db import validator

from compass.db.models import Cluster
from compass.db.models import OSConfigMetadata
#from compass.db.models import AdapterConfigMetadata


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

       info = adapter.to_dict()

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
        except RecordNotExists:
            raise RecordNotExists

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


def update_cluster_config(cluster_id, config, patch=True):
    pass
