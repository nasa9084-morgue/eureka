from datetime import datetime
import enum
import json
import re
import sqlalchemy
from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.sql.expression import text

import config as cfg
import tools

db_url = 'mysql+pymysql://{user}:{passwd}@{host}/{db}?charset={charset}'
engine = sqlalchemy.create_engine(db_url.format(**cfg.mysql))
session = sessionmaker(bind=engine)()

BaseModel = declarative_base()

# Statics
CASCADE = 'CASCADE'
CURRENT_TIMESTAMP = text('CURRENT_TIMESTAMP')


class EurekaModel(object):
    @classmethod
    def query(cls, *a, **kw):
        return session.query(cls, *a, **kw)

    def save(self):
        session.commit()


class User(BaseModel, EurekaModel):
    __tablename__ = cfg.table_prefix + '_users'

    # table definition
    login = Column(String(64), primary_key=True)
    password = Column(String(512), nullable=False)

    posts = relation('Article', order_by='Article.published', backref='users')


tag_relations = sqlalchemy.Table(
    'tag_relations', BaseModel.metadata,
    Column('article', String(64),
           ForeignKey(cfg.table_prefix + '_articles.slug',
                      ondelete=CASCADE)),
    Column('tag', String(64),
           ForeignKey(cfg.table_prefix + '_tags.slug',
                      ondelete=CASCADE)))


class Tag(BaseModel, EurekaModel):
    __tablename__ = cfg.table_prefix + '_tags'

    # table definition
    slug = Column(String(64), primary_key=True)

    def __str__(self):
        return self.slug


class Article(BaseModel, EurekaModel):
    __tablename__ = cfg.table_prefix + '_articles'

    # table definition
    slug = Column(String(64), primary_key=True)
    author = Column(String(64), ForeignKey(User.login,
                                           onupdate=CASCADE,
                                           ondelete=CASCADE),
                    nullable=False)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(
        Enum(enum.Enum('ArticleStatus',
                       {s:s for s in cfg.statuses})),
        nullable=False)
    created = Column(DateTime, nullable=False,
                     server_default=CURRENT_TIMESTAMP)
    published = Column(DateTime)
    modified = Column(DateTime)

    tags = relation('Tag', order_by='Tag.slug',
                    backref='articles', secondary=tag_relations)

    comments = relation('Comment', order_by='Comment.created',
                        backref='articles')

    def abstract(self):
        if '<more>' in self.content:
            return re.split('<more>', self.content)[0]
        else:
            return self.content

    def has_more(self):
        return '<more>' in self.content

    def json(self):
        return json.dumps({
            'slug': self.slug,
            'author': self.author,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'created': self.created,
            'published': self.published,
            'modified': self.modified,
            'comments': self.comments
        }, default=tools.json_serialize)

    def publish(self):
        if self.status.value == 'draft':
            self.published = datetime.now()
            self.status = 'published'
            session.commit()



class Comment(BaseModel, EurekaModel):
    __tablename__ = cfg.table_prefix + '_comments'

    # table definition
    id_ = Column(Integer, primary_key=True,
                 autoincrement=True)
    article_slug = Column(String(64), ForeignKey(Article.slug,
                                                 onupdate=CASCADE,
                                                 ondelete=CASCADE))
    author = Column(String(64), nullable=False)
    author_email = Column(String(128))
    author_url = Column(String(256))
    content = Column(Text, nullable=False)
    created = Column(DateTime, nullable=False,
                     server_default=CURRENT_TIMESTAMP)


class Config(BaseModel, EurekaModel):
    __tablename__ = cfg.table_prefix + '_config'

    # table definition
    configkey = Column(String(64), primary_key=True)
    configvalue = Column(String(512), nullable=False)
