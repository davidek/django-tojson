# Django view decorator to easily handle json responses
#
# I was annoyed by annoying.decorators.ajax_request, so I wrote my own
# render_to_response decorator, which I find more flexible and useful.
# See examples in the docstrings below for usage.
#
# Written by: Davide Kirchner
#

from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings

from functools import wraps
try:
    import json
except ImportError:
    import simplejson as json


def charset_already_set(response):
    """
    This function check if charset is already setted in Content-Type
    """
    charset = response.get('Content-Type', None)
    if charset:
        if 'charset' in unicode(charset).lower():
            return True
        else : 
            return False
    else:
        return False


def to_json_response(obj, **kwargs):
    """
    Unless obj is itself an HttpResponse or cls is None,
    kwargs will be passed to the class constructor.
    Special kwargs are:
    'cls'      Class to be used instead of HttpResponse.
               If None, obj will be simply returned
    'jsonify'  Boolean: if false, obj will be just written to reponse
    'ensure_ascii' Boolean: if true, json will be encoded into ascii.
                   default False
    """
    if isinstance(obj, HttpResponse):
        return obj

    cls = kwargs.pop('cls', HttpResponse)
    jsonify = kwargs.pop('jsonify', True)
    ascii = kwargs.pop('ensure_ascii', False)

    try:
        params = {'mimetype': 'application/json'}
        params.update(kwargs)
        r = cls(**params)
    except TypeError:
        return obj

    if obj is not None:
        indent = 4 if getattr(settings, 'DEBUG', False) else None
        if jsonify:
            json.dump(obj, r, indent=indent, ensure_ascii=ascii)
            if (not ascii) and (not charset_already_set(r)):
                r['Content-Type'] += '; charset=utf-8'
        else:
            r.write(obj)
    else:
        r.write("")

    return r


def render_to_json(**default_args):
    """
    Decorator that wraps to_json_response.
    
    @render_to_json()
    def my_view(request):
        if ... :
            return {'status': 'ok'}
        else if ... :
            return {'status': 'authentication failed'}, dict(cls=HttpResponseForbidden)
        else if ... :
            return 'My custom string, will simply be written into HttpResponse', dict(jsonify=False)
        else:
            return HttpResponseSubClass('This will not be touched by the decorator.')

    @render_to_json(status=401):
    def my_view(request):
        return {'whatever': 21}

    """
    def wrap(the_func):
        @wraps(the_func)
        def _decorated(*args, **kwargs):
            ret = the_func(*args, **kwargs)
            obj = ret
            dec_args = default_args.copy()

            if isinstance(ret, tuple):
                if len(ret) == 2:
                    obj, newargs = ret
                    if isinstance(newargs, dict):
                        dec_args.update(newargs)

            return to_json_response(obj, **dec_args)

        return _decorated
    return wrap

from django.contrib.auth import authenticate
import base64

def login_required_json(
    error={'success': False,
           'message': 'Logging in is required'},
    accept_default_auth=True, accept_basic_auth=False):
    '''
    If the user is not logged in, rejects the request with the given error
    and HTTP 403 Forbidden status code.
    If accept_basic is True and user is not already authenticated, HTTP
    basic auth will be tried and, on failure, the error is returned.
    For http basic auth one may want to also use @csrf_exempt
    The error must be a json-serializable object
    '''
    def wrap(view):
        @wraps(view)
        def _decorated(request, *args, **kwargs):
            authorized = False
            if accept_default_auth:
                if request.user.is_authenticated():
                    authorized = True

            if ((not authorized) and accept_basic_auth):
                auth_header = request.META.get('HTTP_AUTHORIZATION', None)
                if auth_header is None:
                    auth_header = request.META.get('HTTP_X_AUTHORIZATION', None)
                try:
                    auth_type, token = auth_header.split()
                    if auth_type.lower() == "basic":
                        uname, passwd = base64.b64decode(token).split(':')
                        user = authenticate(username=uname, password=passwd)
                        if user is not None:
                            if user.is_active:
                                # login(request, user) # no need no save session
                                request.user = user
                                authorized = True
                except (ValueError, AttributeError):
                    pass

            if authorized:
                return view(request, *args, **kwargs)
            else:
                return to_json_response(error, cls=HttpResponseForbidden)

        return _decorated
    return wrap
