Django to json
==============

Django view decorator to easily handle json responses

I was annoyed by annoying.decorators.ajax_request, so I wrote my own
render_to_response decorator, which I find more flexible and useful.

installation
------------
Simply install with:

`pip install git+https://github.com/davidek/django-tojson.git@master`

render_to_json
--------------

```python
from tojson import render_to_json

@render_to_json()
def my_view(request):
    if ... :
        # Simple usage
        return {'success': True}
    else if ... :
        # Passing an HttpResponse subclass that will be used instead of HttpResponse
        return {'status': 'authentication failed'}, dict(cls=HttpResponseForbidden)
    else if ... :
        # Directly return some content
        return 'My custom string, will simply be written into HttpResponse', dict(jsonify=False)
    else:
        # Returning an HttpResponse or a sublcass, nothing will be done
        return HttpResponseSubClass('This will not be touched by the decorator.')

# Arguments can be passed directly to the decorator

# Any non-recognized arguments will be passed to
# HttpResponse (or provided subclass) constructor

@render_to_json(status=401):
def my_view(request):
    return {'example': 21}


# Using django Http404 exception
@render_to_json(not_found_error={'success': False, 'message': 'Are you kidding me?'}):
    my_obj = get_object_or_404(MyModel, ...)

    if not some_condition_satisfied:
        raise Http404

```

Recognized keyword arguments are:

- `cls`  Class to be used instead of HttpResponse
- `jsonify` if False (default: True) obj will be just written to reponse
- `ensure_ascii` if True (default: False) obj will be encoded before
  writing it to response
- `not_found_error` object thet will be converted to json and written in case
  Http404 is raised (Note this can only be specified as the decorator parameter)


### Configuration

not_found_error can also be specified at project-level, inside your settings file

```python
# settings.py

TOJSON_DEFAULT_ERRORS = {
    'not_found':
        {'success': False,
         'message': 'Page not found'},
}

```

login_required_json
-------------------

```python
from tojson import login_required_json

@login_required_json(accept_basic_auth=True)
def my_view(request):
    # request.user abailable

```

Parameters:

- `accept_default_auth` (default: True) also accept standard django cookie-based
  authentication
- `accept_basic_auth` (default: False) also accept Http basic authentication
  (see http://en.wikipedia.org/wiki/Basic_access_authentication)

  Note that in addition to `Authorization` header, `X-Authorization` is allowed
  as well. This is to avoid problems in case your webserver "catches" the
  `Authorization` header

AUTHORS
-------
* Davide Kirchner
* Roberto Bampi

