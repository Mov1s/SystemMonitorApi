from flask import request, current_app, jsonify
from functools import wraps
from subprocess import Popen, PIPE
import traceback
import sys

def support_jsonp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content,mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            exception = sys.exc_info()
            traceback.print_exception(*exception)
            error = ''.join(traceback.format_exception(*exception)[-2:]).strip().replace('\n',': ').replace('"', "'")
            error_response = jsonify({ "message" : "Something went wrong.", "error" : error })
            error_response.status_code = 500
            del exception
            return error_response
    return decorated_function


def run_from_shell(*args):
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    return out
