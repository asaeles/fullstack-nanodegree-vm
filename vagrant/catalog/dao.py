#!/usr/bin/env python2
# DB helper file

from flask import jsonify
from models import Base, User, Category, Item
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Prepare SQLAlchemy DB session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Authentication


def verifyAuthToken(username_or_token_or_guid):
    """Verify auth token and return user ID if successful."""
    return User.verify_auth_token(username_or_token_or_guid)

# Authorization


def checkAuthorization(table_name, id, user_id):
    """Return true if the supplied user is the one who created
    the supplied object otherwise return false."""
    if table_name == 'Category':
        table = Category
    elif table_name == 'Item':
        table = Item
    else:
        print('Unknown table: ' + table_name)
        return False
    obj = session.query(table).filter_by(id=id).one_or_none()
    if obj.user_id == user_id or obj.user_id is None:
        return True
    else:
        return False

# Users


def getUser(id):
    """Return the user with the supplied
    user ID or None if not found."""
    user = session.query(User).filter_by(id=id).one_or_none()
    return user


def getUserByUsername(username):
    """Return the user with the supplied
    username or None if not found."""
    user = session.query(User).filter_by(
        username=username).one_or_none()
    return user


def addUser(username, picture, email, password):
    """Insert a new user into the DB
    and return the created user."""
    user = User(username=username, picture=picture, email=email)
    user.hash_password(password)
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return user


# Categories
def getAllCategories():
    """Return all categories."""
    categories = session.query(Category).all()
    return categories


def getCategoriesByName(query):
    """Return categories having the
    query string in their name."""
    categories = session.query(Category).filter(
        Category.name.contains(query)).order_by(Category.name).all()
    return categories


def getCategory(id):
    """Return the category with the Id
    supplied or None if not found."""
    category = session.query(Category).filter_by(id=id).one_or_none()
    return category


def addCategory(name, picture, description, user_id):
    """Insert new category into DB and
    return the resulting category."""
    category = Category(name=name, picture=picture,
                        description=description, user_id=user_id)
    session.add(category)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return category


def updateCategory(id, name, picture, description):
    """Updating existing category in the DB
     and return the updated category."""
    category = session.query(Category).filter_by(id=id).one_or_none()
    category.name = name
    category.picture = picture
    category.description = description
    session.add(category)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return category


def deleteCategory(id):
    """Delete an existing category from the DB
     and return the deleted category."""
    category = session.query(Category).filter_by(id=id).one_or_none()
    session.delete(category)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return category


# Items
def getAllItems():
    """Return all items."""
    items = session.query(Item).all()
    return items


def getItemsByName(query):
    """Return items having the
    query string in their name."""
    items = session.query(Item).filter(
        Item.name.contains(query)).order_by(Item.name).all()
    return items


def getItem(id):
    """Return the item with the Id
    supplied or None if not found."""
    item = session.query(Item).filter_by(id=id).one_or_none()
    return item


def addItem(name, picture, description, category_id, user_id):
    """Insert new item into DB and
    return the resulting item."""
    item = Item(name=name, picture=picture, description=description,
                category_id=category_id, user_id=user_id)
    session.add(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return item


def updateItem(id, name, picture, description):
    """Updating existing item in the DB
     and return the updated item."""
    item = session.query(Item).filter_by(id=id).one_or_none()
    item.name = name
    item.picture = picture
    item.description = description
    session.add(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return item


def deleteItem(id):
    """Delete an existing item from the DB
     and return the deleted item."""
    item = session.query(Item).filter_by(id=id).one_or_none()
    session.delete(item)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise(e)
    return item


def getCatalog():
    """Return full catalog (categories +
    items) in an easy to traverse
    dictionary tree."""
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
    return catalog
