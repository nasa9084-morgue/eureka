import bottle
from datetime import datetime
import enum
import functools

from pyorg import org_to_html
import config as cfg
import models

def session(func):
    @functools.wraps(func)
    def inner(*a, **kw):
        session = bottle.request.environ.get('beaker.session')
        path = bottle.request.path.split('/')[1:]
        query = bottle.request.query.decode()
        return add_dict(
            func(*a, **kw, session=session),
            {'session': session, 'path': path, 'query': query})
    return inner


def site_info(func):
    @functools.wraps(func)
    def inner(*a, **kw):
        session = bottle.request.environ.get('beaker.session')
        return add_dict(
            models.Config.get_dict(),
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


def password(password):
    return password


def add_dict(*dicts):
    return {k: v
            for d in dicts if d is not None
            for k, v in d.items()}


def image_filepath(path):
    return '/' + cfg.img_save_path + '/' + path

org_to_html = functools.partial(org_to_html, default_heading=2, newline='\n')
view = functools.partial(bottle.jinja2_view,
                         template_settings={
                             'filters': {
                                 'org': org_to_html,
                                 'image_filepath': image_filepath
                             }
                         })
