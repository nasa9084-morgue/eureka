-- replace {{prefix}} to table prefix before execute
CREATE TABLE {{prefix}}_users (
       login VARCHAR(64) PRIMARY KEY,
       passwd VARCHAR(512) NOT NULL
) DEFAULT CHARSET=utf8;

CREATE TABLE {{prefix}}_articles (
       slug VARCHAR(64) PRIMARY KEY,
       title VARCHAR(128) NOT NULL,
       content LONGTEXT NOT NULL,
       status ENUM('draft', 'published') DEFAULT 'draft',
       created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       published DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8;

CREATE TABLE {{prefix}}_article_modified (
       slug VARCHAR(64) PRIMARY KEY,
       FOREIGN KEY (slug) REFERENCES {{prefix}}_articles (slug)

) DEFAULT CHARSET=utf8;
