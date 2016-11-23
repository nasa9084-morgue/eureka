from models import Article, BaseModel, Comment, User
from models import engine, session

BaseModel.metadata.drop_all(engine)
BaseModel.metadata.create_all(engine)

new_user = User(login='admin', password='PASRORR')
session.add(new_user)
session.commit()

user = session.query(User).get('admin')
new_article = {
    'slug': 'hello',
    'author': user.login,
    'title': 'Hello',
    'content': 'Hello, World',
    'status': 'published'
}
session.add(Article(**new_article))
session.commit()

article = session.query(Article).get('hello')
print(article.status.value == 'published')
print(article.json())

print(session.query(Article).all())
