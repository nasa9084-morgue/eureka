import app.models
import os

import app.config as cfg
import app.tools as tools

# create image dir
os.mkdir(cfg.img_save_path)

# initialize database
models.BaseModel.metadata.drop_all(models.engine)
models.BaseModel.metadata.create_all(models.engine)

for k, v in cfg.site_info.items():
    models.session.add(
        models.Config(**{'key': k, 'value': v})
    )

models.session.add(
    models.User(**{'login': 'admin', 'password': tools.password('PASSWORD')})
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
