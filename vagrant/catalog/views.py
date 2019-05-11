#!/usr/bin/env python2
# Flask API endpoint file

import json
import time
import requests
from dao import (verifyAuthToken, getUser, getUserByUsername, addUser,
                 getAllCategories, getCategoriesByName, addCategory,
                 getCategory, checkAuthorization, updateCategory,
                 deleteCategory, getAllItems, getItemsByName, addItem,
                 getItem, updateItem, deleteItem, getCatalog)
from flask import (Flask, jsonify, request, url_for, abort,
                   g, render_template, send_from_directory)
from flask_httpauth import HTTPBasicAuth
from exception_handler import JSONExceptionHandler
from werkzeug.exceptions import default_exceptions
from werkzeug.routing import BaseConverter
from functools import update_wrapper
from redis import Redis


# Initialize application objects
redis = Redis()
auth = HTTPBasicAuth()
app = Flask(__name__)
handler = JSONExceptionHandler(app)


class RegexConverter(BaseConverter):
    """RegEx class extending base converter
    adding regular expression support."""

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


# Add new RegEx converter class to URL Mapping for routes
app.url_map.converters['regex'] = RegexConverter


class RateLimit(object):
    """Implements rate limit design."""
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)
    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    """Gets rate limit instance from global."""
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    """Define return error upon exceeding
    rate limit."""
    return (jsonify({'data': 'You hit the rate limit', 'error': '429'}), 429)


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    """The actual function used as a decorator
    that uses the rate limit class."""
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator


@app.after_request
def inject_x_rate_headers(response):
    """Runs after response to add rate
    limit data to HTTP header."""
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


@auth.verify_password
def verify_password(username_or_token_or_guid, password_or_gtoken):
    """Used by flask_httpauth to verify password
    for routes with login_required decorator"""
    # Try to see if it's a token first
    user_id = verifyAuthToken(username_or_token_or_guid)
    if user_id:
        user = getUser(user_id)
        g.user = user
        return True
    # If not a token then assume username and password
    user = getUserByUsername(username_or_token_or_guid)
    if user and user.verify_password(password_or_gtoken):
        g.user = user
        return True
    # If not a user then assume it's a Google O-Auth token
    userinfo_url = "https://oauth2.googleapis.com/tokeninfo"
    params = {'id_token': password_or_gtoken}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # Now make sure that this token belongs to an already
    #  registered user
    if ('sub' in data):
        user = getUserByUsername('GU'+data['sub'])
        if (user):
            g.user = user
            return True
    # Finally if all fails refuse access
    return False


# Home page
@app.route('/')
@ratelimit(limit=60, per=60 * 1)
def start():
    """Display home page"""
    return render_template('app.html')


# Resources
@app.route(r'/<regex("[^\.]+(\.(html|css|js|ico))?"):path>')
@ratelimit(limit=500, per=60 * 1)
def send_stuff(path):
    """Generic route to fetch any resources
    required by HTML page, route is limited
    by regular expressions"""
    return send_from_directory('templates', path)


# Rest of application routes
# Token generation
@app.route('/api/v1/token')
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def get_auth_token():
    """Retrun authentication token to be used
    more safely instead of username & password."""
    token = g.user.generate_auth_token(24*3600)
    return jsonify({'user_id': g.user.id, 'token': token.decode('ascii')})


# Users
# Create
@app.route('/api/v1/users', methods=['POST'])
@ratelimit(limit=10, per=60 * 1)
def new_user():
    """API endpoint to create new users."""
    username = request.json.get('username')
    password = request.json.get('password')
    picture = request.json.get('picture')
    email = request.json.get('email')
    if username is None or password is None:
        print("missing arguments")
        abort(400)

    if getUserByUsername(username) is not None:
        print("existing user")
        return jsonify({'message': 'user already exists'}), 200

    user = addUser(username, picture, email, password)
    return jsonify(user=user.serialize), 201


@app.route('/api/v1/users/check/<string:username>')
@ratelimit(limit=10, per=60 * 1)
def check_username(username):
    """API endpoint to check if username already
    exists, used for duplicate check."""
    user = getUserByUsername(username)
    if not user:
        return jsonify({'found': False})
    else:
        return jsonify({'found': True})


@app.route('/api/v1/users/<int:id>')
@auth.login_required
@ratelimit(limit=10, per=60 * 1)
def get_user(id):
    """API endpoint to get user by user ID,
    only works if credentials matches
    those of the requested user."""
    if (g.user.id == id):
        return jsonify(g.user.serialize)
    else:
        abort(400)


# Categories
@app.route('/api/v1/categories', methods=['GET'])
@ratelimit(limit=10, per=60 * 1)
def all_categories_handler():
    """API endpoint to get all categories."""
    categories = getAllCategories()
    return jsonify(categories=[i.serialize for i in categories])


@app.route('/api/v1/categories/<string:query>', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def query_categories_handler(query):
    """API endpoint to search for category by name."""
    categories = getCategoriesByName(query)
    return jsonify(categories=[i.serialize for i in categories])


@app.route('/api/v1/categories', methods=['POST'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def add_categories_handler():
    """API endpoint to create new category."""
    rq = request.get_json()
    name = rq['name']
    picture = rq['picture']
    description = rq['description']
    category = addCategory(name, picture, description, g.user.id)
    return jsonify(category=category.serialize)


@app.route('/api/v1/categories/<int:id>', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def category_retrieve(id):
    """API endpoint to get category by Id."""
    category = getCategory(id)
    if category is None:
        return jsonify({}), 204
    else:
        return jsonify(category=category.serialize)


@app.route('/api/v1/categories/<int:id>', methods=['PUT', 'DELETE'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def category_handler(id):
    """API endpoint to update or delete a category."""
    if request.method == 'PUT':
        # authorization
        if not checkAuthorization('Category', id, g.user.id):
            return (jsonify({'data': 'Unauthorized', 'error': '401'}), 401)
        # Call the method to update a category
        rq = request.get_json()
        name = rq['name']
        picture = rq['picture']
        description = rq['description']
        category = updateCategory(id, name, picture, description)
        return jsonify(category=category.serialize)
    elif request.method == 'DELETE':
        # authorization
        if not checkAuthorization('Category', id, g.user.id):
            return (jsonify({'data': 'Unauthorized', 'error': '401'}), 401)
        # Call the method to remove a category
        category = deleteCategory(id)
        return jsonify(category=category.serialize)


# Items
@app.route('/api/v1/items', methods=['GET'])
@ratelimit(limit=10, per=60 * 1)
def all_items_handler():
    """API endpoint to get all items."""
    items = getAllItems()
    return jsonify(items=[i.serialize for i in items])


@app.route('/api/v1/items/<string:query>', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def query_items_handler(query):
    """API endpoint to search for item by name."""
    items = getItemsByName(query)
    return jsonify(items=[i.serialize for i in items])


@app.route('/api/v1/items', methods=['POST'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def add_items_handler():
    """API endpoint to create new item."""
    rq = request.get_json()
    name = rq['name']
    picture = rq['picture']
    description = rq['description']
    category_id = rq['category_id']
    item = addItem(name, picture, description, category_id, g.user.id)
    return jsonify(item=item.serialize)


@app.route('/api/v1/items/<int:id>', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def item_retrieve(id):
    """API endpoint to get item by Id."""
    item = getItem(id)
    if item is None:
        return jsonify({}), 204
    else:
        return jsonify(item=item.serialize)


@app.route('/api/v1/items/<int:id>', methods=['PUT', 'DELETE'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def item_handler(id):
    """API endpoint to update or delete an item."""
    if request.method == 'PUT':
        # authorization
        if not checkAuthorization('Item', id, g.user.id):
            return (jsonify({'data': 'Unauthorized', 'error': '401'}), 401)
        # Call the method to update a item
        rq = request.get_json()
        name = rq['name']
        picture = rq['picture']
        description = rq['description']
        item = updateItem(id, name, picture, description)
        return jsonify(item=item.serialize)
    elif request.method == 'DELETE':
        # authorization
        if not checkAuthorization('Item', id, g.user.id):
            return (jsonify({'data': 'Unauthorized', 'error': '401'}), 401)
        # Call the method to remove a item
        item = deleteItem(id)
        return jsonify(item=item.serialize)


# Catalog
@app.route('/api/v1/catalog')
@ratelimit(limit=60, per=60 * 1)
def get_catalog():
    """API endpoint to get full catalog
    (categories + items) in an easy to
    traverse tree like JSON object."""
    return jsonify(getCatalog())


# Finally application start if file is run as main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
