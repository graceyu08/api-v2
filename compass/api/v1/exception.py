from compass.api import utils
from compass.api.exception import *
from compass.api.v1 import v1_app as app

@app.errorhandler(ItemNotFound)
def handle_not_exist(error, failed_objs=None):                                 
    """Handler of ItemNotFound Exception."""                                   
                                                                               
    message = {'type': 'itemNotFound',                                         
               'message': error.message}                                       
                                                                               
    if failed_objs and isinstance(failed_objs, dict):                          
        message.update(failed_objs)                                            
                                                                               
    return utils.make_json_response(404, message)                              
                                                                               
                                                                               
@app.errorhandler(Unauthorized)                                                
def handle_invalid_user(error, failed_objs=None):                              
    """Handler of Unauthorized Exception."""                                   
                                                                               
    message = {'type': 'unathorized',                                          
               'message': error.message}                                       
                                                                               
    if failed_objs and isinstance(failed_objs, dict):                          
        message.update(failed_objs)                                            
                                                                               
    return utils.make_json_response(401, message)                              
                                                                               
                                                                               
@app.errorhandler(Forbidden)                                                   
def handle_no_permission(error, failed_objs=None):                             
    """Handler of Forbidden Exception."""                                      
                                                                               
    message = {'type': 'Forbidden',                                            
               'message': error.message}                                       
                                                                               
    if failed_objs and isinstance(failed_objs, dict):                          
        message.update(failed_objs)                                            
                                                                               
    return utils.make_json_response(403, message)
