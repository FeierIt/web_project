# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from data import db_session


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Таблица с пользователями
    __tablename__ = 'users'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)   
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date)  
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)  
    friends = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    avatar_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                  sqlalchemy.ForeignKey("avatar.id"))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = orm.relation('Photo', back_populates='user')
    avatar = orm.relation('Avatar', back_populates='user')
    like = orm.relation('Like', back_populates='user')
    comment = orm.relation('Comment', back_populates='user')
    avatar = orm.relation('Avatar')
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)  