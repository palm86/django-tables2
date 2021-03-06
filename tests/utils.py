import warnings
from contextlib import contextmanager

import lxml.etree
import lxml.html
import six
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import FakePayload


def parse(html):
    return lxml.etree.fromstring(html)


def attrs(xml):
    """
    Helper function that returns a dict of XML attributes, given an element.
    """
    return lxml.html.fromstring(xml).attrib


@contextmanager
def warns(warning_class):
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        yield ws
        assert any((issubclass(w.category, DeprecationWarning) for w in ws))


@contextmanager
def translation(language_code, deactivate=False):
    """
    Port of django.utils.translation.override from Django 1.4

    @param language_code: a language code or ``None``. If ``None``, translation
                          is disabled and raw translation strings are used
    @param    deactivate: If ``True``, when leaving the manager revert to the
                          default behaviour (i.e. ``settings.LANGUAGE_CODE``)
                          rather than the translation that was active prior to
                          entering.
    """
    from django.utils import translation
    original = translation.get_language()
    if language_code is not None:
        translation.activate(language_code)
    else:
        translation.deactivate_all()
    try:
        yield
    finally:
        if deactivate:
            translation.deactivate()
        else:
            translation.activate(original)


def build_request(uri='/'):
    """
    Return a fresh HTTP GET / request.

    This is essentially a heavily cutdown version of Django 1.3's
    `~django.test.client.RequestFactory`.
    """
    path, _, querystring = uri.partition('?')
    return WSGIRequest({
        'CONTENT_TYPE': 'text/html; charset=utf-8',
        'PATH_INFO': path,
        'QUERY_STRING': querystring,
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'SERVER_NAME': 'testserver',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': FakePayload(b''),
        'wsgi.errors': six.StringIO(),
        'wsgi.multiprocess': True,
        'wsgi.multithread': False,
        'wsgi.run_once': False,
    })
