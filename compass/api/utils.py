"""Utils for API usage."""
import netaddr
import re

from flask.ext.restful import Api
from flask import make_response
import simplejson as json

#from compass.api import app


#API = Api(app)


def make_json_response(status_code, data):
    """Wrap json format to the reponse object."""

    result = json.dumps(data, indent=4) + '\r\n'
    resp = make_response(result, status_code)
    resp.headers['Content-type'] = 'application/json'
    return resp


def make_csv_response(status_code, csv_data, fname):
    """Wrap CSV format to the reponse object."""
    fname = '.'.join((fname, 'csv'))
    resp = make_response(csv_data, status_code)
    resp.mimetype = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename="%s"' % fname
    return resp

'''
def add_resource(*args, **kwargs):
    """Add resource."""
    API.add_resource(*args, **kwargs)
'''
