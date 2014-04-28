"""Provider interface to manipulate database."""
import logging

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from threading import local

from compass.db import models
#from compass.utils import setting_wrapper as setting

SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/app.db"
ENGINE = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
SESSION = sessionmaker()
SESSION.configure(bind=ENGINE)
SCOPED_SESSION = scoped_session(SESSION)
SESSION_HOLDER = local()

models.BASE.query = SCOPED_SESSION.query_property()

#Default permissions for Permission table
DEFAULT_PERMS = [
    {"name": "create_user", "alias": "create a user"},
    {"name": "delete_user", "alias": "delete a user"},
    {"name": "change_permission", "alias": "change permissions of a user"},
    {"name": "delete_cluster", "alias": "delete a cluster"}
]

# Adapter
ADAPTERS = ['openstack', 'ceph', 'centos', 'ubuntu']

# OS
OS = ['CentOs', 'Ubuntu']

# adapter_os (adater_id, os_id)
ADAPTER_OS_DEF = {
    1: [1,2],
    2: [1],
    3: [1],
    4: [2]
}

# OS config metatdata
OS_CONFIG_META_DEF = [
        {"name": "os_config", "p_id": None, 'os_id': None},
        {"name": "general", "p_id": 1, 'os_id': None},
        {"name": "network", "p_id": 1, 'os_id': None},
        {"name": "$interface", "p_id": 3, 'os_id': None},
        {"name": "ext_example_meta", "p_id": 1, 'os_id': 2}
]
# OS config field
OS_CONFIG_FIELD_DEF = [
    {"name": "languge", "validator": None, 'is_required': True, 'ftype': 'str'},
    {"name": "timezone", "validator": None, 'is_required': True, 'ftype': 'str'},
    {"name": "ip", "validator": 'is_valid_ip', 'is_required': True, 'ftype': 'str'},
    {"name": "netmask", "validator": 'is_valid_netmask', 'is_required': True, 'ftype': 'str'},
    {"name": "gateway", "validator": 'is_valid_gateway', 'is_required': True, 'ftype': 'str'},
    {"name": "ext_example_field", "validator": None, 'is_required': True, 'ftype': 'str'}
]

# OS config metadata field (metadata_id, field_id)
COMMON_OS_CONFIG_META_FIELD_DEF = {
    2: [1, 2],
    4: [3, 4, 5],
    5: [6]
}

def init(database_url):
    """Initialize database.

    :param database_url: string, database url.
    """
    global ENGINE
    global SCOPED_SESSION
    ENGINE = create_engine(database_url, convert_unicode=True)
    SESSION.configure(bind=ENGINE)
    SCOPED_SESSION = scoped_session(SESSION)
    models.BASE.query = SCOPED_SESSION.query_property()


def in_session():
    """check if in database session scope."""
    if hasattr(SESSION_HOLDER, 'session'):
        return True
    else:
        return False


@contextmanager
def session():
    """database session scope.

       .. note::
       To operate database, it should be called in database session.
    """
    if hasattr(SESSION_HOLDER, 'session'):
        logging.error('we are already in session')
        raise Exception('session already exist')
    else:
        new_session =  SCOPED_SESSION()
        SESSION_HOLDER.session = new_session

    try:
        yield new_session
        new_session.commit()
    except Exception as error:
        new_session.rollback()
        logging.error('failed to commit session')
        logging.exception(error)
        raise error
    finally:
        new_session.close()
        SCOPED_SESSION.remove()
        del SESSION_HOLDER.session


def current_session():
    """Get the current session scope when it is called.

       :return: database session.
    """
    try:
        return SESSION_HOLDER.session
    except Exception as error:
        logging.error('It is not in the session scope')
        logging.exception(error)
        raise error


def create_db():
    """Create database."""
    models.BASE.metadata.create_all(bind=ENGINE)
    with session() as _session:
        # Initialize default user
        user = models.User(email='admin@abc.com',
                           password='admin')#,is_admin=True)
        logging.info('Init user: %s, %s' % (user.email, user.get_password()))
        _session.add(user)

        # Initialize default permissions
        permissions = []
        for perm in DEFAULT_PERMS:
            permissions.append(models.Permission(**perm))

        _session.add_all(permissions)

        # Populate adapter table
        adapters = []
        for name in ADAPTERS:
            adapters.append(models.Adapter(name=name))
        _session.add_all(adapters)


        # Populate os table
        oses = []
        for name in OS:
            oses.append(models.OperatingSystem(name=name))
        _session.add_all(oses)

        # Populate adapter_os table 
        for key in ADAPTER_OS_DEF:
            adapter = adapters[key-1]
            for os_id in ADAPTER_OS_DEF[key]:
                os = oses[os_id-1]
                adapter.support_os.append(os)
 
        
        # Populate OS config metatdata
        os_meta= []
        for key in OS_CONFIG_META_DEF:
            if key['p_id'] is None:
                meta = models.OSConfigMetadata(name=key['name'],
                                               os_id=key['os_id'])
            else:
                parent = os_meta[key['p_id']-1]
                meta = models.OSConfigMetadata(name=key['name'],
                                                os_id=key['os_id'],
                                                parent=parent)
            os_meta.append(meta)

        _session.add_all(os_meta)

        
        # Populate OS config field
        os_fields = []
        for field in OS_CONFIG_FIELD_DEF:
            os_fields.append(models.OSConfigField(
                field=field['name'], validator=field['validator'],
                is_required=field['is_required'], ftype=field['ftype']))
        _session.add_all(os_fields)

         
        # Populate common OS config metatdata field
        for meta_id in COMMON_OS_CONFIG_META_FIELD_DEF:
            meta = os_meta[meta_id-1]
            for field_id in COMMON_OS_CONFIG_META_FIELD_DEF[meta_id]:
                field = os_fields[field_id-1]
                meta.fields.append(field)
        
def drop_db():
    """Drop database."""
    models.BASE.metadata.drop_all(bind=ENGINE)


def create_table(table):
    """Create table.

    :param table: Class of the Table defined in the model.
    """
    table.__table__.create(bind=ENGINE, checkfirst=True)


def drop_table(table):
    """Drop table.

    :param table: Class of the Table defined in the model.
    """
    table.__table__.drop(bind=ENGINE, checkfirst=True)
