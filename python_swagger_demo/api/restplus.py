import logging
import traceback
from functools import wraps

from flask import request, abort, g, Response
from flask_restplus import Api
from python_swagger_demo import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


def my_decorator(func):
    func = api.doc(security='apikey')(func)

    def wrapper(*args, **kwargs):
        print("my decorator")
        print(request.headers)
        if 'X-API-KEY' not in request.headers:
            api.abort('401', 'API key required')
        return func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def auth_required(func):
    func = api.doc(security='apikey')(func)

    def check_auth(*args, **kwargs):
        if 'X-API-KEY' not in request.headers:
            api.abort('401', 'API key required')
        key = request.headers['X-API-KEY']

        return func(*args, **kwargs)

    return check_auth


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        user = ['add']
        if auth:  # no header set
            if auth.username:  # check active session
                g.user = user
            return f(*args, **kwargs)
        else:
            abort(401, 'not authorization')
            # user = UserModel.query.filter_by(username=auth.username).first()
            # if user is None or user.password != auth.password:
            #     abort(401)
            g.user = user
        return f(*args, **kwargs)

    return decorated


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(version='1.0', title='Python服务 API',
          description='Python服务 API 文档')


@api.errorhandler
def default_error_handler(e):
    message = '发生异常情况.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': '数据查询没有找到任何结果.'}, 404
