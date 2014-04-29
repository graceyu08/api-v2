#!/usr/bin/python
import os

from flask.ext.script import Manager

from compass.api import app
from compass.db.api import database

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


if __name__ == "__main__":
    app_manager.run()
