from bottle import HTTPError

class EurekaException(HTTPError):
    default_status = 500


class DatabaseError(EurekaException):
    default_status = 500


class ArticleNotFoundError(EurekaException):
    default_status = 404
