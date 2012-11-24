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

try:
    import json
except ImportError:
    import simplejson as json

def to_json_response(obj, **kwargs):
    """
    Unless obj is itself an HttpResponse or cls is None,
    kwargs will be passed to the class constructor.
    Special kwargs are:
    'cls'      Class to be used instead of HttpResponse.
               If None, obj will be simply returned
    'jsonify'  Boolean: if false, obj will be just written to reponse
    """
    if isinstance(obj, HttpResponse):
        return obj

    cls = kwargs.pop('cls', HttpResponse)
    jsonify = kwargs.pop('jsonify', True)
    try:
        params = {'mimetype': 'application/json'}
        params.update(kwargs)
        r = cls(**params)
    except TypeError:
        return obj

    if obj is not None:
        indent = 4 if getattr(settings, 'DEBUG', False) else None
        if jsonify:
            r.write(json.dumps(obj, indent=indent))
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
        def _decorated(*args, **kwargs):
            ret = the_func(*args, **kwargs)
            obj = ret
            args=default_args

            if isinstance(ret, tuple):
                if len(ret) == 2:
                    obj, newargs = ret
                    if isinstance(newargs, dict):
                        args.update(newargs)

            return to_json_response(obj, **args)

        _decorated.__name__ = the_func.__name__
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
        def _decorated(request, *args, **kwargs):
            authorized = False
            if accept_default_auth:
                if request.user.is_authenticated():
                    authorized = True

            if ((not authorized) and accept_basic_auth):
                try:
                    auth_type, token = request.META['HTTP_AUTHORIZATION'].split()
                    if auth_type.lower() == "basic":
                        uname, passwd = base64.b64decode(token).split(':')
                        user = authenticate(username=uname, password=passwd)
                        if user is not None:
                            if user.is_active:
                                # login(request, user) # non needed, I think
                                request.user = user
                                authorized = True
                except (ValueError, KeyError):
                    pass

            if authorized:
                return view(request, *args, **kwargs)
            else:
                return to_json_response(error, cls=HttpResponseForbidden)

        _decorated.__name__ = view.__name__
        return _decorated
    return wrap
