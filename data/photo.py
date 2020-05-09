# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Photo(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Таблица с фотографиями
    __tablename__ = 'photo'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    img_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("users.id"))
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    user = orm.relation('User')
    avatar = orm.relation('Avatar', back_populates='photo')