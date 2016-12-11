import bottle
from beaker.middleware import SessionMiddleware
from datetime import datetime
import functools
import os
import re

import config as cfg
import models
import tools
from tools import view

app = application = SessionMiddleware(bottle.app(), cfg.beaker_opts)
route = bottle.route
get = bottle.get
post = bottle.post
redirect = bottle.redirect
error = bottle.error


@route('/')
@view('index.tmpl')
@tools.site_info
@tools.session
def index(session):
    articles = models.Article.query().order_by(models.Article.published).filter(models.Article.status=='published')
    users = models.User.query().all()
    return {'articles': articles,
            'users': users}


@route('/tag/<slug>')
@view('index.tmpl')
@tools.site_info
@tools.session
def tag_articles(slug, session):
    articles = models.Tag.query().get(slug).articles
    articles = [article for article in articles if article.status.value=='published']
    return {'articles': articles}


@route('/article/<slug>')
@view('article.tmpl')
@tools.site_info
@tools.session
def article(slug, session):
    article = models.Article.query().get(slug)
    if not article:
        bottle.abort(404)
    if article.status.value == 'draft':
        bottle.abort(403)
    return {'article': article}


@post('/article/<slug>/comment.new')
@tools.session
def comment_new_post(slug, session):
    request = bottle.request.forms.decode()
    article = models.Article.query().get(slug)
    if article.status.value == 'draft':
        bottle.abort(403)
    new_comment = {
        'article_slug': slug,
        'author': request['name'],
        'content': request['content']
    }
    if request.get('email'):
        new_comment['author_email'] = request['email']
    if request.get('url'):
        new_comment['author_url'] = request['url']
    models.session.add(models.Comment(**new_comment))
    models.session.commit()
    redirect('/article/{}'.format(slug))



@route('/login')
@view('login.tmpl')
@tools.site_info
@tools.session
def login(session):
    if session.get('login'):
        redirect('admin')
    return


@post('/login')
@tools.session
def login_middle(session):
    login = bottle.request.forms.decode().get('login_name')
    user = models.session.query(models.User).get(login)
    if user is None:
        redirect('/login?error_code=20')
    password = bottle.request.forms.get('password')
    if user.password == tools.password(password):
        session['login'] = user.login
        session.save()
        redirect('/admin')
    redirect('/login?error_code=20')


@route('/logout')
@tools.site_info
@tools.session
def logout(session):
    session.delete()
    redirect('/login')


@route('/{}'.format(cfg.admin_path))
@view('dashboard.tmpl')
@tools.site_info
@tools.session
@tools.login
def dashboard(session):
    return {}


@route('/{}/article'.format(cfg.admin_path))
@view('admin_article.tmpl')
@tools.site_info
@tools.session
@tools.login
def article(session):
    articles = models.Article.query().order_by(models.Article.published)
    return {'articles': articles}


@route('/{}/article.new'.format(cfg.admin_path))
@view('admin_article_new.tmpl')
@tools.site_info
@tools.session
@tools.login
def article_new(session):
    return {'statuses': cfg.statuses}


@post('/{}/article.new'.format(cfg.admin_path))
@tools.session
@tools.login
def article_new_post(session):
    request = bottle.request.forms.decode()
    tag_strs = [tag
                for tag in re.split(',\s?', request.get('tags'))
                if tag]
    tags = []
    for tag in tag_strs:
        if tag in [str(t) for t in models.Tag.query().all()]:
            tags.append(models.Tag.query().get(tag))
        else:
            tags.append(models.Tag(slug=tag))
    new_article = {
        'slug': request.get('slug'),
        'author': session['login'],
        'title': request.get('title'),
        'content': request.get('content'),
        'tags': tags,
        'status': request.get('status')
    }
    if request.get('status') == 'published':
        new_article.update({'published': datetime.now()})
    models.session.add(models.Article(**new_article))
    models.session.commit()
    redirect('/admin/article')


@route('/{}/article/<slug>'.format(cfg.admin_path))
@view('admin_article_detail.tmpl')
@tools.site_info
@tools.session
@tools.login
def article_detail(session, slug):
    article = models.Article.query().get(slug)
    return {'article': article,
            'statuses': cfg.statuses}


@post('/{}/article/<slug>'.format(cfg.admin_path))
@tools.session
@tools.login
def article_detail_update(session, slug):
    request = bottle.request.forms.decode()
    article = models.Article.query().get(slug)
    if article.title != request.get('title'):
        article.title = request.get('title')
    tag_strs = [tag
                for tag in re.split(',\s?', request.get('tags'))
                if tag]
    tags = []
    for tag in tag_strs:
        if tag in [str(t) for t in models.Tag.query().all()]:
            tags.append(models.Tag.query().get(tag))
        else:
            tags.append(models.Tag(slug=tag))
    if article.tags != tags:
        article.tags = tags
    if article.content != request.get('content'):
        article.content = request.get('content')
    if article.status != request.get('status'):
        article.status = request.get('status')
    if request.get('status') == 'published' and article.published is None:
        article.published = datetime.now()
    elif request.get('status') == 'draft':
        article.published = None
    article.save()
    redirect('/admin/article')


@route('/{}/image'.format(cfg.admin_path))
@view('admin_images.tmpl')
@tools.site_info
@tools.session
@tools.login
def image(session):
    images = os.listdir(cfg.img_save_path)
    return {'images': images}


@post('/{}/image'.format(cfg.admin_path))
@tools.session
@tools.login
def image_post(session):
    filename = bottle.request.forms.decode().get('filename')
    posted = bottle.request.files.get('upload_img')
    if not posted:
        redirect('/admin/image')
    _, extension = os.path.splitext(posted.filename)
    if not extension.lower() in cfg.allow_img_ext:
        redirect('/admin/image')
    if not filename.lower().endswith(extension.lower()):
        redirect('/admin/image')
    posted.filename = filename
    posted.save(cfg.img_save_path)
    redirect('/admin/image')


@route('/{}/tag'.format(cfg.admin_path))
@view('admin_tags.tmpl')
@tools.site_info
@tools.session
@tools.login
def tag(session):
    tags = models.Tag.query().all()
    return {'tags': tags}


@route('/{}/tag/<slug>'.format(cfg.admin_path))
@view('admin_tag_articles.tmpl')
@tools.site_info
@tools.session
@tools.login
def tag_detail(session, slug):
    articles = models.Tag.query().get(slug).articles
    return {'tag': slug,
            'articles': articles}


@route('/{}/tag/<slug>/delete'.format(cfg.admin_path))
@tools.site_info
@tools.session
@tools.login
def tag_delete(session, slug):
    tag = models.Tag.query().get(slug)
    models.session.delete(tag)
    redirect('/admin/tag')


@route('/{}/user'.format(cfg.admin_path))
@view('admin_user.tmpl')
@tools.site_info
@tools.session
@tools.login
def admin_user(session):
    return {}


@post('/{}/user'.format(cfg.admin_path))
@tools.session
@tools.login
def admin_user_post(session):
    request = bottle.request.forms.decode()
    user = models.User.query().get(session['login'])
    login = request.get('login')
    current_password = request.get('current_password')
    new_password = request.get('new_password')
    if not login or not current_password:
        redirect('/admin/user?error_code=40')
    if user.password != tools.password(current_password):
        redirect('/admin/user?error_code=41')
    if user.login != login:
        user.login = login
    if new_password:
        user.password = tools.password(new_password)
    user.save()
    session['login'] = user.login
    session.save()
    redirect('/admin/user')


@route('/{}/config'.format(cfg.admin_path))
@view('admin_config.tmpl')
@tools.site_info
@tools.session
@tools.login
def config(session):
    return {}


@post('/{}/config'.format(cfg.admin_path))
@tools.session
@tools.login
def config_post(session):
    request = bottle.request.forms.decode()
    configs = models.Config.query().all()
    for config in configs:
        if config.key in request and config.value != request[config.key]:
            config.value = request[config.key]
            config.save()
    redirect('/{}/config'.format(cfg.admin_path))


@error(404)
@view('404.tmpl')
@tools.site_info
def error404(err):
    session = bottle.request.environ.get('beaker.session')
    return {'message': 'Not Found'}


@bottle.route('/' + cfg.img_save_path + '/<fname>')
def static(fname):
    return bottle.static_file(fname, root=cfg.img_save_path)


@bottle.route('/static/<fpath:path>')
def static(fpath):
    return bottle.static_file(fpath, root='static')


@bottle.error(500)
def rollback(e):
    models.session.rollback()

if __name__ == '__main__':
    bottle.run(app=app, debug=True)
