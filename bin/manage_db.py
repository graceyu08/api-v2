#!/usr/bin/python
import os

from flask.ext.script import Manager

from compass.api import app
from compass.db.api import database
from compass.db.models import Permission
from compass.db.models import User
from compass.db.models import user_permission


app_manager = Manager(app, usage="Perform database operations")


@app_manager.command
def createdb():
    """Create database from sqlalchemy models"""
    path = '/tmp/app.db'
    if os.path.exists(path):
        os.remove(path)
    try:
        database.create_db()
    except Exception as e:
        print e
    os.chmod(path, 0o777)
