import bottle
from datetime import datetime
import enum
import functools

import config as cfg
import filters


def json_serialize(o):
    if isinstance(o, datetime):
        return o.strftime('%Y/%m/%d %H:%M')
    elif isinstance(o, enum.Enum):
        return o.value
    raise TypeError(repr(o) + ' is not JSON serializable')


def session(func):
    @functools.wraps(func)
    def inner(*a, **kw):
        session = bottle.request.environ.get('beaker.session')
        path = bottle.request.path.split('/')[1:]
        return add_dict(
            func(*a, **kw, session=session),
            {'session': session, 'path': path})
    return inner


def site_info(func):
    @functools.wraps(func)
    def inner(*a, **kw):
        session = bottle.request.environ.get('beaker.session')
        return add_dict(
            cfg.site_info,
            func(*a, **kw),
            {'session': session})
    return inner


def login(func):
    @functools.wraps(func)
    def inner(session, *a, **kw):
        if not session.get('login'):
            bottle.redirect('/login')
        return func(*a, **kw, session=session)
    return inner


def add_dict(*dicts):
    return {k: v
            for d in dicts if d is not None
            for k, v in d.items()}


view = functools.partial(bottle.jinja2_view,
                         template_settings={
                             'globals': cfg.site_info,
                             'filters': {
                                 'org': filters.org,
                                 'org_esc': filters.org_esc
                             }
                         })
