# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Like(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'likes'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))
    photo_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                 sqlalchemy.ForeignKey("photo.id"))
    user = orm.relation('User')
    photo = orm.relation('Photo')