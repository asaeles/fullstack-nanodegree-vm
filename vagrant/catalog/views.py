#!/usr/bin/env python2

import json
import time
import requests
from flask import Flask, jsonify, request, url_for, abort, g, render_template, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.routing import BaseConverter
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from functools import update_wrapper
from redis import Redis


# Prepare SQLAlchemy DB session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# Initialize application objects
redis = Redis()
auth = HTTPBasicAuth()
session = DBSession()
app = Flask(__name__)

# Add RegEx converter to URL Mapping for routes
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

# Rate limit class, functions and implementation
class RateLimit(object):
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
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return (jsonify({'data': 'You hit the rate limit', 'error': '429'}), 429)

def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
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
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


# Basic HTTP authentication implementation
@auth.verify_password
def verify_password(username_or_token_or_guid, password_or_gtoken):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token_or_guid)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
        g.user = user
        return True
    # If not a token then assume username and password
    user = session.query(User).filter_by(
        username=username_or_token_or_guid).first()
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
        user = session.query(User).filter_by(username='GU'+data['sub']).first()
        if (user):
            g.user = user
            return True
    # Finally if all fails refuse access
    return False


# Home page
@app.route('/')
@ratelimit(limit=60, per=60 * 1)
def start():
    return render_template('app.html')

# Resources
@app.route('/<regex("[^\.]+(\.(html|css|js|ico))?"):path>')
@ratelimit(limit=500, per=60 * 1)
def send_stuff(path):
    return send_from_directory('templates', path)


# Rest of application routes
# Token generation
@app.route('/api/v1/token')
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def get_auth_token():
    token = g.user.generate_auth_token(24*3600)
    return jsonify({'user_id': g.user.id, 'token': token.decode('ascii')})


# Users
# Create
@app.route('/api/v1/users', methods=['POST'])
@ratelimit(limit=10, per=60 * 1)
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    picture = request.json.get('picture')
    email = request.json.get('email')
    if username is None or password is None:
        print("missing arguments")
        abort(400)

    if session.query(User).filter_by(username=username).first() is not None:
        print("existing user")
        user = session.query(User).filter_by(username=username).first()
        # , {'Location': url_for('get_user', id = user.id, _external = True)}
        return jsonify({'message': 'user already exists'}), 200

    user = User(
        username=username,
        picture=picture,
        email=email
    )
    user.hash_password(password)
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    # , {'Location': url_for('get_user', id = user.id, _external = True)}
    return jsonify({'id': user.id, 'username': user.username}), 201

# Duplicate check (existing username)
@app.route('/api/v1/users/check/<string:username>')
@ratelimit(limit=10, per=60 * 1)
def check_username(username):
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({'found': False})
    else:
        return jsonify({'found': True})

# Get user data only if credentials matches
#  those of the requested user id
@app.route('/api/v1/users/<int:id>')
@auth.login_required
@ratelimit(limit=10, per=60 * 1)
def get_user(id):
    if (g.user.id == id):
        return jsonify(g.user.serialize)
    else:
        abort(400)


# Categories
# Fetch all
@app.route('/api/v1/categories', methods=['GET'])
@ratelimit(limit=10, per=60 * 1)
def all_categories_handler():
    # Call the method to Get all of the categories
    return getAllCategories()

# Search for categories
@app.route('/api/v1/categories/<string:query>', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def query_categories_handler(query):
    return getCategoriesByName(query)

# Create
@app.route('/api/v1/categories', methods=['POST'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def add_categories_handler():
    # Call the method to make a new category
    rq = request.get_json()
    name = rq['name']
    picture = rq['picture']
    description = rq['description']
    category = Category(name=name, picture=picture,
                        description=description)
    session.add(category)
    try:
         session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(category=category.serialize)

# RUD from CRUD
@app.route('/api/v1/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def category_handler(id):
    # YOUR CODE HERE
    if request.method == 'GET':
        # Call the method to get a specific category based on their id
        return getCategory(id)
    if request.method == 'PUT':
        # Call the method to update a category
        rq = request.get_json()
        name = rq['name']
        picture = rq['picture']
        description = rq['description']
        return updateCategory(id, name, picture, description)
    elif request.method == 'DELETE':
        # Call the method to remove a category
        return deleteCategory(id)


# Items
# Fetch all
@app.route('/api/v1/items', methods=['GET'])
@ratelimit(limit=60, per=60 * 1)
def all_items_handler():
    # Call the method to get all of the items
    return getAllItems()

# Create
@app.route('/api/v1/items', methods=['POST'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def add_items_handler():
    # Call the method to make a new category
    rq = request.get_json()
    name = rq['name']
    picture = rq['picture']
    description = rq['description']
    category_id = rq['category_id']
    item = Item(name=name, picture=picture,
                description=description, category_id=category_id)
    session.add(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(category=item.serialize)

# RUD from CRUD
@app.route('/api/v1/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
@ratelimit(limit=60, per=60 * 1)
def item_handler(id):
    # YOUR CODE HERE
    if request.method == 'GET':
        # Call the method to get a specific item based on their id
        return getItem(id)
    if request.method == 'PUT':
        # Call the method to update a item
        rq = request.get_json()
        name = rq['name']
        picture = rq['picture']
        description = rq['description']
        return updateItem(id, name, picture, description)
    elif request.method == 'DELETE':
        # Call the method to remove a item
        return deleteItem(id)


# Catalog (Categories + Items)
# Special route to return the full
#  catalog in an easy to traverse
#  tree like JSON object
@app.route('/api/v1/catalog')
@ratelimit(limit=60, per=60 * 1)
def get_catalog():
    catalog = []
    categories = session.query(Category).order_by(Category.name).all()
    for c in categories:
        cat = c.serialize
        cat['items'] = []
        items = session.query(Item).filter_by(
            category_id=c.id).order_by(Item.name)
        for i in items:
            cat['items'].append(i.serialize)
        catalog.append(cat)
    return jsonify(catalog)


# Rest of functions
# Categories
def getAllCategories():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


def getCategoriesByName(parameter_list):
    pass


def getCategory(id):
    category = session.query(Category).filter_by(id=id).one()
    return jsonify(category=category.serialize)


def updateCategory(id, name, picture, description):
    category = session.query(Category).filter_by(id=id).one()
    category.name = name
    category.picture = picture
    category.description = description
    session.add(category)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(category=category.serialize)


def deleteCategory(id):
    category = session.query(Category).filter_by(id=id).one()
    session.delete(category)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(category=category.serialize)


# Items
def getAllItems():
    items = session.query(Item).join(Category).all()
    for item in items:
        cat = item.category
        print(item.id, item.name, cat.name)
    return jsonify(items=[i.serialize.update(i.category.serialize) for i in items])


def getItemsByName(parameter_list):
    pass


def getItem(id):
    item = session.query(Item).filter_by(id=id).one()
    return jsonify(item=item.serialize)


def updateItem(id, name, picture, description):
    item = session.query(Item).filter_by(id=id).one()
    item.name = name
    item.picture = picture
    item.description = description
    session.add(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(item=item.serialize)


def deleteItem(id):
    item = session.query(Item).filter_by(id=id).one()
    session.delete(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return jsonify(item=item.serialize)


# Finally application start if file is run as main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
