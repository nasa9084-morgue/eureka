import pymysql.cursors

# site info
site_info = {
    'site_title': 'Eureka',
    'site_description': 'Eureka Blog CMS'
}

# article statuses
statuses = [
    'draft',
    'published'
]

# beaker session options
beaker_opts = {
    'session.type': 'redis',
    'session.url': '127.0.0.1:6379'
}

# table name prefix
table_prefix = 'eureka'

# MySQL Database options
mysql = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'nasa9084',
    'db': 'eureka_db',
    'charset': 'utf8'
}

# Image save path
img_save_path = 'img'

# Image Upload Allow
allow_img_ext = ['.png', '.jpg', '.gif']
