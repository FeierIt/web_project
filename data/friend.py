# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Friends(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Таблица с друзьями
    __tablename__ = 'friends'
        
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    friend_id1 = sqlalchemy.Column(sqlalchemy.Integer, 
                                   sqlalchemy.ForeignKey("users.id"))
    friend_id2 = sqlalchemy.Column(sqlalchemy.Integer, 
                                   sqlalchemy.ForeignKey("users.id"))
    friend1 = orm.relation('User', foreign_keys=[friend_id1]) 
    friend2 = orm.relation('User', foreign_keys=[friend_id2]) 
    