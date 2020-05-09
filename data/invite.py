# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Invite(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'invite'
        
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    archive = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sender = orm.relation('User', foreign_keys=[sender_id]) 
    receiver = orm.relation('User', foreign_keys=[receiver_id]) 
