#!/usr/bin/env python2
# DB model file

import random
import string
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

Base = declarative_base()
# This randomly generated key changes every time
#  python script starts, it is used in creating
#  auth tokens
secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    """Class to represent user information stored in DB."""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String, index=True)
    password_hash = Column(String(64))
    categories = relationship('Category', backref='user')
    items = relationship('Item', backref='user')

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'username': self.username,
            'picture': self.picture,
            'email': self.email,
        }

    def hash_password(self, password):
        """Hash password to be used after user creation."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify supplied password against saved hash."""
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        """Genrate auth token to be used instead of password."""
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Verify supplied auth token against saved one."""
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id


class Category(Base):
    """Class to represent category information stored in DB."""
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    picture = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'),
                     nullable=False)
    # Delete all child items if parent category is deleted
    items = relationship('Item', backref='category',
                         lazy=True, cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
        }


class Item(Base):
    """Class to represent item information stored in DB."""
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'),
                         nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'),
                     nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
