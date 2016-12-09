import app.models
import os

import app.config as cfg

# create image dir
os.mkdir(cfg.img_save_path)

# initialize database
models.BaseModel.metadata.drop_all(models.engine)
models.BaseModel.metadata.create_all(models.engine)

models.session.add(
    models.User(**{'login': 'admin', 'password': 'PASSWORD'})
)
models.session.commit()

# create hello article
user = models.User.query().get('admin')
new_article = {
    'slug': 'hello',
    'author': user.login,
    'title': 'Hello',
    'content': 'Hello, World',
    'status': 'published'
}
models.session.add(models.Article(**new_article))
models.session.commit()
